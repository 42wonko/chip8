"""
@file instruction.py

@brief Decoded CHIP-8 instruction.

@details
Represents a single decoded CHIP-8 instruction.

The instruction is immutable and contains the opcode together with its
decoded operands. It does not execute itself; execution is performed by
the CHIP-8 machine.

The instruction address is stored to support debugging, tracing,
disassembly and breakpoint handling.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from dataclasses import dataclass

from emulator.constants import ADDRESS_MASK, BYTE_MASK, NIBBLE_MASK


@dataclass(frozen=True, slots=True)
class Instruction:
    """
    @brief Decoded CHIP-8 instruction.
    """
    address: int
    opcode: int
    x: int
    y: int
    n: int
    nn: int
    nnn: int


    def __str__(self) -> str:
        """
        @brief Return the CHIP-8 assembly representation.

        @return
            Assembly language representation of the instruction.
        """
        match self.family:
            case 0x0:        # 0nnn
                match self.opcode:
                    case 0x00E0:
                        return "CLS"

                    case 0x00EE:
                        return "RET"
                    case _:
                        return f"SYS {self.nnn:03X}"
            case 0x1:                                           # 1nnn
                return f"JP {self.nnn:03X}"
            case 0x2:                                           # 2nnn
                return f"CALL {self.nnn:03X}"
            case 0x3:                                           # 3xkk
                return f"SE V{self.x:X}, {self.nn:02X}"
            case 0x4:                                           # 4xkk
                return f"SNE V{self.x:X}, {self.nn:02X}"
            case 0x5:                                           # 5xy0
                return f"SE V{self.x:X}, V{self.y:X}"
            case 0x6:                                           # 6xkk
                return f"LD V{self.x:X}, {self.nn:02X}"
            case 0x7:                                           # 7xkk
                return f"ADD V{self.x:X}, {self.nn:02X}"
            case 0x8:                                           # 8xy*
                match self.n:

                    case 0x0:
                        return f"LD V{self.x:X}, V{self.y:X}"

                    case 0x1:
                        return f"OR V{self.x:X}, V{self.y:X}"

                    case 0x2:
                        return f"AND V{self.x:X}, V{self.y:X}"

                    case 0x3:
                        return f"XOR V{self.x:X}, V{self.y:X}"

                    case 0x4:
                        return f"ADD V{self.x:X}, V{self.y:X}"

                    case 0x5:
                        return f"SUB V{self.x:X}, V{self.y:X}"

                    case 0x6:
                        return f"SHR V{self.x:X}"

                    case 0x7:
                        return f"SUBN V{self.x:X}, V{self.y:X}"

                    case 0xE:
                        return f"SHL V{self.x:X}"

                    case _:
                        return f"DATA {self.opcode:04X}"

            case 0x9:
                return f"SNE V{self.x:X}, V{self.y:X}"          # 9xy0

            case 0xA:                                           # Annn
                return f"LD I, {self.nnn:03X}"

            case 0xB:                                           # Bnnn
                return f"JP V0, {self.nnn:03X}"

            case 0xC:                                           # Cxkk
                return f"RND V{self.x:X}, {self.nn:02X}"

            case 0xD:                                           # Dxyn
                return f"DRW V{self.x:X}, V{self.y:X}, {self.n:X}"

            case 0xE:                                           # Ex**
                match self.nn:

                    case 0x9E:
                        return f"SKP V{self.x:X}"

                    case 0xA1:
                        return f"SKNP V{self.x:X}"

                    case _:
                        return f"DATA {self.opcode:04X}"

            case 0xF:                                           # Fx**
                match self.nn:

                    case 0x07:
                        return f"LD V{self.x:X}, DT"

                    case 0x0A:
                        return f"LD V{self.x:X}, K"

                    case 0x15:
                        return f"LD DT, V{self.x:X}"

                    case 0x18:
                        return f"LD ST, V{self.x:X}"

                    case 0x1E:
                        return f"ADD I, V{self.x:X}"

                    case 0x29:
                        return f"LD F, V{self.x:X}"

                    case 0x33:
                        return f"LD B, V{self.x:X}"

                    case 0x55:
                        return f"LD [I], V{self.x:X}"

                    case 0x65:
                        return f"LD V{self.x:X}, [I]"

                    case _:
                        return f"DATA {self.opcode:04X}"
            case _:                                             # Unknown opcode family.
                return f"DATA {self.opcode:04X}"


    @property
    def family(self) -> int:
        """
        @brief Return the primary opcode family.

        @return
            Upper opcode nibble.
        """
        return (self.opcode >> 12) & NIBBLE_MASK


    @classmethod
    def decode( cls, address: int, opcode: int) -> Instruction:
        """
        @brief Decode an opcode.

        @param address
            Address of the instruction.

        @param opcode
            16-bit opcode.

        @return
            Decoded instruction.
        """
        return cls(
            address=address & ADDRESS_MASK,
            opcode=opcode,
            x=(opcode >> 8) & NIBBLE_MASK,
            y=(opcode >> 4) & NIBBLE_MASK,
            n=opcode & NIBBLE_MASK,
            nn=opcode & BYTE_MASK,
            nnn=opcode & ADDRESS_MASK
        )


