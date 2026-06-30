"""
@file types.py

@brief Common NumPy type aliases.

@details
Defines strongly typed aliases for the data structures used by the
emulator.

@author
    <your name>

@copyright
    MIT License
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

Framebuffer = NDArray[np.bool_]     # CHIP-8 display framebuffer.
Memory = NDArray[np.uint8]          # Complete 4 KiB memory.
Registers = NDArray[np.uint8]       # Sixteen V registers.
Stack = NDArray[np.uint16]          # Return address stack.

