"""
@file constants.py

@brief Global CHIP-8 constants.

@details
This module defines the architectural constants of the CHIP-8 virtual
machine. They are shared by the emulator core and the GUI.

@author
    Michael Dlubatz

@copyright
    MIT License
"""

from __future__ import annotations

###############################################################################
# Display
###############################################################################
DISPLAY_WIDTH: int = 64             # Display width in pixels.
DISPLAY_HEIGHT: int = 32            # Display height in pixels.

###############################################################################
# Memory
###############################################################################
MEMORY_SIZE: int = 4096             # Total memory size in bytes.
PROGRAM_START: int = 0x200          # Start address for CHIP-8 programs.

###############################################################################
# CPU
###############################################################################
REGISTER_COUNT: int = 16            # Number of general-purpose registers.
STACK_SIZE: int = 16                # Maximum call stack depth.
KEY_COUNT: int = 16                 # Number of hexadecimal keys.
FONT_ADDRESS: int = 0x000           # Location of the built-in font.

