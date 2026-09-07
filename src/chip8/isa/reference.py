"""
@file reference.py

@brief Instruction resource reference definitions.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReferenceAccess(StrEnum):
    """
    @brief Access mode for an instruction resource reference.
    """

    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"


@dataclass(frozen=True, slots=True)
class InstructionReference:
    """
    @brief Reference to an architectural resource accessed by an instruction.
    """

    resource: str
    access: ReferenceAccess
