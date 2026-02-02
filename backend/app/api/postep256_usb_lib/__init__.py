"""PostEP256 USB Motor Controller Library.

A Python library for controlling PostEP256 stepper motor controllers via USB.

This is a local copy of the PostEP256 USB driver from IRNAS.
Original repository: https://github.com/IRNAS/postep256-pyusb-driver
"""

from .postep256usb import PoStep256USB

__version__ = "1.0.0"
__author__ = "IRNAS"
__all__ = ["PoStep256USB"]
