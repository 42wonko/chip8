"""SCHIPC (HP48 Super-CHIP) instruction set architecture."""

from __future__ import annotations

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import InstructionExecutionContext
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from chip8.isa.superchip11isa import SuperChip11InstructionSetArchitecture
from emulator.stepresult import StepResult


class SCHIPCInstructionSetArchitecture(SuperChip11InstructionSetArchitecture):
    """Super-CHIP 1.1 instructions with the HP48 SCHIPC compatibility quirks."""

    def __init__(self) -> None:
        super().__init__()
        # SCHIPC uses the original Bnnn jump-to-V0 behavior, not Bxnn.
        self._execute_handlers[InstructionId.JP_V0] = self._execute_jp_v0
        # The row-count VF quirk belongs to Super-CHIP 1.1, not the HP48.
        self._execute_handlers[InstructionId.DRW_16] = self._execute_drw_16
        self._format_handlers[InstructionId.JP_V0] = self._format_jp_v0

    def _decode_id(self, opcode: int) -> InstructionId:
        """Reject the HP48-invalid zero-distance scroll instruction."""
        if opcode == 0x00C0:
            return InstructionId.UNKNOWN
        return super()._decode_id(opcode)

    def assembler_mnemonics(self) -> frozenset[str]:
        return super().assembler_mnemonics() | frozenset({"JP"})

    def create_assembler_instruction( self, mnemonic: str, operands: tuple[AssemblerOperand, ...],) -> AssemblerInstruction:
        name = mnemonic.upper()
        if name == "SCD" and len(operands) == 1:
            if operands[0].type is not AssemblerOperandType.VALUE:
                raise ValueError("SCD requires one numeric row count from 1 to 15.")
            if not 1 <= operands[0].value <= 0xF:
                raise ValueError("SCHIPC SCD row count must be in the range 1 to 15.")
        if name == "JP" and len(operands) == 2:
            register, address = operands
            if ( register.type is AssemblerOperandType.REGISTER and address.type is AssemblerOperandType.ADDRESS):
                if register.value != 0:
                    raise ValueError("SCHIPC JP offset form requires V0 as the first operand.")
                if not 0 <= address.value <= 0xFFF:
                    raise ValueError("JP address must be in the range 0x000 to 0xFFF.")
                return AssemblerInstruction(id=InstructionId.JP_V0, nnn=address.value)
        return super().create_assembler_instruction(name, operands)

    def assembler_operand_signatures( self, mnemonic: str, operand_count: int,) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        if mnemonic.upper() == "JP" and operand_count == 2:
            return ((AssemblerOperandType.REGISTER, AssemblerOperandType.ADDRESS),)
        if mnemonic.upper() == "SCD" and operand_count == 1:
            return ((AssemblerOperandType.VALUE,),)
        return super().assembler_operand_signatures(mnemonic, operand_count)

    def assembler_instruction_size(self, mnemonic: str, operand_count: int) -> int:
        if mnemonic.upper() == "JP" and operand_count == 2:
            return 2
        return super().assembler_instruction_size(mnemonic, operand_count)

    def _execute_drw_16( self, machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        """Use HP48 collision-flag behavior for 16-row sprites."""
        return SuperChip10InstructionSetArchitecture._execute_drw_16( self, machine, instruction)

    @staticmethod
    def _execute_jp_v0( machine: InstructionExecutionContext, instruction: Instruction) -> StepResult:
        """Jump to NNN plus V0, as on the original CHIP-8 architecture."""
        machine.registers.pc = instruction.nnn + machine.registers[0]
        return StepResult()


