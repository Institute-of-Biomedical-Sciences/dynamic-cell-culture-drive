# ruff: noqa: D107

import logging
import os
import platform
import struct
import time

import usb.backend.libusb1
import usb.core
import usb.util

os.environ["PYUSB_DEBUG"] = "debug"  # for extra debugging of USB

VENDOR_ID = 0x1DC3
PRODUCT_ID = 0x0641
OUT_ENDPOINT = 0x01
IN_ENDPOINT = 0x81


class PoStep256USB(object):
    """PoStep256USB class."""

    def __init__(self, log_level=logging.INFO, serial_number=None):
        self.was_kernel_driver_active = False
        self.device = None
        self.is_moving = False

        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
            level=log_level,
        )

        logging.info(
            "Detected platform {} with arch {}".format(
                platform.system(), platform.architecture()[0]
            )
        )

        if serial_number is None:
            # Select the first device on the list
            logging.info(
                "Serial number is not specified. Selecting first discovered device."
            )
            self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        else:
            # Select the device with the given serial number
            logging.info(f"Selected device serial number: {serial_number}.")
            self.device = usb.core.find(
                idVendor=VENDOR_ID,
                idProduct=PRODUCT_ID,  # serial_number=serial_number
            )
        # if the OS kernel already claimed the device
        if self.device is not None and platform.system() != "Windows":
            if self.device.is_kernel_driver_active(0):
                # tell the kernel to detach
                self.device.detach_kernel_driver(0)
                self.was_kernel_driver_active = True

        if self.device is None:
            logging.error("Driver not found, make sure it is attached.")
            return

        self.device.reset()

        # Set the active configuration. With no arguments, the first configuration will be the active one
        self.device.set_configuration()

        # Claim interface 0
        usb.util.claim_interface(self.device, 0)

        self.configuration = self.read_configuration()

        # initialize motor parameter
        self.max_speed = 50000
        self.max_accel = 40000
        self.max_decel = 3000
        self.endsw = None

    @staticmethod
    def discover_devices():
        """Discover PoStep256USB devices."""
        device_list = []
        if platform.system() == "Windows":
            # required for Windows only
            # libusb DLLs from: https://sourcefore.net/projects/libusb/

            arch = platform.architecture()
            if arch[0] == "32bit":
                backend = usb.backend.libusb1.get_backend(
                    find_library=lambda x: "C:\\Windows\\System\\libusb\\x86\\libusb-1.0.dll"
                )  # 32-bit DLL, select the appropriate one based on your Python installation

            elif arch[0] == "64bit":
                backend = usb.backend.libusb1.get_backend(
                    find_library=lambda x: "C:\\Windows\\System\\libusb\\x64\\libusb-1.0.dll"
                )  # 64-bit DLL

            devices = usb.core.find(
                find_all=True, backend=backend, idVendor=VENDOR_ID, idProduct=PRODUCT_ID
            )

            for d in devices:
                try:
                    d.set_configuration()
                    serial = usb.util.get_string(d, d.iProduct)
                    device_list.append(serial)
                except usb.core.USBError as e:
                    if e.errno == 32:
                        time.sleep(0.2)
                continue  # skip devices that fail
        else:
            # custom_match=lambda d: d.idProduct=PRODUCT_ID and d.idvendor=VENDOR_ID
            devices = usb.core.find(
                find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID
            )
            for d in devices:
                for attempt in range(3):
                    try:
                        if d.is_kernel_driver_active(0):
                            d.detach_kernel_driver(0)
                        d.set_configuration()
                        serial = usb.util.get_string(d, d.iSerialNumber)
                        device_list.append(serial)
                        break
                    except usb.core.USBError as e:
                        if e.errno == 32:
                            time.sleep(0.2)
                    continue  # skip devices that fail
        return device_list

    def __del__(self):
        """Destructor for PoStep256USB class."""
        if self.device is not None:
            usb.util.release_interface(self.device, 0)

        # This applies to Linux only - reattach the kernel driver if we previously detached it
        if self.was_kernel_driver_active:
            self.device.attach_kernel_driver(0)
            logging.info("Kernel driver reattached.")

    def get_device_info(self):
        """Get device information."""
        data_list = [0] * 64

        data_list[0] = 0x00
        data_list[1] = 0x01
        data_list[63] = 0x00

        self.write_to_postep(data_list)
        # request data with 500ms tuimeout
        received = self.read_from_postep(500)

        received = list(received)

        bl_fw_version = (received[1] << 8) | received[2]
        print(f"Bootloader fw version: {bl_fw_version}")

        app_fw_version = (received[3] << 8) | received[4]
        print(f"App fw version: {app_fw_version}")

        supply_voltage = (received[8] * 256 + received[9]) * 0.072
        print(f"Supply voltage: {supply_voltage}")

        temperature = (received[44] * 256 + received[45]) * 0.125
        print(f"Device temperature: {temperature}")

        status = received[
            46
        ]  # 0x01 - sleep, 0x02 - active, 0x03 - idle, 0x04 - overheated, 0x05 - pwm mode
        print(f"Device status: {status}")
        # check if response is valid
        # if(received[0]!=0x02):
        #     logging.error("Bad response: {}".format(received[0]))
        #     return False
        # return True

    def enable_rt_stream(self):
        """Enable real-time data streaming."""
        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0xA0
        # write to driver
        logging.info("postep_enable_rt_stream")
        self.write_to_postep(data_list)
        # request data with 500ms tuimeout
        received = self.read_from_postep(500)
        # check if response is valid
        if received[0] != 0x02:
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def read_stream(self):
        """Read real-time data stream."""
        received = self.read_from_postep(200)
        # parse data
        status = {}
        status["pos"], status["speed"], status["final"] = struct.unpack(
            ">iii", received[20:32]
        )

        status["endswitch"] = bool((received[6] >> 6) & 0x01)
        logging.debug("Status: {}".format(status))
        return status

    def run_sleep(self, run):
        """Run or sleep the motor.

        Args:
            run (bool): True to run, False to sleep
        """
        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0xA1
        if run is True:
            data_list[20] = 0x01
        # write to driver
        logging.info("postep_run_sleep {}".format(run))
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if received is None:
            return False
            logging.error("No response.")
        if received[0] != 0x02:
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def set_requested_speed(self, speed, direction="cw"):
        """Set the requested speed for the motor.

        :param self: Description
        :param speed: Description
        """
        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0x90
        # 480000 kHz/step_value = speed
        if speed != 0:
            step_values = 480000 / speed
        else:
            step_values = 480000
        data_list[20:24] = struct.pack("<I", int(step_values))
        if direction == "ccw":
            data_list[24] = 0x01
        # write to driver
        logging.info("postep_move_speed {}".format(speed))
        self.write_to_postep(data_list)
        # write again - TODO this is an unknown bug
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if received[15] != 0x90:
            logging.error("Bad response: {}".format(received[15]))
            return False
        return True

    def set_run(self, run):
        """Set the motor to run or sleep mode.

        Args:
            run (bool): True to run, False to sleep
        """
        data_list = [0] * 64
        data_list[1] = 0xA1
        data_list[20] = 0x01 if run else 0x00

        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        print(list(received))
        print(f"Byte at 15: {received[15]}")

    def read_configuration(self):
        """Read the configuration of the motor driver."""
        data_list = [0] * 64
        data_list[1] = 0x88

        self.write_to_postep(data_list)
        received = self.read_from_postep(500)
        print(list(received))

        received = list(received)

        velocity_max = int.from_bytes(received[24:28], byteorder="little")
        print(f"raw bytes velocity: {received[24:28]}")
        print(f"Velocity max: {velocity_max}")

        acceleration = int.from_bytes(received[28:32], byteorder="little")
        print(f"Raw bytes acceleration: {received[28:32]}")
        print(f"Acceleration: {acceleration}")

        deceleration = int.from_bytes(received[32:36], byteorder="little")
        print(f"Raw bytes deceleration: {received[32:36]}")
        print(f"Deceleration: {deceleration}")

        settings_byte = received[36]
        print(f"Settings byte: {settings_byte}")

        self.current_settings = received  # store settings as a list

    def write_driver_settings(self, settings_list):
        """Write driver settings to the motor driver."""
        data_list = [0] * 64
        data_list[1] = 0x80
        data_list[20:36] = settings_list[40:56]
        data_list[37] = settings_list[62]
        data_list[38:44] = settings_list[56:62]
        data_list[44] = settings_list[63]

        print(f"Writing data list: {data_list}")
        self.write_to_postep(data_list)
        self.write_to_postep(data_list)
        time.sleep(1)
        received = self.read_from_postep(500)
        print(list(received))

    def read_driver_settings(self):
        """Read driver settings from the motor driver."""
        data_list = [0] * 64
        data_list[1] = 0x81

        self.write_to_postep(data_list)
        received = self.read_from_postep(500)
        print("Raw read list: ", list(received))

        received = list(received)

        return received

    def change_configuration(
        self, velocity=10000, acceleration=2000, deceleration=2000, settings=0
    ):
        """Change the configuration of the motor driver.

        Args:
            velocity (int): Velocity in steps per second
            acceleration (int): Acceleration in steps per second squared
            deceleration (int): Deceleration in steps per second squared
            settings (int): Settings byte
        """
        data_list = [0] * 64
        data_list[1] = 0x87

        # set velocity
        data_list[24:28] = list(velocity.to_bytes(4, "little"))

        # set acceleration
        data_list[28:32] = list(acceleration.to_bytes(4, "little"))

        # set deceleration
        data_list[32:36] = list(deceleration.to_bytes(4, "little"))

        # set settings
        data_list[36] = settings

        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        print(list(received))
        print(f"Byte at 15: {received[15]}")

    def set_pwm(
        self,
        duty1_ccw,
        duty2_ccw,
        duty1_acw,
        duty2_acw,
    ):
        """Set the PWM values for the motor driver.

        Args:
            duty1_ccw (int): Duty cycle for counter-clockwise rotation
            duty2_ccw (int): Duty cycle for counter-clockwise rotation
            duty1_acw (int): Duty cycle for clockwise rotation
            duty2_acw (int): Duty cycle for clockwise rotation
        """
        data_list = [0] * 64
        data_list[1] = 0xB0
        data_list[20] = 0
        data_list[21] = 0
        data_list[22] = 0
        data_list[23] = 24

        data_list[45] = duty1_ccw
        data_list[46] = duty1_acw
        data_list[47] = duty2_ccw
        data_list[48] = duty2_acw

        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        print(list(received))
        print(f"Byte at 15: {received[15]}")

    def move_config(self, max_speed, max_accel, max_decel, endsw=None):
        """Configure motion parameters.

        Args:
            max_speed (int): Maximal speed
            max_accel (int): Maximal acceleration
            max_decel (int): Maximal deceleration
            endsw (str): End switch configuration, either "nc" or "no"
        """
        self.max_speed = max_speed
        self.max_accel = max_accel
        self.max_decel = max_decel
        self.endws = endsw

    def get_move_config(self):
        """Get current motion configuration."""
        return {
            "max_speed": self.max_speed,
            "max_accel": self.max_accel,
            "max_decel": self.max_decel,
            "endsw": self.endsw,
        }

    def move_to(self, position):
        """Move to the specified position.

        Args:
            position (int): Target position in steps
        """
        self.move_trajectory(
            position, self.max_speed, self.max_accel, self.max_decel, self.endsw
        )

    def move_trajectory(
        self, final_position, max_speed, max_accel=30000, max_decel=3000, endsw=None
    ):
        """Move with drivers position tracking system by specifying the desired position.

        Args:
            final_position (int): Target position in steps
            max_speed (int): Maximal speed
            max_accel (int): Maximal acceleration
            max_decel (int): Maximal deceleration
            endsw (str): End switch configuration, either "nc" or "no"
        """
        data_list = [0] * 64
        data_list[1] = 0xB1
        # do not enable autorun
        data_list[2] = 0b00000000
        # Set trajectory final position
        data_list[20:24] = struct.pack("<i", final_position)
        # Set trajectory max speed
        data_list[24:28] = struct.pack("<I", max_speed)
        # Set traject. max acceleration
        data_list[28:32] = struct.pack("<I", max_accel)
        # Set traject. max deceleration
        data_list[32:36] = struct.pack("<I", max_decel)
        # Set InvDir<<2|NCSw<<1| SwEn
        if endsw is not None:
            data_list[36] = data_list[36] | 0b00000001
            if endsw == "nc":
                data_list[36] = data_list[36] | 0b00000010
        # write to driver
        error = False
        for x in range(3):
            error = True
            try:
                logging.info(
                    "postep_move_trajectory to {} speed {} accel {} decel {} endsw {}".format(
                        final_position, max_speed, max_accel, max_decel, endsw
                    )
                )
                self.write_to_postep(data_list)
                # request data
                received = self.read_from_postep(500)
                # check if response is valid
                if received[15] != 0xB1:
                    logging.error("Bad response: {}".format(received[15]))

                else:
                    error = False
                    break
            except Exception:
                logging.error("Bad response")
        return error

    def move_to_stop(self):
        """Stop the motor."""
        # stop trajectory
        data_list = [0] * 64
        data_list[1] = 0xB2

        # write to driver
        self.write_to_postep(data_list)
        # request data
        logging.info("move_to_stop")
        received = self.read_from_postep(500)
        # check if response is valid
        if received[0] != 0x02:
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def move_reset_to_zero(self):
        """Reset the motor position to zero."""
        # zero trajectory
        data_list = [0] * 64
        data_list[1] = 0xB3

        # write to driver
        logging.info("move_reset_to_zero")
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if received[0] != 0x02:
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def system_reset(self):
        """Reset the motor driver."""
        # note driver will disconnect from USB
        data_list = [0] * 64
        data_list[1] = 0x02

        # write to driver
        logging.info("postep_system_reset")
        self.write_to_postep(data_list)

    def write_to_postep(self, data_list):
        """Write data to the motor driver.

        Args:
            data_list (list): List of data to write
        """
        # data_list = [0] * 64
        # for run/sleep send data[1] = 0xA1
        # data_list[0] = 0x01
        # data_list[1] = 0x90

        data = bytearray(data_list)
        logging.debug("Writing command: {}".format(bytes(data).hex()))

        num_bytes_written = 0
        try:
            num_bytes_written = self.device.write(OUT_ENDPOINT, data, 500)
        except usb.core.USBError as e:
            print(e.args)

        return num_bytes_written

    def read_from_postep(self, timeout):
        """Read data from the motor driver.

        Args:
            timeout (int): Timeout in milliseconds
        Returns:
            data (bytes): Data received from the driver
        """
        data = None
        for x in range(3):
            try:
                data = self.device.read(IN_ENDPOINT, 64, timeout)
            except usb.core.USBError as e:
                print("Error reading response: {}".format(e.args))
                continue
            logging.debug("Receive command: {}".format(bytes(data).hex()))
            if len(data) == 0:
                logging.error("No data received")
                data = None
                continue
            else:
                break

        return data

    def map_gain(self, gain):
        """Return map gain."""
        if gain == 0:
            return 5
        if gain == 1:
            return 10
        if gain == 2:
            return 20
        if gain == 3:
            return 40

    def fullscale_current_to_torque(self, fsc, is_gain):
        """Convert fullscale current to torque value."""
        torque = min(int((256 * self.map_gain(is_gain) * 0.033 * fsc) / 2.75), 255)
        return torque

    def current_to_reg_val(self, curr):
        """Convert current to register value."""
        reg_0 = int(curr * 123)
        reg_1 = 3
        while reg_0 > 255:
            reg_1 -= 1
            reg_0 = reg_0 >> 1
        return reg_0, reg_1

    def reg_val_to_current(self, reg_0, reg_1):
        """Convert register value to current."""
        while reg_1 < 3:
            reg_0 = reg_0 << 1
            reg_1 += 1
        current = reg_0 / 123
        print(f"Reg 0: {reg_0}, reg 1: {reg_1}")
        return current

    def get_driver_settings(self):
        """Get the PoStep driver settings."""
        for _ in range(0, 3):
            received = self.read_driver_settings()
            if received[15] == 0x81:
                break

        settings = {}

        ctrl_reg = received[40:42]
        print(f"Control register:{ctrl_reg}")

        microstepping = (ctrl_reg[0] & 0x78) >> 3  # this is good
        print(f"Microstep setting: {microstepping}")
        settings["microstepping"] = microstepping

        is_gain = ctrl_reg[1] & 0x03
        print(f"Read is_gain: {is_gain}")
        settings["isgain"] = is_gain
        self.is_gain = is_gain

        torque = received[42:44]  # actually torque setting - convert to fs current
        print(f"Read torque: {torque[0]}")
        settings["torque"] = torque[0]

        fsc = (2.75 * torque[0]) / (256 * self.map_gain(is_gain) * 0.033)
        print(f"Calculated full scale current: {fsc}")
        settings["fullscale_current"] = round(fsc, 1)

        idle_current_reg = received[57:59]
        print(f"Read idle current: {idle_current_reg}")

        idle_current = self.reg_val_to_current(idle_current_reg[0], idle_current_reg[1])
        print(f"Calculated current: {idle_current}")
        settings["idle_current"] = round(idle_current, 1)

        overheat_current_reg = received[59:61]
        print(f"overheat current: {overheat_current_reg}")  # works

        overheat_current = self.reg_val_to_current(
            overheat_current_reg[0], overheat_current_reg[1]
        )
        print(f"Calculated current: {overheat_current}")  # works
        settings["overheat_current"] = round(overheat_current, 1)

        self.current_settings = received
        
        print("Current settings: ", self.current_settings)
        return settings

    def set_driver_settings(
        self, microstep=None, fsc=None, idlec=None, overheatc=None, step_mode=4
    ):
        """Set PoStep driver settings."""
        if microstep is not None:
            current_ctrl_reg = self.current_settings[40]
            current_ctrl_reg &= 0x87
            new_ctrl_reg = current_ctrl_reg | (int(microstep) << 3)
            self.current_settings[40] = new_ctrl_reg
        if fsc is not None:
            torque = self.fullscale_current_to_torque(float(fsc), self.is_gain)
            self.current_settings[42] = torque
        if idlec is not None:
            idle_current_0, idle_current_1 = self.current_to_reg_val(float(idlec))
            self.current_settings[57] = idle_current_0
            self.current_settings[58] = idle_current_1
        if overheatc is not None:
            overheat_current_0, overheat_current_1 = self.current_to_reg_val(
                float(overheatc)
            )
            self.current_settings[59] = overheat_current_0
            self.current_settings[60] = overheat_current_1
        if step_mode is not None:
            # current_ctrl_reg = self.current_settings[40]
            # current_ctrl_reg &= 0x87
            # new_ctrl_reg = current_ctrl_reg | (int(step_mode) << 3)
            self.current_settings[37] = step_mode
            # self.current_settings[40] = new_ctrl_reg

        print("Current settings: ", self.current_settings)
        print("SET ESETTINGS")
        self.write_driver_settings(self.current_settings)
