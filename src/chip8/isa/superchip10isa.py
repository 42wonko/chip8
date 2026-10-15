"""
@file superchip10isa.py

@brief Super-CHIP 1.0 instruction set architecture.

Super-CHIP extends Classic CHIP-8. This implementation deliberately inherits
Classic decoding, execution, formatting, and analysis for instructions whose
semantics are shared, overriding only the additional instruction encodings
and handlers.
"""

from __future__ import annotations

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import ControlFlow, InstructionAnalysis, InstructionExecutionContext
from chip8.isa.reference import InstructionReference, ReferenceAccess
from emulator.chip8framebuffer import SUPERCHIP_DISPLAY_HEIGHT, SUPERCHIP_DISPLAY_WIDTH
from emulator.constants import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    INSTRUCTION_SIZE,
    NIBBLE_MASK,
    SUPERCHIP_FONT_CHARACTER_SIZE,
    SUPERCHIP_FONT_START,
    SUPERCHIP_FONTSET,
)
from emulator.stepresult import StepResult


class SuperChip10InstructionSetArchitecture(ClassicInstructionSetArchitecture):
    """Classic CHIP-8 ISA extended with Super-CHIP 1.0 instructions."""

    def __init__(self) -> None:
        super().__init__()
        self._reference_handlers.update({
            InstructionId.LOW_RES: self._references_none,
            InstructionId.HIGH_RES: self._references_none,
            InstructionId.EXIT: self._references_none,
            InstructionId.DRW_16: self._references_drw,
        })
        self._execute_handlers.update({
            InstructionId.LOW_RES: self._execute_low_res,
            InstructionId.HIGH_RES: self._execute_high_res,
            InstructionId.EXIT: self._execute_exit,
            InstructionId.DRW_16: self._execute_drw_16,
            InstructionId.LD_HF_VX: self._execute_ld_hf_vx,
            InstructionId.LD_R_VX: self._execute_ld_r_vx,
            InstructionId.LD_VX_R: self._execute_ld_vx_r,
            InstructionId.LD_I_VX: self._execute_ld_i_vx,
            InstructionId.LD_VX_I: self._execute_ld_vx_i,
            InstructionId.JP_V0: self._execute_jp_vx,
        })
        self._format_handlers.update({
            InstructionId.LOW_RES: self._format_low_res,
            InstructionId.HIGH_RES: self._format_high_res,
            InstructionId.EXIT: self._format_exit,
            InstructionId.DRW_16: self._format_drw_16,
            InstructionId.LD_HF_VX: self._format_ld_hf_vx,
            InstructionId.LD_R_VX: self._format_ld_r_vx,
            InstructionId.LD_VX_R: self._format_ld_vx_r,
            InstructionId.JP_V0: self._format_jp_vx,
            InstructionId.UNKNOWN: self._format_unknown,
        })

    def assembler_mnemonics(self) -> frozenset[str]:
        """Return Classic mnemonics plus Super-CHIP 1.0 additions."""
        return super().assembler_mnemonics() | frozenset({"LOW", "HIGH", "EXIT"})

    def create_assembler_instruction(
        self,
        mnemonic: str,
        operands: tuple[AssemblerOperand, ...],
    ) -> AssemblerInstruction:
        """Create a Super-CHIP 1.0 instruction or delegate to Classic."""
        name = mnemonic.upper()
        simple_instructions = {
            "LOW": InstructionId.LOW_RES,
            "HIGH": InstructionId.HIGH_RES,
            "EXIT": InstructionId.EXIT,
        }
        if name in simple_instructions:
            if operands:
                raise ValueError(f"{name} does not accept operands.")
            return AssemblerInstruction(id=simple_instructions[name])
        if name == "LD" and len(operands) == 2:
            destination, source = operands
            if destination.type is AssemblerOperandType.HIGH_FONT_REGISTER and source.type is AssemblerOperandType.REGISTER:
                self._validate_register(source.value)
                return AssemblerInstruction(id=InstructionId.LD_HF_VX, x=source.value)
            if destination.type is AssemblerOperandType.USER_FLAGS_REGISTER and source.type is AssemblerOperandType.REGISTER:
                self._validate_user_flags_register(source.value)
                return AssemblerInstruction(id=InstructionId.LD_R_VX, x=source.value)
            if destination.type is AssemblerOperandType.REGISTER and source.type is AssemblerOperandType.USER_FLAGS_REGISTER:
                self._validate_user_flags_register(destination.value)
                return AssemblerInstruction(id=InstructionId.LD_VX_R, x=destination.value)
        if name == "DRW" and len(operands) == 3:
            x, y, height = operands
            if (
                x.type is AssemblerOperandType.REGISTER
                and y.type is AssemblerOperandType.REGISTER
                and height.type is AssemblerOperandType.VALUE
                and height.value == 0
            ):
                self._validate_register(x.value)
                self._validate_register(y.value)
                return AssemblerInstruction(
                    id=InstructionId.DRW_16, x=x.value, y=y.value, n=0
                )
        if name == "JP" and len(operands) == 2:
            register, offset = operands
            if register.type is not AssemblerOperandType.REGISTER:
                raise ValueError("Super-CHIP JP requires a register as the first operand.")
            if offset.type is not AssemblerOperandType.VALUE:
                raise ValueError("Super-CHIP JP requires an 8-bit value as the second operand.")
            if not 0 <= register.value <= 0xF:
                raise ValueError("Register must be in the range V0 to VF.")
            if not 0 <= offset.value <= 0xFF:
                raise ValueError("Super-CHIP JP offset must be in the range 0x00 to 0xFF.")
            return AssemblerInstruction(id=InstructionId.JP_V0, x=register.value, nn=offset.value)
        return super().create_assembler_instruction(name, operands)

    def assembler_operand_signatures(
        self,
        mnemonic: str,
        operand_count: int,
    ) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        """Return valid operand signatures for Super-CHIP mnemonics."""
        name = mnemonic.upper()
        if name in {"LOW", "HIGH", "EXIT"}:
            return ((),) if operand_count == 0 else ()
        if name == "JP" and operand_count == 2:
            return ((AssemblerOperandType.REGISTER, AssemblerOperandType.VALUE),)
        if name == "LD":
            signatures = super().assembler_operand_signatures(name, operand_count)
            if operand_count == 2:
                signatures += (
                    (AssemblerOperandType.HIGH_FONT_REGISTER, AssemblerOperandType.REGISTER),
                    (AssemblerOperandType.USER_FLAGS_REGISTER, AssemblerOperandType.REGISTER),
                    (AssemblerOperandType.REGISTER, AssemblerOperandType.USER_FLAGS_REGISTER),
                )
            return signatures
        return super().assembler_operand_signatures(name, operand_count)

    def assembler_instruction_size(self, mnemonic: str, operand_count: int) -> int:
        """Return the encoded size for valid Super-CHIP or Classic instructions."""
        name = mnemonic.upper()
        if name in {"LOW", "HIGH", "EXIT"}:
            return INSTRUCTION_SIZE if operand_count == 0 else 0
        if name == "JP" and operand_count == 2:
            return INSTRUCTION_SIZE
        if name == "LD" and any(
            signature[0] in (AssemblerOperandType.HIGH_FONT_REGISTER, AssemblerOperandType.USER_FLAGS_REGISTER)
            or signature[1] is AssemblerOperandType.USER_FLAGS_REGISTER
            for signature in self.assembler_operand_signatures(name, operand_count)
            if len(signature) == 2
        ):
            return INSTRUCTION_SIZE
        return super().assembler_instruction_size(name, operand_count)

    def assembler_operand(self, name: str) -> AssemblerOperand | None:
        """Resolve Super-CHIP-specific special operand names."""
        special_operands = {
            "HF": AssemblerOperandType.HIGH_FONT_REGISTER,
            "R": AssemblerOperandType.USER_FLAGS_REGISTER,
        }
        operand_type = special_operands.get(name.upper())
        if operand_type is not None:
            return AssemblerOperand(type=operand_type, value=0)
        return super().assembler_operand(name)

    @staticmethod
    def _validate_register(value: int) -> None:
        if not 0 <= value <= 0xF:
            raise ValueError("Register must be in the range V0 to VF.")

    @staticmethod
    def _validate_user_flags_register(value: int) -> None:
        if not 0 <= value <= 7:
            raise ValueError("Super-CHIP user flags support registers V0 through V7.")

    def encode(self, instruction: AssemblerInstruction) -> int:
        """Encode Super-CHIP 1.0-only instructions; preserve Classic encoding."""
        match instruction.id:
            case InstructionId.LOW_RES:
                return 0x00FE
            case InstructionId.HIGH_RES:
                return 0x00FF
            case InstructionId.EXIT:
                return 0x00FD
            case InstructionId.LD_HF_VX if instruction.x is not None:
                self._validate_register(instruction.x)
                return 0xF030 | (instruction.x << 8)
            case InstructionId.LD_R_VX if instruction.x is not None:
                self._validate_user_flags_register(instruction.x)
                return 0xF075 | (instruction.x << 8)
            case InstructionId.LD_VX_R if instruction.x is not None:
                self._validate_user_flags_register(instruction.x)
                return 0xF085 | (instruction.x << 8)
            case InstructionId.JP_V0 if instruction.x is not None and instruction.nn is not None:
                if not 0 <= instruction.x <= 0xF or not 0 <= instruction.nn <= 0xFF:
                    raise ValueError("Super-CHIP JP operands are outside their encoding ranges.")
                return 0xB000 | (instruction.x << 8) | instruction.nn
            case InstructionId.DRW_16 if instruction.x is not None and instruction.y is not None:
                self._validate_register(instruction.x)
                self._validate_register(instruction.y)
                return 0xD000 | (instruction.x << 8) | (instruction.y << 4)
        return super().encode(instruction)

    def instruction_references(
        self,
        instruction: AssemblerInstruction,
    ) -> tuple[InstructionReference, ...]:
        """Analyze references for Super-CHIP's register-offset jump."""
        is_register_offset_jump = (
            instruction.id is InstructionId.JP_V0
            and instruction.x is not None
            and instruction.nn is not None
        )
        if instruction.id in (InstructionId.LD_HF_VX, InstructionId.LD_R_VX) and instruction.x is not None:
            return (InstructionReference(resource=f"V{instruction.x:X}", access=ReferenceAccess.READ),)
        if instruction.id is InstructionId.LD_VX_R and instruction.x is not None:
            return (InstructionReference(resource=f"V{instruction.x:X}", access=ReferenceAccess.WRITE),)
        if is_register_offset_jump:
            return (
                InstructionReference(
                    resource=f"V{instruction.x:X}",
                    access=ReferenceAccess.READ,
                ),
            )
        return super().instruction_references(instruction)

    def initialize_machine(self, machine: InstructionExecutionContext) -> None:
        """Install the Super-CHIP large hexadecimal font in memory."""
        for offset, value in enumerate(SUPERCHIP_FONTSET):
            machine.memory.write_byte(SUPERCHIP_FONT_START + offset, value)

    def _decode_id(self, opcode: int) -> InstructionId:
        """Decode Super-CHIP 1.0 opcodes before falling back to Classic."""
        match opcode:
            case 0x00FD:
                return InstructionId.EXIT
            case 0x00FE:
                return InstructionId.LOW_RES
            case 0x00FF:
                return InstructionId.HIGH_RES

        # These encodings are reserved for extensions introduced after
        # Super-CHIP 1.0. Do not let Classic's broad 0NNN SYS fallback
        # classify them as valid instructions in this profile.
        if opcode & 0xFFF0 == 0x00C0 or opcode in (0x00FB, 0x00FC):
            return InstructionId.UNKNOWN

        if opcode & 0xF00F == 0xD000:
            return InstructionId.DRW_16

        if opcode & 0xF0FF == 0xF030:
            return InstructionId.LD_HF_VX

        if opcode & 0xF0FF == 0xF075:
            return InstructionId.LD_R_VX if ((opcode >> 8) & NIBBLE_MASK) <= 7 else InstructionId.UNKNOWN

        if opcode & 0xF0FF == 0xF085:
            return InstructionId.LD_VX_R if ((opcode >> 8) & NIBBLE_MASK) <= 7 else InstructionId.UNKNOWN

        return super()._decode_id(opcode)

    def _execute_exit(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        """Stop execution when the Super-CHIP EXIT instruction is executed."""
        return StepResult(terminated=True)

    def _execute_low_res(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        machine.framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        return StepResult(display_changed=True)

    def _execute_high_res(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        machine.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        return StepResult(display_changed=True)

    def _execute_drw_16(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        result = StepResult(display_changed=True)
        x = machine.registers[instruction.x]
        y = machine.registers[instruction.y]
        collision = False

        # Super-CHIP 1.x draws an 8x16 sprite in low-resolution mode and
        # a 16x16 sprite in high-resolution mode.
        if machine.framebuffer.width == DISPLAY_WIDTH:
            for row in range(16):
                sprite = machine.memory.read_byte(machine.registers.i + row)
                for bit in range(8):
                    if sprite & (0x80 >> bit):
                        collision |= machine.framebuffer.xor_pixel(x + bit, y + row)
        else:
            for row in range(16):
                sprite = (machine.memory.read_byte(machine.registers.i + row * 2) << 8) | machine.memory.read_byte(machine.registers.i + row * 2 + 1)
                for bit in range(16):
                    if sprite & (0x8000 >> bit):
                        collision |= machine.framebuffer.xor_pixel(x + bit, y + row)

        machine.registers[0xF] = 1 if collision else 0
        return result

    def _execute_jp_vx(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        """Jump to XNN plus VX, as defined by Super-CHIP 1.0."""
        machine.registers.pc = instruction.nn + machine.registers[instruction.x]
        return StepResult()

    def _execute_ld_i_vx(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        result = super()._execute_ld_i_vx(machine, instruction)
        machine.registers.i += instruction.x
        return result

    def _execute_ld_vx_i(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        result = super()._execute_ld_vx_i(machine, instruction)
        machine.registers.i += instruction.x
        return result

    def _execute_ld_hf_vx(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        digit = machine.registers[instruction.x] & NIBBLE_MASK
        machine.registers.i = SUPERCHIP_FONT_START + digit * SUPERCHIP_FONT_CHARACTER_SIZE
        return StepResult()

    def _execute_ld_r_vx(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        for register in range(instruction.x + 1):
            machine.user_flags[register] = machine.registers[register]
        return StepResult()

    def _execute_ld_vx_r(self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        for register in range(instruction.x + 1):
            machine.registers[register] = machine.user_flags[register]
        return StepResult()

    @staticmethod
    def _format_jp_vx(instruction: Instruction) -> str:
        return f"JP V{instruction.x:X}, {instruction.nn:02X}"

    def analyze(self, instruction: Instruction) -> InstructionAnalysis:
        """Report EXIT as a terminal instruction to debugger analysis."""
        if instruction.id is InstructionId.EXIT:
            return InstructionAnalysis(control_flow=ControlFlow.TERMINATE, targets=(), is_code=True)
        return super().analyze(instruction)

    @staticmethod
    def _format_unknown(instruction: Instruction) -> str:
        """Format an unsupported opcode without breaking code listings."""
        return f"UNKNOWN {instruction.opcode:04X}"

    @staticmethod
    def _format_exit(instruction: Instruction) -> str:
        return "EXIT"

    @staticmethod
    def _format_low_res(instruction: Instruction) -> str:
        return "LOW"

    @staticmethod
    def _format_high_res(instruction: Instruction) -> str:
        return "HIGH"

    @staticmethod
    def _format_drw_16(instruction: Instruction) -> str:
        return f"DRW V{instruction.x:X}, V{instruction.y:X}, 0"

    @staticmethod
    def _format_ld_hf_vx(instruction: Instruction) -> str:
        return f"LD HF, V{instruction.x:X}"

    @staticmethod
    def _format_ld_r_vx(instruction: Instruction) -> str:
        return f"LD R, V{instruction.x:X}"

    @staticmethod
    def _format_ld_vx_r(instruction: Instruction) -> str:
        return f"LD V{instruction.x:X}, R"
