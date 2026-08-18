"""
@file classicisa.py

@brief Classic CHIP-8 instruction set architecture.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

import random
from collections.abc import Callable

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import ControlFlow, InstructionAnalysis, InstructionSetArchitecture
from emulator.chip8machine import Chip8Machine
from emulator.constants import (
    ADDRESS_MASK,
    BYTE_MASK,
    FONT_CHARACTER_SIZE,
    FONT_START,
    NIBBLE_MASK,
    WORD_MASK,
)
from emulator.stepresult import StepResult


class ClassicInstructionSetArchitecture(InstructionSetArchitecture):
    """
    @brief Instruction Set Architecture for Classic CHIP-8.
    """

    _ExecuteHandler = Callable[[Instruction], StepResult]
    _FormatHandler = Callable[[Instruction], str]

    def __init__(self, machine: Chip8Machine) -> None:
        """
        @brief Construct the Classic CHIP-8 ISA.

        @param machine
            Machine whose state is modified by instruction execution.
        """
        self._machine = machine
        self._execute_handlers: dict[ InstructionId, ClassicInstructionSetArchitecture._ExecuteHandler ] = {
            InstructionId.SYS: self._execute_sys,
            InstructionId.CLS: self._execute_cls,
            InstructionId.RET: self._execute_ret,
            InstructionId.JP: self._execute_jp,
            InstructionId.CALL: self._execute_call,
            InstructionId.SE_BYTE: self._execute_se_byte,
            InstructionId.SNE_BYTE: self._execute_sne_byte,
            InstructionId.SE_REGISTER: self._execute_se_register,
            InstructionId.LD_BYTE: self._execute_ld_byte,
            InstructionId.ADD_BYTE: self._execute_add_byte,
            InstructionId.LD_REGISTER: self._execute_ld_register,
            InstructionId.OR: self._execute_or,
            InstructionId.AND: self._execute_and,
            InstructionId.XOR: self._execute_xor,
            InstructionId.ADD_REGISTER: self._execute_add_register,
            InstructionId.SUB: self._execute_sub,
            InstructionId.SHR: self._execute_shr,
            InstructionId.SUBN: self._execute_subn,
            InstructionId.SHL: self._execute_shl,
            InstructionId.SNE_REGISTER: self._execute_sne_register,
            InstructionId.LD_I: self._execute_ld_i,
            InstructionId.JP_V0: self._execute_jp_v0,
            InstructionId.RND: self._execute_rnd,
            InstructionId.DRW: self._execute_drw,
            InstructionId.SKP: self._execute_skp,
            InstructionId.SKNP: self._execute_sknp,
            InstructionId.LD_VX_DT: self._execute_ld_vx_dt,
            InstructionId.LD_VX_K: self._execute_ld_vx_k,
            InstructionId.LD_DT_VX: self._execute_ld_dt_vx,
            InstructionId.LD_ST_VX: self._execute_ld_st_vx,
            InstructionId.ADD_I_VX: self._execute_add_i_vx,
            InstructionId.LD_F_VX: self._execute_ld_f_vx,
            InstructionId.LD_B_VX: self._execute_ld_b_vx,
            InstructionId.LD_I_VX: self._execute_ld_i_vx,
            InstructionId.LD_VX_I: self._execute_ld_vx_i
        }

        self._format_handlers: dict[ InstructionId, ClassicInstructionSetArchitecture._FormatHandler ] = {
            InstructionId.SYS: self._format_sys,
            InstructionId.CLS: self._format_cls,
            InstructionId.RET: self._format_ret,
            InstructionId.JP: self._format_jp,
            InstructionId.CALL: self._format_call,
            InstructionId.SE_BYTE: self._format_se_byte,
            InstructionId.SNE_BYTE: self._format_sne_byte,
            InstructionId.SE_REGISTER: self._format_se_register,
            InstructionId.LD_BYTE: self._format_ld_byte,
            InstructionId.ADD_BYTE: self._format_add_byte,
            InstructionId.LD_REGISTER: self._format_ld_register,
            InstructionId.OR: self._format_or,
            InstructionId.AND: self._format_and,
            InstructionId.XOR: self._format_xor,
            InstructionId.ADD_REGISTER: self._format_add_register,
            InstructionId.SUB: self._format_sub,
            InstructionId.SHR: self._format_shr,
            InstructionId.SUBN: self._format_subn,
            InstructionId.SHL: self._format_shl,
            InstructionId.SNE_REGISTER: self._format_sne_register,
            InstructionId.LD_I: self._format_ld_i,
            InstructionId.JP_V0: self._format_jp_v0,
            InstructionId.RND: self._format_rnd,
            InstructionId.DRW: self._format_drw,
            InstructionId.SKP: self._format_skp,
            InstructionId.SKNP: self._format_sknp,
            InstructionId.LD_VX_DT: self._format_ld_vx_dt,
            InstructionId.LD_VX_K: self._format_ld_vx_k,
            InstructionId.LD_DT_VX: self._format_ld_dt_vx,
            InstructionId.LD_ST_VX: self._format_ld_st_vx,
            InstructionId.ADD_I_VX: self._format_add_i_vx,
            InstructionId.LD_F_VX: self._format_ld_f_vx,
            InstructionId.LD_B_VX: self._format_ld_b_vx,
            InstructionId.LD_I_VX: self._format_ld_i_vx,
            InstructionId.LD_VX_I: self._format_ld_vx_i
        }

    ###############################################################################
    # Public interface
    ###############################################################################
    def decode(self, address: int, opcode: int) -> Instruction:
        """
        @brief Decode a Classic CHIP-8 opcode.

        @param address
            Address of the instruction.

        @param opcode
            Raw 16-bit opcode.

        @return
            Decoded instruction.
        """
        opcode &= WORD_MASK

        x = (opcode >> 8) & NIBBLE_MASK
        y = (opcode >> 4) & NIBBLE_MASK
        n = opcode & NIBBLE_MASK
        nn = opcode & BYTE_MASK
        nnn = opcode & ADDRESS_MASK

        instruction_id = self._decode_id(opcode)

        return Instruction(
            address=address & ADDRESS_MASK,
            opcode=opcode,
            id=instruction_id,
            x=x,
            y=y,
            n=n,
            nn=nn,
            nnn=nnn,
        )

    def create_assembler_instruction( self, mnemonic: str, operands: tuple[AssemblerOperand, ...]) -> AssemblerInstruction:
        """
        @brief Create a Classic CHIP-8 assembler instruction.

        @param mnemonic
            Assembly instruction mnemonic.

        @param operands
            Evaluated assembler operands.

        @return
            Classic Chip-8 assembler instruction.

        @exception ValueError
            If the mnemonic or operand combination is invalid.
        """
        name = mnemonic.upper()

        if name == "CLS":
            if operands:
                raise ValueError( "CLS does not accept operands.")
            return AssemblerInstruction( id=InstructionId.CLS)

        if name == "RET":
            if operands:
                raise ValueError( "RET does not accept operands.")
            return AssemblerInstruction( id=InstructionId.RET)

        if name == "SYS":
            if len(operands) != 1:
                raise ValueError( "SYS requires exactly one operand.")
            operand = operands[0]
            if operand.type != AssemblerOperandType.ADDRESS:
                raise ValueError( "SYS requires an address operand.")
            if not 0 <= operand.value <= 0xFFF:
                raise ValueError( "SYS address must be in the range 0x000 to 0xFFF.")
            return AssemblerInstruction( id=InstructionId.SYS, nnn=operand.value)
        if name == "JP":
            if len(operands) == 1:
                operand = operands[0]
                if operand.type != AssemblerOperandType.ADDRESS:
                    raise ValueError( "JP requires an address operand.")
                if not 0 <= operand.value <= 0xFFF:
                    raise ValueError( "JP address must be in the range 0x000 to 0xFFF.")
                return AssemblerInstruction( id=InstructionId.JP, nnn=operand.value)
            if len(operands) == 2:
                register = operands[0]
                address = operands[1]
                if register.type != AssemblerOperandType.REGISTER:
                    raise ValueError( "JP V0, nnn requires V0 as the first operand.")
                if register.value != 0:
                    raise ValueError( "JP V0, nnn requires V0 as the first operand.")
                if address.type != AssemblerOperandType.ADDRESS:
                    raise ValueError( "JP V0, nnn requires an address as the second operand.")
                if not 0 <= address.value <= 0xFFF:
                    raise ValueError( "JP address must be in the range 0x000 to 0xFFF.")
                return AssemblerInstruction( id=InstructionId.JP_V0, nnn=address.value)
            raise ValueError( "JP requires one or two operands.")

        if name == "CALL":
            if len(operands) != 1:
                raise ValueError( "CALL requires exactly one operand.")
            operand = operands[0]
            if operand.type != AssemblerOperandType.ADDRESS:
                raise ValueError( "CALL requires an address operand.")
            if not 0 <= operand.value <= 0xFFF:
                raise ValueError( "CALL address must be in the range 0x000 to 0xFFF.")
            return AssemblerInstruction( id=InstructionId.CALL, nnn=operand.value)

        if name == "LD":
            if len(operands) != 2:
                raise ValueError( "LD requires exactly two operands.")
            first = operands[0]
            second = operands[1]
            if ( first.type == AssemblerOperandType.REGISTER and second.type == AssemblerOperandType.REGISTER):
                if not 0 <= first.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                if not 0 <= second.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                return AssemblerInstruction( id=InstructionId.LD_REGISTER, x=first.value, y=second.value)
            if ( first.type == AssemblerOperandType.REGISTER and second.type == AssemblerOperandType.VALUE):
                if not 0 <= first.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                if not 0 <= second.value <= 0xFF:
                    raise ValueError( "LD immediate value must be in the range 0x00 to 0xFF.")
                return AssemblerInstruction( id=InstructionId.LD_BYTE, x=first.value, nn=second.value)
            if ( first.type == AssemblerOperandType.INDEX_REGISTER and second.type == AssemblerOperandType.ADDRESS):
                if not 0 <= second.value <= 0xFFF:
                    raise ValueError( "LD I address must be in the range 0x000 to 0xFFF.")
                return AssemblerInstruction( id=InstructionId.LD_I, nnn=second.value)
            if ( first.type == AssemblerOperandType.REGISTER and second.type == AssemblerOperandType.DELAY_REGISTER):
                if not 0 <= first.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                return AssemblerInstruction( id=InstructionId.LD_VX_DT, x=first.value)
            if ( first.type == AssemblerOperandType.REGISTER and second.type == AssemblerOperandType.KEY):
                if not 0 <= first.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                return AssemblerInstruction( id=InstructionId.LD_VX_K, x=first.value)
            if ( first.type == AssemblerOperandType.DELAY_REGISTER and second.type == AssemblerOperandType.REGISTER):
                if not 0 <= second.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                return AssemblerInstruction( id=InstructionId.LD_DT_VX, x=second.value)
            if ( first.type == AssemblerOperandType.SOUND_REGISTER and second.type == AssemblerOperandType.REGISTER):
                if not 0 <= second.value <= 0xF:
                    raise ValueError( "Register must be in the range V0 to VF.")
                return AssemblerInstruction( id=InstructionId.LD_ST_VX, x=second.value)
            raise ValueError( "Invalid operand combination for LD.")

        raise ValueError( f"Unsupported Classic CHIP-8 instruction: {mnemonic}")


    def encode(self, instruction: AssemblerInstruction) -> int:
        """
        @brief Encode an assembler instruction as a Classic CHIP-8 opcode.

        @param instruction
            Instruction to encode.

        @return
            Raw 16-bit CHIP-8 opcode.

        @exception ValueError
            If the instruction is not supported or a required operand
            is missing or outside its valid range.
        """
        match instruction.id:
            case InstructionId.SYS:
                return self._encode_nnn(0x0000, instruction.nnn)

            case InstructionId.CLS:
                return 0x00E0

            case InstructionId.RET:
                return 0x00EE

            case InstructionId.JP:
                return self._encode_nnn(0x1000, instruction.nnn)

            case InstructionId.CALL:
                return self._encode_nnn(0x2000, instruction.nnn)

            case InstructionId.SE_BYTE:
                return self._encode_x_nn(0x3000, instruction.x, instruction.nn)

            case InstructionId.SNE_BYTE:
                return self._encode_x_nn(0x4000, instruction.x, instruction.nn)

            case InstructionId.SE_REGISTER:
                return self._encode_x_y_nibble( 0x5000, instruction.x, instruction.y, 0x0,)

            case InstructionId.LD_BYTE:
                return self._encode_x_nn(0x6000, instruction.x, instruction.nn)

            case InstructionId.ADD_BYTE:
                return self._encode_x_nn(0x7000, instruction.x, instruction.nn)

            case InstructionId.LD_REGISTER:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x0,)

            case InstructionId.OR:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x1,)

            case InstructionId.AND:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x2,)

            case InstructionId.XOR:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x3,)

            case InstructionId.ADD_REGISTER:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x4,)

            case InstructionId.SUB:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x5,)

            case InstructionId.SHR:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x6,)

            case InstructionId.SUBN:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0x7,)

            case InstructionId.SHL:
                return self._encode_x_y_nibble( 0x8000, instruction.x, instruction.y, 0xE,)

            case InstructionId.SNE_REGISTER:
                return self._encode_x_y_nibble( 0x9000, instruction.x, instruction.y, 0x0,)

            case InstructionId.LD_I:
                return self._encode_nnn(0xA000, instruction.nnn)

            case InstructionId.JP_V0:
                return self._encode_nnn(0xB000, instruction.nnn)

            case InstructionId.RND:
                return self._encode_x_nn(0xC000, instruction.x, instruction.nn)

            case InstructionId.DRW:
                return self._encode_x_y_nibble( 0xD000, instruction.x, instruction.y, self._require_n(instruction.n),)

            case InstructionId.SKP:
                return self._encode_x_fixed(instruction.x, 0xE09E)

            case InstructionId.SKNP:
                return self._encode_x_fixed(instruction.x, 0xE0A1)

            case InstructionId.LD_VX_DT:
                return self._encode_x_fixed(instruction.x, 0xF007)

            case InstructionId.LD_VX_K:
                return self._encode_x_fixed(instruction.x, 0xF00A)

            case InstructionId.LD_DT_VX:
                return self._encode_x_fixed(instruction.x, 0xF015)

            case InstructionId.LD_ST_VX:
                return self._encode_x_fixed(instruction.x, 0xF018)

            case InstructionId.ADD_I_VX:
                return self._encode_x_fixed(instruction.x, 0xF01E)

            case InstructionId.LD_F_VX:
                return self._encode_x_fixed(instruction.x, 0xF029)

            case InstructionId.LD_B_VX:
                return self._encode_x_fixed(instruction.x, 0xF033)

            case InstructionId.LD_I_VX:
                return self._encode_x_fixed(instruction.x, 0xF055)

            case InstructionId.LD_VX_I:
                return self._encode_x_fixed(instruction.x, 0xF065)

            case InstructionId.UNKNOWN:
                raise ValueError("Cannot encode an unknown instruction.")

        raise ValueError(
            f"Unsupported instruction ID: {instruction.id!s}."
        )


    def execute(self, instruction: Instruction) -> StepResult:
        handler = self._execute_handlers.get(instruction.id)
        if handler is None:
            raise ValueError( f"No execution handler for instruction ID {instruction.id}.")
        return handler(instruction)


    def format(self, instruction: Instruction) -> str:
        handler = self._format_handlers.get(instruction.id)
        if handler is None:
            raise ValueError( f"No format handler for instruction ID {instruction.id!s}.")
        return handler(instruction)


    def analyze(self, instruction: Instruction) -> InstructionAnalysis:
        next_address = instruction.address + 2

        match instruction.id:
            case InstructionId.RET:
                return InstructionAnalysis( control_flow=ControlFlow.RETURN, targets=(), is_code = True)

            case InstructionId.JP:
                return InstructionAnalysis( control_flow=ControlFlow.BRANCH, targets=(instruction.nnn,), is_code = True)

            case InstructionId.CALL:
                return InstructionAnalysis( control_flow=ControlFlow.CALL, targets=(instruction.nnn,), is_code = True)

            case InstructionId.SE_BYTE | InstructionId.SNE_BYTE:
                return InstructionAnalysis( control_flow=ControlFlow.CONDITIONAL_BRANCH, targets=(next_address, next_address + 2), is_code = True)

            case InstructionId.SE_REGISTER:
                if instruction.n != 0:
                    return InstructionAnalysis( control_flow=ControlFlow.TERMINATE, targets=(), is_code = True)
                return InstructionAnalysis( control_flow=ControlFlow.CONDITIONAL_BRANCH, targets=(next_address, next_address + 2), is_code = True)

            case InstructionId.SNE_REGISTER:
                return InstructionAnalysis( control_flow=ControlFlow.CONDITIONAL_BRANCH, targets=(next_address, next_address + 2), is_code = True)

            case InstructionId.JP_V0:
                return InstructionAnalysis( control_flow=ControlFlow.BRANCH, targets=(), is_code = True)

            case InstructionId.SKP | InstructionId.SKNP:
                return InstructionAnalysis( control_flow=ControlFlow.CONDITIONAL_BRANCH, targets=(next_address, next_address + 2), is_code = True)

            case InstructionId.SYS:
                return InstructionAnalysis( control_flow=ControlFlow.TERMINATE, targets=(), is_code = True)

            case InstructionId.UNKNOWN:
                return InstructionAnalysis( control_flow=ControlFlow.TERMINATE, targets=(), is_code = False)

            case _:
                return InstructionAnalysis( control_flow=ControlFlow.NEXT, targets=(next_address,), is_code = True)



    ###############################################################################
    # Private helpers
    ###############################################################################
    def _decode_id(self, opcode: int) -> InstructionId:
        """
        @brief Determine the instruction identifier for an opcode.

        @param opcode
            Raw 16-bit opcode.

        @return
            Instruction identifier.
        """
        match opcode & 0xF000:
            case 0x0000:
                match opcode:
                    case 0x00E0:
                        return InstructionId.CLS

                    case 0x00EE:
                        return InstructionId.RET

                    case _:
                        return InstructionId.SYS

            case 0x1000:
                return InstructionId.JP

            case 0x2000:
                return InstructionId.CALL

            case 0x3000:
                return InstructionId.SE_BYTE

            case 0x4000:
                return InstructionId.SNE_BYTE

            case 0x5000:
                if (opcode & NIBBLE_MASK) == 0:
                    return InstructionId.SE_REGISTER
                return InstructionId.UNKNOWN

            case 0x6000:
                return InstructionId.LD_BYTE

            case 0x7000:
                return InstructionId.ADD_BYTE

            case 0x8000:
                match opcode & NIBBLE_MASK:
                    case 0x0:
                        return InstructionId.LD_REGISTER

                    case 0x1:
                        return InstructionId.OR

                    case 0x2:
                        return InstructionId.AND

                    case 0x3:
                        return InstructionId.XOR

                    case 0x4:
                        return InstructionId.ADD_REGISTER

                    case 0x5:
                        return InstructionId.SUB

                    case 0x6:
                        return InstructionId.SHR

                    case 0x7:
                        return InstructionId.SUBN

                    case 0xE:
                        return InstructionId.SHL

                    case _:
                        return InstructionId.UNKNOWN

            case 0x9000:
                if (opcode & NIBBLE_MASK) == 0:
                    return InstructionId.SNE_REGISTER
                return InstructionId.UNKNOWN

            case 0xA000:
                return InstructionId.LD_I

            case 0xB000:
                return InstructionId.JP_V0

            case 0xC000:
                return InstructionId.RND

            case 0xD000:
                return InstructionId.DRW

            case 0xE000:
                match opcode & BYTE_MASK:
                    case 0x9E:
                        return InstructionId.SKP

                    case 0xA1:
                        return InstructionId.SKNP

                    case _:
                        return InstructionId.UNKNOWN

            case 0xF000:
                match opcode & BYTE_MASK:
                    case 0x07:
                        return InstructionId.LD_VX_DT

                    case 0x0A:
                        return InstructionId.LD_VX_K

                    case 0x15:
                        return InstructionId.LD_DT_VX

                    case 0x18:
                        return InstructionId.LD_ST_VX

                    case 0x1E:
                        return InstructionId.ADD_I_VX

                    case 0x29:
                        return InstructionId.LD_F_VX

                    case 0x33:
                        return InstructionId.LD_B_VX

                    case 0x55:
                        return InstructionId.LD_I_VX

                    case 0x65:
                        return InstructionId.LD_VX_I

                    case _:
                        return InstructionId.UNKNOWN

            case _:
                return InstructionId.UNKNOWN


    @staticmethod
    def _require_operand( value: int | None, name: str, maximum: int) -> int:
        """
        @brief Validate and return an assembler operand.

        @param value
            Operand value.

        @param name
            Operand name used in the error message.

        @param maximum
            Maximum valid operand value.

        @return
            Validated operand.

        @exception ValueError
            If the operand is missing or outside its valid range.
        """
        if value is None:
            raise ValueError(f"Missing operand: {name}.")

        if not 0 <= value <= maximum:
            raise ValueError(
                f"Operand {name} is outside its valid range: {value}."
            )

        return value


    @classmethod
    def _require_x(cls, value: int | None) -> int:
        """
        @brief Validate a register X operand.

        @param value
            Register number.

        @return
            Validated register number.
        """
        return cls._require_operand(value, "x", NIBBLE_MASK)


    @classmethod
    def _require_y(cls, value: int | None) -> int:
        """
        @brief Validate a register Y operand.

        @param value
            Register number.

        @return
            Validated register number.
        """
        return cls._require_operand(value, "y", NIBBLE_MASK)


    @classmethod
    def _require_n(cls, value: int | None) -> int:
        """
        @brief Validate a nibble operand.

        @param value
            Nibble value.

        @return
            Validated nibble value.
        """
        return cls._require_operand(value, "n", NIBBLE_MASK)


    @classmethod
    def _require_nn(cls, value: int | None) -> int:
        """
        @brief Validate a byte operand.

        @param value
            Byte value.

        @return
            Validated byte value.
        """
        return cls._require_operand(value, "nn", BYTE_MASK)


    @classmethod
    def _require_nnn(cls, value: int | None) -> int:
        """
        @brief Validate a 12-bit address operand.

        @param value
            Address value.

        @return
            Validated address value.
        """
        return cls._require_operand(value, "nnn", ADDRESS_MASK)


    @classmethod
    def _encode_nnn( cls, base: int, nnn: int | None) -> int:
        """
        @brief Encode an instruction containing a 12-bit address.

        @param base
            Opcode base.

        @param nnn
            12-bit address operand.

        @return
            Encoded opcode.
        """
        return base | cls._require_nnn(nnn)


    @classmethod
    def _encode_x_nn( cls, base: int, x: int | None, nn: int | None) -> int:
        """
        @brief Encode an instruction containing X and byte operands.

        @param base
            Opcode base.

        @param x
            X register.

        @param nn
            Byte operand.

        @return
            Encoded opcode.
        """
        return ( base | (cls._require_x(x) << 8) | cls._require_nn(nn))


    @classmethod
    def _encode_x_y_nibble( cls, base: int, x: int | None, y: int | None, n: int) -> int:
        """
        @brief Encode an instruction containing X, Y and nibble operands.

        @param base
            Opcode base.

        @param x
            X register.

        @param y
            Y register.

        @param n
            Low-order opcode nibble.

        @return
            Encoded opcode.
        """
        return ( base | (cls._require_x(x) << 8) | (cls._require_y(y) << 4) | n)


    @classmethod
    def _encode_x_fixed( cls, x: int | None, suffix: int) -> int:
        """
        @brief Encode an instruction containing X and a fixed suffix.

        @param x
            X register.

        @param suffix
            Fixed opcode suffix.

        @return
            Encoded opcode.
        """
        return (cls._require_x(x) << 8) | suffix


    ###############################################################################
    # Private execute methods
    ###############################################################################
    def _execute_sys(self, instruction: Instruction) -> StepResult:
        raise NotImplementedError(f"Opcode {instruction.opcode:04X} is not implemented.")

    def _execute_cls(self, instruction: Instruction) -> StepResult:
        result = StepResult()
        self._machine.framebuffer.clear()
        result.display_changed = True
        return result

    def _execute_ret(self, instruction: Instruction) -> StepResult:
        result = StepResult()
        self._machine.registers.pc = self._machine.stack.pop()
        return result

    def _execute_jp(self, instruction: Instruction) -> StepResult:
        self._machine.registers.pc = instruction.nnn
        return StepResult()

    def _execute_call(self, instruction: Instruction) -> StepResult:
        self._machine.stack.push(self._machine.registers.pc)
        self._machine.registers.pc = instruction.nnn
        return StepResult()

    def _execute_se_byte(self, instruction: Instruction) -> StepResult:
        if self._machine.registers[instruction.x] == instruction.nn:
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_sne_byte(self, instruction: Instruction) -> StepResult:
        if self._machine.registers[instruction.x] != instruction.nn:
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_se_register(self, instruction: Instruction) -> StepResult:
        if instruction.n != 0:
            raise NotImplementedError( f"Opcode {instruction.opcode:04X} is not implemented.")
        if self._machine.registers[instruction.x] == self._machine.registers[instruction.y]:
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_ld_byte(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] = instruction.nn
        return StepResult()

    def _execute_add_byte(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] += instruction.nn
        return StepResult()

    def _execute_ld_register(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] = self._machine.registers[instruction.y]
        return StepResult()

    def _execute_or(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] |= self._machine.registers[instruction.y]
        return StepResult()

    def _execute_and(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] &= self._machine.registers[instruction.y]
        return StepResult()

    def _execute_xor(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] ^= self._machine.registers[instruction.y]
        return StepResult()

    def _execute_add_register(self, instruction: Instruction) -> StepResult:
        vx = self._machine.registers[instruction.x]
        vy = self._machine.registers[instruction.y]
        total = vx + vy
        self._machine.registers[0xF] = 1 if total > 0xFF else 0
        self._machine.registers[instruction.x] = total
        return StepResult()

    def _execute_sub(self, instruction: Instruction) -> StepResult:
        vx = self._machine.registers[instruction.x]
        vy = self._machine.registers[instruction.y]
        self._machine.registers[0xF] = 1 if vx >= vy else 0
        self._machine.registers[instruction.x] = vx - vy
        return StepResult()

    def _execute_shr(self, instruction: Instruction) -> StepResult:
        vx = self._machine.registers[instruction.x]
        self._machine.registers[0xF] = vx & 0x01
        self._machine.registers[instruction.x] = vx >> 1
        return StepResult()

    def _execute_subn(self, instruction: Instruction) -> StepResult:
        vx = self._machine.registers[instruction.x]
        vy = self._machine.registers[instruction.y]
        self._machine.registers[0xF] = 1 if vy >= vx else 0
        self._machine.registers[instruction.x] = vy - vx
        return StepResult()

    def _execute_shl(self, instruction: Instruction) -> StepResult:
        vx = self._machine.registers[instruction.x]
        self._machine.registers[0xF] = (vx >> 7) & 0x01
        self._machine.registers[instruction.x] = vx << 1
        return StepResult()

    def _execute_sne_register(self, instruction: Instruction) -> StepResult:
        if self._machine.registers[instruction.x] != self._machine.registers[instruction.y]:
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_ld_i(self, instruction: Instruction) -> StepResult:
        self._machine.registers.i = instruction.nnn
        return StepResult()

    def _execute_jp_v0(self, instruction: Instruction) -> StepResult:
        self._machine.registers.pc = instruction.nnn + self._machine.registers[0]
        return StepResult()

    def _execute_rnd(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] = (random.randint(0, 0xFF) & instruction.nn)
        return StepResult()

    def _execute_drw(self, instruction: Instruction) -> StepResult:
        result = StepResult()
        collision = False
        x = self._machine.registers[instruction.x]
        y = self._machine.registers[instruction.y]
        for row in range(instruction.n):
            sprite = self._machine.memory.read_byte(self._machine.registers.i + row)
            for bit in range(8):
                if sprite & (0x80 >> bit):
                    if self._machine.framebuffer.xor_pixel(x + bit, y + row):
                        collision = True
        self._machine.registers[0xF] = 1 if collision else 0
        result.display_changed = True
        return result

    def _execute_skp(self, instruction: Instruction) -> StepResult:
        if self._machine.keyboard.is_pressed(self._machine.registers[instruction.x]):
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_sknp(self, instruction: Instruction) -> StepResult:
        if not self._machine.keyboard.is_pressed(self._machine.registers[instruction.x]):
            self._machine.registers.pc += 2
        return StepResult()

    def _execute_ld_vx_dt(self, instruction: Instruction) -> StepResult:
        self._machine.registers[instruction.x] = self._machine.timers.delay_timer
        return StepResult()

    def _execute_ld_vx_k(self, instruction: Instruction) -> StepResult:
        key = self._machine.keyboard.first_pressed()
        if key is None:
            self._machine.registers.pc -= 2
        else:
            self._machine.registers[instruction.x] = key
        return StepResult()

    def _execute_ld_dt_vx(self, instruction: Instruction) -> StepResult:
        self._machine.timers.delay_timer = self._machine.registers[instruction.x]
        return StepResult()

    def _execute_ld_st_vx(self, instruction: Instruction) -> StepResult:
        self._machine.timers.sound_timer = self._machine.registers[instruction.x]
        return StepResult()

    def _execute_add_i_vx(self, instruction: Instruction) -> StepResult:
        self._machine.registers.i += self._machine.registers[instruction.x]
        return StepResult()

    def _execute_ld_f_vx(self, instruction: Instruction) -> StepResult:
        digit = self._machine.registers[instruction.x] & NIBBLE_MASK
        self._machine.registers.i = FONT_START + digit * FONT_CHARACTER_SIZE
        return StepResult()

    def _execute_ld_b_vx(self, instruction: Instruction) -> StepResult:
        result = StepResult()
        value = self._machine.registers[instruction.x]
        self._machine.memory.write_byte(self._machine.registers.i + 0, value // 100)
        self._machine.memory.write_byte(self._machine.registers.i + 1, (value // 10) % 10)
        self._machine.memory.write_byte(self._machine.registers.i + 2, value % 10)
        result.memory_range = (self._machine.registers.i, self._machine.registers.i + 2)
        return result

    def _execute_ld_i_vx(self, instruction: Instruction) -> StepResult:
        result = StepResult()
        for register in range(instruction.x + 1):
            self._machine.memory.write_byte( self._machine.registers.i + register, self._machine.registers[register])
        result.memory_range = (self._machine.registers.i, self._machine.registers.i + instruction.x)
        return result

    def _execute_ld_vx_i(self, instruction: Instruction) -> StepResult:
        for register in range(instruction.x + 1):
            self._machine.registers[register] = self._machine.memory.read_byte( self._machine.registers.i + register)
        return StepResult()


    ###############################################################################
    # Private format methods
    ###############################################################################
    def _format_sys(self, instruction: Instruction) -> str:
        raise ValueError(f"Opcode {instruction.opcode:04X} cannot be formatted.")

    def _format_cls(self, instruction: Instruction) -> str:
        return "CLS"

    def _format_ret(self, instruction: Instruction) -> str:
        return "RET"

    def _format_jp(self, instruction: Instruction) -> str:
        return f"JP {instruction.nnn:03X}"

    def _format_call(self, instruction: Instruction) -> str:
        return f"CALL {instruction.nnn:03X}"

    def _format_se_byte(self, instruction: Instruction) -> str:
        return f"SE V{instruction.x:X}, {instruction.nn:02X}"

    def _format_sne_byte(self, instruction: Instruction) -> str:
        return f"SNE V{instruction.x:X}, {instruction.nn:02X}"

    def _format_se_register(self, instruction: Instruction) -> str:
        if instruction.n == 0:
            return f"SE V{instruction.x:X}, V{instruction.y:X}"
        return f"DATA {instruction.opcode:04X}"

    def _format_ld_byte(self, instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, {instruction.nn:02X}"

    def _format_add_byte(self, instruction: Instruction) -> str:
        return f"ADD V{instruction.x:X}, {instruction.nn:02X}"

    def _format_ld_register(self, instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, V{instruction.y:X}"

    def _format_or(self, instruction: Instruction) -> str:
        return f"OR V{instruction.x:X}, V{instruction.y:X}"

    def _format_and(self, instruction: Instruction) -> str:
        return f"AND V{instruction.x:X}, V{instruction.y:X}"

    def _format_xor(self, instruction: Instruction) -> str:
        return f"XOR V{instruction.x:X}, V{instruction.y:X}"

    def _format_add_register(self, instruction: Instruction) -> str:
        return f"ADD V{instruction.x:X}, V{instruction.y:X}"

    def _format_sub(self, instruction: Instruction) -> str:
        return f"SUB V{instruction.x:X}, V{instruction.y:X}"

    def _format_shr(self, instruction: Instruction) -> str:
        return f"SHR V{instruction.x:X}"

    def _format_subn(self, instruction: Instruction) -> str:
        return f"SUBN V{instruction.x:X}, V{instruction.y:X}"

    def _format_shl(self, instruction: Instruction) -> str:
        return f"SHL V{instruction.x:X}"

    def _format_sne_register(self, instruction: Instruction) -> str:
        return f"DATA {instruction.opcode:04X}"

    def _format_ld_i(self, instruction: Instruction) -> str:
        return f"LD I, {instruction.nnn:03X}"

    def _format_jp_v0(self, instruction: Instruction) -> str:
        return f"JP V0, {instruction.nnn:03X}"

    def _format_rnd(self, instruction: Instruction) -> str:
        return f"RND V{instruction.x:X}, {instruction.nn:02X}"

    def _format_drw(self, instruction: Instruction) -> str:
        return f"DRW V{instruction.x:X}, V{instruction.y:X}, {instruction.n:X}"

    def _format_skp(self, instruction: Instruction) -> str:
        return f"SKP V{instruction.x:X}"

    def _format_sknp(self, instruction: Instruction) -> str:
        return f"SKNP V{instruction.x:X}"

    def _format_ld_vx_dt(self, instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, DT"

    def _format_ld_vx_k(self, instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, K"

    def _format_ld_dt_vx(self, instruction: Instruction) -> str:
        return f"LD DT, V{instruction.x:X}"

    def _format_ld_st_vx(self, instruction: Instruction) -> str:
        return f"LD ST, V{instruction.x:X}"

    def _format_add_i_vx(self, instruction: Instruction) -> str:
        return f"ADD I, V{instruction.x:X}"

    def _format_ld_f_vx(self, instruction: Instruction) -> str:
        return f"LD F, V{instruction.x:X}"

    def _format_ld_b_vx(self, instruction: Instruction) -> str:
        return f"LD B, V{instruction.x:X}"

    def _format_ld_i_vx(self, instruction: Instruction) -> str:
        return f"LD [I], V{instruction.x:X}"

    def _format_ld_vx_i(self, instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, [I]"

