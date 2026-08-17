"""
@file target.py

@brief Target architecture definitions for the assembler.
"""

from __future__ import annotations

from enum import StrEnum


class Target(StrEnum):
    """
    @brief Identifies a target architecture supported by the assembler.
    """
    COSMAC = "COSMAC"
