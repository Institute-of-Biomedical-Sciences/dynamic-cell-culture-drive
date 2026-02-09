import asyncio
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict

import numpy as np
from app.api.handlers.postep256_handler import postep256_handler
from app.asyncio_loop import get_event_loop
from app.database.peristaltic_motor_handler import (
    create_entry,
    create_peristaltic_measurements_batch,
    get_entries,
    get_measurements,
    get_peristaltic_calibration,
    get_peristaltic_calibrations,
    get_peristaltic_scenarios,
    get_tube_configuration,
    get_tube_configurations,
    remove_peristaltic_scenario,
    save_peristaltic_calibration,
    save_peristaltic_scenario,
    save_tube_configuration,
    update_peristaltic_calibration,
    update_peristaltic_scenario,
    update_tube_configuration,
)
from app.models import (
    MotorStatus,
    PeristalticCalibration,
    PeristalticMovement,
    PeristalticScenario,
    TubeConfiguration,
)
from app.websocket_manager import manager
from sklearn.linear_model import LinearRegression

FLOW_RATIO_CONSTANT = 5.34


class PeristalticMotorHandler:
    """Handler for the Peristaltic PoStep motor."""

    def __init__(self):
        """Init function for the handler."""
        self._postep = None
        self._motor_status = MotorStatus.IDLE
        self._is_moving = False
        self._position_deg = 0  # in degrees
        self._max_speed = 1000
        self._max_acceleration = 70000
        self._max_deceleration = 70000
        self._initialized = False
        self._rotate_motor_task: threading.Thread = None
        self._rpm_calibration_stopped = False
        self._rotate_motor_running = False
        self._rotate_motor_paused = False
        self._rotate_motor_start_time = 0
        self._movement_start_time = 0
        self._pause_pressed = False
        self._movement_stopped_time = 0
        self._movement_remaining_time = 0
        self._current_speed = 0
        self._movement_speed = 0
        self._resume_pressed = False
        self._stop_pressed = False
        self._current_direction = "cw"
        self._microstepping = 2
        self._prev_pause_state = False
        self._measurement_queue: Deque[Dict[str, Any]] = deque()
        self._queue_lock = threading.Lock()
        self._current_entry_id: int = None
        self._save_interval = 0.5  # Save queue to DB every 1 second
        self._save_measurements_task: threading.Thread = None
        self._calibration_flow_ratio = None

    def initialize(self):
        """Initialize motor hardware with PoStep256 USB."""
        try:
            # Initialize shared device if not already initialized
            if not postep256_handler.is_initialized():
                postep256_handler.initialize(
                    max_speed=self._max_speed,
                    max_accel=self._max_acceleration,
                    max_decel=self._max_deceleration,
                )

            # Get the shared postep instance
            self._postep = postep256_handler.get_postep()
            self._position_deg = postep256_handler.get_position()

            # Configure motor-specific settings
            #self._postep.set_driver_settings(microstep=2)

            # Update position after settings
            try:
                stream_data = self._postep.read_stream()
                if stream_data and "pos" in stream_data:
                    self._position_deg = stream_data["pos"]
                    postep256_handler.update_position(self._position_deg)
            except Exception as e:
                print(f"Warning: Could not read position: {e}")

            self._initialized = True
        except Exception as e:
            self._motor_status = MotorStatus.ERROR
            self._initialized = False
            raise Exception(f"Error initializing Peristaltic motor: {e}")

    # ---------------------------------------------------------
    # Calibration helpers
    # ---------------------------------------------------------

    def stop_rpm_calibration(self):
        """Stop RPM calibration."""
        self._rpm_calibration_stopped = True
        return True

    def start_rpm_calibration(self, duration: int, rpm: float, direction: str):
        """Start RPM calibration."""
        try:
            self._postep.get_driver_settings()
            self._postep.set_driver_settings(step_mode=2, microstep=4)
            time.sleep(0.1)
            self._rpm_calibration_stopped = False
            self._postep.run_sleep(True)
            self._raise_speed_gradually(int(rpm * FLOW_RATIO_CONSTANT), direction)
            start_time = time.time()
            while time.time() - start_time < duration:
                if self._rpm_calibration_stopped:
                    self._lower_speed_gradually(int(rpm * FLOW_RATIO_CONSTANT), direction, send_measurements=False)
                    break
                time.sleep(0.05)

            self._lower_speed_gradually(int(rpm * FLOW_RATIO_CONSTANT), direction, send_measurements=False)
            self._postep.run_sleep(False)
            return True
        except Exception as e:
            print(f"Error starting RPM calibration: {e}")
            raise e

    def _raise_speed_gradually(self, speed: int, direction: str):
        """Set the speed gradually."""
        for i in range(0, speed, 5):
            if self._rpm_calibration_stopped:
                self._lower_speed_gradually(i, direction, direction, send_measurements=False)
                break
            self._postep.set_requested_speed(i, direction)
            time.sleep(0.02)
        self._postep.set_requested_speed(speed, direction)

    def _lower_speed_gradually(self, speed: int, direction: str, send_measurements: bool = True):
        """Lower the speed gradually."""
        for i in range(speed, 0, -5):
            if send_measurements:
                rpm_current = i / FLOW_RATIO_CONSTANT
                flow_current = rpm_current * self._calibration_flow_ratio  # mL/min
                self._add_to_measurement_queue(
                    entry_id=self._current_entry_id,
                    flow= flow_current,
                    direction=self._current_direction,
                    time=time.time() - self._rotate_motor_start_time,
                )
            self._postep.set_requested_speed(i, direction)
            self._current_speed = i
            time.sleep(0.02)
        self._postep.set_requested_speed(0, direction)
        self._current_speed = 0

    def _compute_slope(
        self,
        duration: int,
        low_rpm: int,
        high_rpm: int,
        low_rpm_volume: float,
        high_rpm_volume: float,
    ) -> float:
        """Compute slope (flow rate per RPM) using linear regression. Duration in seconds."""
        duration_m = duration / 60.0
        X = np.array([0, low_rpm, high_rpm]).reshape((-1, 1))
        y = np.array([0, low_rpm_volume, high_rpm_volume]) / duration_m
        model = LinearRegression(fit_intercept=False).fit(X, y)
        return float(model.coef_[0] * duration_m)  # Convert to ml/min

    def save_calibration(
        self,
        duration: int,
        low_rpm: int,
        high_rpm: int,
        low_rpm_volume: float,
        high_rpm_volume: float,
        name: str,
        diameter: float,
    ):
        """Save calibration data."""
        # New slope calculation using linear regression
        duration_m = duration / 60.0
        X = np.array([0, low_rpm, high_rpm]).reshape((-1, 1))
        y = np.array([0, low_rpm_volume, high_rpm_volume]) / duration_m
        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)

        # Perform linear regression
        model = LinearRegression().fit(X, y)

        # The slope (coefficient) of the linear regression model
        slope = model.coef_[0] * duration_m  # Convert to ml/min

        save_peristaltic_calibration(
            duration=duration,
            low_rpm=low_rpm,
            high_rpm=high_rpm,
            low_rpm_volume=low_rpm_volume,
            high_rpm_volume=high_rpm_volume,
            slope=slope,
            name=name,
            diameter=diameter,
        )
        return slope
    
    def get_flow_from_rpm(self, rpm: int, slope: float) -> float:
        """Get flow from RPM."""
        return rpm * slope
    
    def get_rpm_from_flow(self, flow: float, slope: float) -> int:
        """Get RPM from flow."""
        return flow / slope

    # ---------------------------------------------------------
    # Internal helpers: WebSocket + speed control + threading
    # ---------------------------------------------------------

    def _send_peristaltic_stopped_websocket(self):
        """Send a peristaltic stopped update to the WebSocket."""
        try:
            self._submit_async(manager.send_peristaltic_stopped())
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")

    def _submit_async(self, coro):
        try:
            loop = get_event_loop()
            asyncio.run_coroutine_threadsafe(coro, loop)
        except Exception as e:
            print(f"Async submission error: {e}")

    def _set_requested_speed(self, speed, direction, prev_direction):
        """Set the requested speed for the motor."""
        if speed < self._current_speed and prev_direction == direction:
            for i in range(int(self._movement_speed), int(speed), -5):
                rpm_current = i / FLOW_RATIO_CONSTANT
                flow_current = rpm_current * self._calibration_flow_ratio  # mL/min
                self._add_to_measurement_queue(
                    entry_id=self._current_entry_id,
                    flow= flow_current,
                    direction=direction,
                    time=time.time() - self._rotate_motor_start_time,
                )
                if self._stop_pressed or self._pause_pressed:
                    self._lower_speed_gradually(i, direction)
                    self._postep.run_sleep(False)
                    break
                self._postep.set_requested_speed(i, direction)
                self._current_speed = i
                time.sleep(0.02)
        elif (
            speed > self._current_speed
            and self._current_speed > 0
            and prev_direction == direction
        ):
            for i in range(int(self._movement_speed), int(speed), 5):
                rpm_current = i / FLOW_RATIO_CONSTANT
                flow_current = rpm_current * self._calibration_flow_ratio  # mL/min
                self._add_to_measurement_queue(
                    entry_id=self._current_entry_id,
                    flow= flow_current,
                    direction=direction,
                    time=time.time() - self._rotate_motor_start_time,
                )
                if self._stop_pressed or self._pause_pressed:
                    self._lower_speed_gradually(i, direction)
                    self._postep.run_sleep(False)
                    break
                self._postep.set_requested_speed(i, direction)
                self._current_speed = i
                time.sleep(0.02)
        else:
            if self._current_speed > 0:
                self._lower_speed_gradually(self._current_speed, prev_direction)
            for i in range(0, int(speed), 5):
                current_rpm = i / FLOW_RATIO_CONSTANT
                current_flow = current_rpm * self._calibration_flow_ratio  # mL/min
                self._add_to_measurement_queue(
                    entry_id=self._current_entry_id,
                    flow= current_flow,
                    direction=direction,
                    time=time.time() - self._rotate_motor_start_time,
                )
                if self._stop_pressed or self._pause_pressed:
                    self._lower_speed_gradually(i, direction)
                    self._postep.run_sleep(False)
                    break
                self._postep.set_requested_speed(i, direction)
                self._current_speed = i
                time.sleep(0.02)

    def _rotate_motor_thread(
        self,
        movements: list[PeristalticMovement],
    ):
        try:
            self._rotate_motor_start_time = time.time()
            movement_index = 0
            for movement in movements:
                self.send_peristaltic_movement_websocket(movement_index)
                movement_index += 1
                
                self._movement_speed = int(movement.flow * FLOW_RATIO_CONSTANT)
                self._movement_start_time = time.time()
                self._movement_remaining_time = 0

                self._set_requested_speed(
                    self._movement_speed,
                    movement.direction,
                    self._current_direction,
                )
                self._current_direction = movement.direction


                while (
                    time.time() - self._movement_start_time < movement.duration
                    or movement.duration == 0
                ):
                    if self._stop_pressed:
                        break
                    if self._pause_pressed or self._rotate_motor_paused:
                        self._lower_speed_gradually(self._current_speed, self._current_direction)
                        print("JE OD TU?")
                        self._postep.run_sleep(False)
                        while self._rotate_motor_paused:
                            if self._stop_pressed:
                                break
                            time.sleep(0.2)
                            self._add_to_measurement_queue(
                                entry_id=self._current_entry_id,
                                flow=0,
                                direction=self._current_direction,
                                time=time.time() - self._rotate_motor_start_time,
                            )

                        if self._resume_pressed:
                            self._postep.run_sleep(True)
                            time.sleep(0.05)
                            self._set_requested_speed(
                                self._movement_speed,
                                self._current_direction,
                                self._current_direction,
                            )
                            if movement.duration > 0:
                                movement.duration = (
                                    movement.duration - self._movement_remaining_time
                                )
                            self._resume_pressed = False
                            self._pause_pressed = False
                            print("se to sploh izvede")
                            self._rotate_motor_paused = False
                            self._movement_start_time = time.time()
                            continue

                    stream_data = self._postep.read_stream()
                    if stream_data and "pos" in stream_data:
                        self._position_deg = stream_data["pos"]
                        if self._current_entry_id is not None and self._current_speed > 0:
                            rpm_current = self._movement_speed / FLOW_RATIO_CONSTANT
                            flow_current = rpm_current * self._calibration_flow_ratio  # mL/min
                            self._add_to_measurement_queue(
                                entry_id=self._current_entry_id,
                                flow= flow_current,
                                direction=self._current_direction,
                                time=time.time() - self._rotate_motor_start_time,
                            )
                            
            self._lower_speed_gradually(self._current_speed, self._current_direction)
            self._postep.move_to_stop()
            self._postep.run_sleep(False)
            time.sleep(0.05)
            self._send_peristaltic_stopped_websocket()
            self._rotate_motor_running = False
            self._stop_pressed = False
            self._pause_pressed = False
            self._rotate_motor_paused = False
            self._resume_pressed = False
            self._is_moving = False
            self._motor_status = MotorStatus.IDLE
            self._rotate_motor_start_time = 0
            self.stop_motor()
        except Exception as e:
            print(f"Error in peristaltic_motor thread: {e}")
            raise e

    def _add_to_measurement_queue(
        self, entry_id: int, flow: float, direction: str, time: datetime
    ):
        """Add a measurement to the queue."""
        with self._queue_lock:
            self._measurement_queue.append(
                {
                    "entry_id": entry_id,
                    "flow": flow,
                    "direction": direction,
                    "time": time,
                }
            )

    def _save_measurements_batch(self):
        """Save queued measurements to database in batch and return the batch."""
        measurements_to_save: list[Dict[str, Any]] = []
        with self._queue_lock:
            if self._measurement_queue:
                measurements_to_save = list(self._measurement_queue)
                self._measurement_queue.clear()

        if not measurements_to_save:
            return []

        try:
            create_peristaltic_measurements_batch(measurements_to_save)
        except Exception as e:
            print(f"Error saving measurements batch: {e}")
            # Re-add measurements to queue on error
            with self._queue_lock:
                self._measurement_queue.extendleft(reversed(measurements_to_save))
            # On error we consider nothing was successfully sent
            return []

        return measurements_to_save

    def _handle_measurements_thread(self, entry_id: int):
        """Thread that periodically saves queued measurements to database."""
        self._current_entry_id = entry_id
        while self._is_moving:
            batch = self._save_measurements_batch()
            if batch:
                self.send_measurements_websocket(batch)
            time.sleep(self._save_interval)

        # Save any remaining measurements when stopping
        final_batch = self._save_measurements_batch()
        if final_batch:
            self.send_measurements_websocket(final_batch)

        self._current_entry_id = None

    def send_peristaltic_movement_websocket(self, movement: int):
        """Send a rotate movement update to the WebSocket."""
        try:
            self._submit_async(manager.send_peristaltic_movement(movement))
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")

    def send_measurements_websocket(self, measurements: list[Dict[str, Any]]):
        """Send measurements to the WebSocket."""
        try:
            self._submit_async(manager.send_peristaltic_measurements(measurements))
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")

    # ---------------------------------------------------------
    # Public motor control (rotate)
    # ---------------------------------------------------------

    def rotate_motor(
        self,
        entry_name: str,
        scenario_id: int,
        scenario_name: str,
        calibration_name: str,
        calibration_preset: bool,
        movements: list[PeristalticMovement],
    ) -> bool:
        """Rotate the peristaltic motor based on movements."""
        if self._is_moving:
            return False
        entry_id = create_entry(
            name=entry_name,
            peristaltic_scenario_id=scenario_id,
            scenario_name=scenario_name,
        )
        self._current_entry_id = entry_id
        self._postep.run_sleep(True)
        self._rotate_motor_running = True
        self._postep.get_driver_settings()
        self._postep.set_driver_settings(step_mode=2, microstep=4)
        time.sleep(0.1)
        self._is_moving = True
        self._motor_status = MotorStatus.MOVING
        if calibration_preset:
            tube_configuration = self.get_tube_configuration(calibration_name)
            self._calibration_flow_ratio = tube_configuration.flow_rate
            for movement in movements:
                movement.flow = self.get_rpm_from_flow(movement.flow, tube_configuration.flow_rate)
        else:
            calibration = self.get_peristaltic_calibration(calibration_name)
            self._calibration_flow_ratio = calibration.slope
            for movement in movements:
                movement.flow = self.get_rpm_from_flow(movement.flow, calibration.slope)
        self._rotate_motor_task = threading.Thread(
            target=self._rotate_motor_thread,
            args=(movements,),
            daemon=True,
        )
        self._stop_pressed = False

        self._rotate_motor_task.start()
        self._save_measurements_task = threading.Thread(
            target=self._handle_measurements_thread,
            args=(entry_id,),
            daemon=True,
        )
        self._save_measurements_task.start()
        return True

    def stop_peristaltic_motor(self):
        """Manually stop the peristaltic motor motion."""
        if (
            self._rotate_motor_running
            and self._rotate_motor_task
            and self._rotate_motor_task.is_alive()
        ):
            self._stop_pressed = True
            self._rotate_motor_task.join(timeout=3)
            self._is_moving = False
            self._motor_status = MotorStatus.IDLE
            self._rotate_motor_task = None
            if self._save_measurements_task:
                self._save_measurements_task.join(timeout=3)
                self._measurement_queue.clear()
                self._save_measurements_task = None

    def pause_peristaltic_motor(self):
        """Pause the peristaltic motor motion temporarily."""
        if (
            self._rotate_motor_running
            and self._rotate_motor_task
            and self._rotate_motor_task.is_alive()
            and not self._rotate_motor_paused
        ):
            self._movement_remaining_time = time.time() - self._movement_start_time
            self._rotate_motor_paused = True
            self._pause_pressed = True
            self._movement_stopped_time = time.time()
            self._resume_pressed = False

    def resume_peristaltic_motor(self, movement: int):
        """Resume the peristaltic motor motion from where it was paused."""
        if (
            self._rotate_motor_running
            and self._rotate_motor_task
            and self._rotate_motor_task.is_alive()
            and self._rotate_motor_paused
        ):
            self._pause_pressed = False
            self._postep.run_sleep(True)
            self._resume_pressed = True
            self._pause_pressed = False
            self._rotate_motor_paused = False

    # ---------------------------------------------------------
    # Movement state helpers + status
    # ---------------------------------------------------------

    def stop_motor(self) -> bool:
        """Stop motor movement using PoStep256 USB."""
        if not self._is_moving:
            return True

        if self._postep.device is None:
            return False

        try:
            self._postep.move_to_stop()
            self._postep.run_sleep(False)
        except Exception as e:
            print(f"Error stopping peristaltic motor: {e}")
            return False

        self._is_moving = False
        self._motor_status = MotorStatus.IDLE

        return True

    def get_status(self) -> dict:
        """Get current motor status."""
        return {
            "status": self._motor_status.value,
            "position": self._position_deg,
            "is_moving": self._is_moving,
            "initialized": self._initialized,
        }

    # ---------------------------------------------------------
    # DB / model wrappers (entries, calibration, scenarios, tubes)
    # ---------------------------------------------------------

    def get_entries(self) -> list[Dict[str, Any]]:
        """Get all measurement entries."""
        try:
            entries = get_entries()
            return entries
        except Exception as e:
            print(f"Error getting entries: {e}")
            raise e

    def update_peristaltic_calibration(
        self, calibration: PeristalticCalibration
    ) -> bool:
        """Update a peristaltic calibration."""
        return update_peristaltic_calibration(calibration)

    def get_peristaltic_calibration(self, name: str) -> PeristalticCalibration:
        """Get a peristaltic calibration by name."""
        return get_peristaltic_calibration(name)

    def get_peristaltic_calibrations(self) -> list[PeristalticCalibration]:
        """Get all peristaltic calibrations."""
        return get_peristaltic_calibrations()

    def update_peristaltic_scenario(
        self, scenario_id: int, scenario: PeristalticScenario
    ) -> bool:
        """Update a peristaltic scenario."""
        return update_peristaltic_scenario(scenario_id=scenario_id, scenario=scenario)

    def remove_peristaltic_scenario(self, scenario_id: str) -> bool:
        """Remove a peristaltic scenario."""
        return remove_peristaltic_scenario(scenario_id=scenario_id)

    def save_peristaltic_scenario(self, scenario: PeristalticScenario) -> int:
        """Save a peristaltic scenario."""
        return save_peristaltic_scenario(scenario)

    def get_peristaltic_scenarios(self) -> list[PeristalticScenario]:
        """Get list of peristaltic scenarios."""
        return get_peristaltic_scenarios()

    def get_tube_configuration(self, name: str) -> TubeConfiguration:
        """Get a tube configuration by name."""
        try:
            return get_tube_configuration(name)
        except Exception as e:
            print(f"Error getting tube configuration: {e}")
            raise e

    def get_tube_configurations(self) -> list[TubeConfiguration]:
        """Get list of tube configurations."""
        try:
            return get_tube_configurations()
        except Exception as e:
            print(f"Error getting tube configurations: {e}")
            raise e

    def update_tube_configuration(self, tube_configuration: TubeConfiguration) -> bool:
        """Update a tube configuration."""
        return update_tube_configuration(tube_configuration)

    def save_tube_configuration(self, tube_configuration: TubeConfiguration) -> bool:
        """Save a tube configuration."""
        return save_tube_configuration(tube_configuration)

    def get_measurements(self, entry_id: int, limit: int = 100) -> list[Dict[str, Any]]:
        """Get peristaltic measurements for an entry."""
        return get_measurements(entry_id, limit)

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    def cleanup(self):
        """Cleanup resources."""
        if self._is_moving:
            self.stop_motor()
        if self._postep:
            try:
                # self.move_to_deg(0)
                self.stop_motor()
                self._postep.set_run(False)
            except Exception as e:
                print(f"Error cleaning up peristaltic motor: {e}")
        print("Peristaltic motor cleanup completed")


peristaltic_motor_handler = PeristalticMotorHandler()
