import threading

from app.api.postep256_usb_lib.postep256usb import PoStep256USB


class Postep256Handler:
    """Singleton handler for shared PoStep256 USB device."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Postep256Handler, cls).__new__(cls)
                    cls._instance._initialized = False
                    cls._instance._postep = None
                    cls._instance._position_deg = 0
        return cls._instance

    def initialize(
        self,
        max_speed: int = 40000,
        max_accel: int = 40000,
        max_decel: int = 40000,
        log_level: str = "INFO",
        device_index: int = 0,
    ) -> None:
        """Initialize the shared PoStep256 USB device (only once).

        Args:
            max_speed: Maximum speed setting
            max_accel: Maximum acceleration setting
            max_decel: Maximum deceleration setting
            log_level: Logging level for PoStep256USB
            device_index: Index of device to use if multiple devices found

        Raises:
            Exception: If initialization fails
        """
        if self._initialized:
            print("PoStep256 device already initialized.")
            return

        with self._lock:
            if self._initialized:
                return

            try:
                print("Initializing shared PoStep256 USB device...")

                serial_number = PoStep256USB.discover_devices()
                print("devices", serial_number)
                if len(serial_number) == 0:
                    raise Exception("No PoStep256 Motor USB device found.")

                if device_index >= len(serial_number):
                    raise Exception(
                        f"Device index {device_index} not available. Found {len(serial_number)} device(s)."
                    )

                self._postep = PoStep256USB(
                    serial_number=serial_number[device_index], log_level=log_level
                )

                if self._postep.device is None:
                    raise Exception("No PoStep256 Motor USB device found.")

                if self._postep.enable_rt_stream():
                    print("PoStep256 motor real-time streaming enabled.")


                self._postep.get_driver_settings()

                # self._postep.move_config(
                #     max_speed=max_speed,
                #     max_accel=max_accel,
                #     max_decel=max_decel,
                #     endsw=None,
                # )

                # Read initial position
                try:
                    stream_data = self._postep.read_stream()
                    if stream_data and "pos" in stream_data:
                        self._position_deg = stream_data["pos"]
                except Exception as e:
                    print(f"Warning: Could not read initial position: {e}")
                    self._position_deg = 0

                self._initialized = True
                print("PoStep256 device initialization successful.")

            except Exception as e:
                self._initialized = False
                raise Exception(f"Error initializing PoStep256 device: {e}")

    def get_postep(self) -> PoStep256USB:
        """Get the shared PoStep256 instance."""
        if not self._initialized:
            raise Exception(
                "PoStep256 device not initialized. Call initialize() first."
            )
        return self._postep

    def get_position(self) -> int:
        """Get current position."""
        return self._position_deg

    def update_position(self, position: int) -> None:
        """Update the stored position."""
        self._position_deg = position

    def is_initialized(self) -> bool:
        """Check if device is initialized."""
        return self._initialized

    def cleanup(self):
        """Cleanup resources."""
        if self._postep:
            try:
                self._postep.set_run(False)
            except Exception as e:
                print(f"Error cleaning up PoStep256 device: {e}")
        self._initialized = False
        print("PoStep256 device cleanup completed")


# Global singleton instance
postep256_handler = Postep256Handler()
