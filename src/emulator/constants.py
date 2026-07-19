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
# Fonts
###############################################################################
FONTSET: list[int] = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]
FONT_SIZE: int = len(FONTSET)
FONT_START: int = 0x050             # Start address for CHIP-8 fonts.
FONT_ADDRESS: int = 0x000           # Location of the built-in font.
FONT_CHARACTER_COUNT: int = 16      # we have 16 HEX characters 0-9,a-f
FONT_CHARACTER_SIZE: int = 5        # each character is encodes in 5 bytes

###############################################################################
# Memory
###############################################################################
MEMORY_SIZE: int = 4096             # Total memory size in bytes.
PROGRAM_START: int = 0x200          # Start address for CHIP-8 programs.
CHIP8_STACK_SIZE = 16               # stack has room for 16 return addresses

###############################################################################
# CPU
###############################################################################
REGISTER_COUNT: int = 16            # Number of general-purpose registers.
STACK_SIZE: int = 16                # Maximum call stack depth.
KEY_COUNT: int = 16                 # Number of hexadecimal keys.

###############################################################################
# Timers
###############################################################################
TIMER_FREQUENCY: int = 60           # 60Hz
DEFAULT_CPU_FREQUENCY: int   = 500  # Main clock is 500Hz

###############################################################################
# Audio
###############################################################################
BEEPER_FREQUENCY = 440              #
BEEPER_SAMPLE_RATE = 44100          #
BEEPER_AMPLITUDE = 16000            #

###############################################################################
# Instruction size
###############################################################################
INSTRUCTION_SIZE:int = 2            # Every CHIP-8 instruction is 2 bytes long

###############################################################################
# Masks
###############################################################################
BYTE_MASK: int          = 0x00FF    # make sure a value stays within 8 bits
NIBBLE_MASK: int        = 0x000F    # mask the lower 4 bits of a byte.
ADDRESS_MASK: int       = 0x0FFF    # makae sure an address is alwas within 12 bits
STACK_POINTER_MASK: int = 0x000F    # we have a 4 bit stack pointer

###############################################################################
# Application / Version
###############################################################################
APPLICATION_NAME = "CHIP-8 Emulator"
APPLICATION_VERSION = "1.0.0"
