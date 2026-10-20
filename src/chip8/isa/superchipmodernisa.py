"""Super-CHIP Modern instruction set architecture."""

from __future__ import annotations

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import InstructionExecutionContext
from chip8.isa.superchip11isa import SuperChip11InstructionSetArchitecture
from emulator.chip8framebuffer import SUPERCHIP_DISPLAY_HEIGHT, SUPERCHIP_DISPLAY_WIDTH
from emulator.constants import DISPLAY_HEIGHT, DISPLAY_WIDTH
from emulator.stepresult import StepResult


class SuperChipModernInstructionSetArchitecture(SuperChip11InstructionSetArchitecture):
    """Super-CHIP 1.1 opcodes with the Modern profile's behavior quirks."""

    def __init__(self) -> None:
        super().__init__()
        self._execute_handlers.update({
            InstructionId.SHR: self._execute_shr_modern,
            InstructionId.SHL: self._execute_shl_modern,
            InstructionId.LD_I_VX: self._execute_ld_i_vx_modern,
            InstructionId.LD_VX_I: self._execute_ld_vx_i_modern,
            InstructionId.DRW_16: self._execute_drw_16_modern,
            InstructionId.LOW_RES: self._execute_low_res_modern,
            InstructionId.HIGH_RES: self._execute_high_res_modern,
        })

    def _decode_id(self, opcode: int) -> InstructionId:
        """Decode user-flag transfers for all sixteen Modern registers."""
        if opcode & 0xF0FF == 0xF075:
            return InstructionId.LD_R_VX
        if opcode & 0xF0FF == 0xF085:
            return InstructionId.LD_VX_R
        return super()._decode_id(opcode)

    def create_assembler_instruction(
        self,
        mnemonic: str,
        operands: tuple[AssemblerOperand, ...],
    ) -> AssemblerInstruction:
        """Allow Modern user-flag transfers through VF."""
        if mnemonic.upper() == "LD" and len(operands) == 2:
            destination, source = operands
            if (
                destination.type is AssemblerOperandType.USER_FLAGS_REGISTER
                and source.type is AssemblerOperandType.REGISTER
            ):
                self._validate_register(source.value)
                return AssemblerInstruction(id=InstructionId.LD_R_VX, x=source.value)
            if (
                destination.type is AssemblerOperandType.REGISTER
                and source.type is AssemblerOperandType.USER_FLAGS_REGISTER
            ):
                self._validate_register(destination.value)
                return AssemblerInstruction(id=InstructionId.LD_VX_R, x=destination.value)
        return super().create_assembler_instruction(mnemonic, operands)

    def encode(self, instruction: AssemblerInstruction) -> int:
        """Encode Modern user-flag transfers for V0 through VF."""
        if instruction.id is InstructionId.LD_R_VX and instruction.x is not None:
            self._validate_register(instruction.x)
            return 0xF075 | (instruction.x << 8)
        if instruction.id is InstructionId.LD_VX_R and instruction.x is not None:
            self._validate_register(instruction.x)
            return 0xF085 | (instruction.x << 8)
        return super().encode(instruction)

    @staticmethod
    def _validate_register(value: int) -> None:
        if not 0 <= value <= 0xF:
            raise ValueError("Register must be in the range V0 to VF.")

    @staticmethod
    def _execute_shr_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Shift Vy right into Vx, storing the shifted-out bit in VF."""
        value = machine.registers[instruction.y]
        shifted_out = value & 0x01
        machine.registers[instruction.x] = value >> 1
        machine.registers[0xF] = shifted_out
        return StepResult()

    @staticmethod
    def _execute_shl_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Shift Vy left into Vx, storing the shifted-out bit in VF."""
        value = machine.registers[instruction.y]
        shifted_out = (value >> 7) & 0x01
        machine.registers[instruction.x] = (value << 1) & 0xFF
        machine.registers[0xF] = shifted_out
        return StepResult()

    @staticmethod
    def _execute_ld_i_vx_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Store V0 through Vx without changing I."""
        result = SuperChipModernInstructionSetArchitecture._store_registers(machine, instruction.x)
        return result

    @staticmethod
    def _execute_ld_vx_i_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Load V0 through Vx without changing I."""
        for register in range(instruction.x + 1):
            machine.registers[register] = machine.memory.read_byte(machine.registers.i + register)
        return StepResult()

    @staticmethod
    def _store_registers(
        machine: InstructionExecutionContext, last_register: int
    ) -> StepResult:
        result = StepResult()
        for register in range(last_register + 1):
            machine.memory.write_byte(machine.registers.i + register, machine.registers[register])
        result.memory_range = (machine.registers.i, machine.registers.i + last_register)
        return result

    @staticmethod
    def _execute_drw_16_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Draw a 16x16 sprite in both low- and high-resolution modes."""
        x = machine.registers[instruction.x]
        y = machine.registers[instruction.y]
        collision = False
        for row in range(16):
            sprite = (
                (machine.memory.read_byte(machine.registers.i + row * 2) << 8)
                | machine.memory.read_byte(machine.registers.i + row * 2 + 1)
            )
            for bit in range(16):
                if sprite & (0x8000 >> bit):
                    collision |= machine.framebuffer.xor_pixel(x + bit, y + row)
        machine.registers[0xF] = 1 if collision else 0
        return StepResult(display_changed=True)

    @staticmethod
    def _execute_low_res_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        machine.framebuffer.set_resolution(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        machine.framebuffer.clear()
        return StepResult(display_changed=True)

    @staticmethod
    def _execute_high_res_modern(
        machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        machine.framebuffer.set_resolution(SUPERCHIP_DISPLAY_WIDTH, SUPERCHIP_DISPLAY_HEIGHT)
        machine.framebuffer.clear()
        return StepResult(display_changed=True)
