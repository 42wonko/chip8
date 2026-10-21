"""Super-CHIP 1.1 instruction set architecture."""

from __future__ import annotations

from assembler.instruction import AssemblerInstruction
from assembler.operand import AssemblerOperand, AssemblerOperandType
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from chip8.isa.isa import InstructionExecutionContext
from chip8.isa.superchip10isa import SuperChip10InstructionSetArchitecture
from emulator.constants import DISPLAY_WIDTH
from emulator.stepresult import StepResult


class SuperChip11InstructionSetArchitecture(SuperChip10InstructionSetArchitecture):
    """Super-CHIP 1.0 extended with Super-CHIP 1.1 scrolling opcodes."""

    def __init__(self) -> None:
        super().__init__()
        self._reference_handlers.update({
            InstructionId.SCROLL_DOWN: self._references_none,
            InstructionId.SCROLL_RIGHT: self._references_none,
            InstructionId.SCROLL_LEFT: self._references_none,
        })
        self._execute_handlers.update({
            InstructionId.SCROLL_DOWN: self._execute_scroll_down,
            InstructionId.SCROLL_RIGHT: self._execute_scroll_right,
            InstructionId.SCROLL_LEFT: self._execute_scroll_left,
        })
        self._format_handlers.update({
            InstructionId.SCROLL_DOWN: self._format_scroll_down,
            InstructionId.SCROLL_RIGHT: self._format_scroll_right,
            InstructionId.SCROLL_LEFT: self._format_scroll_left,
        })

    def assembler_mnemonics(self) -> frozenset[str]:
        """Return Super-CHIP 1.0 mnemonics plus Super-CHIP 1.1 scrolling."""
        return super().assembler_mnemonics() | frozenset({"SCD", "SCR", "SCL"})

    def create_assembler_instruction(
        self,
        mnemonic: str,
        operands: tuple[AssemblerOperand, ...],
    ) -> AssemblerInstruction:
        """Create Super-CHIP 1.1 scrolling instructions or delegate to 1.0."""
        name = mnemonic.upper()
        if name in {"SCR", "SCL"}:
            if operands:
                raise ValueError(f"{name} does not accept operands.")
            instruction_id = (
                InstructionId.SCROLL_RIGHT if name == "SCR" else InstructionId.SCROLL_LEFT
            )
            return AssemblerInstruction(id=instruction_id)
        if name == "SCD":
            if len(operands) != 1 or operands[0].type is not AssemblerOperandType.VALUE:
                raise ValueError("SCD requires one numeric row count from 0 to 15.")
            rows = operands[0].value
            if not 0 <= rows <= 0xF:
                raise ValueError("SCD row count must be in the range 0 to 15.")
            return AssemblerInstruction(id=InstructionId.SCROLL_DOWN, n=rows)
        return super().create_assembler_instruction(name, operands)

    def assembler_operand_signatures(
        self,
        mnemonic: str,
        operand_count: int,
    ) -> tuple[tuple[AssemblerOperandType, ...], ...]:
        """Describe valid operand types for Super-CHIP 1.1 scrolling."""
        name = mnemonic.upper()
        if name in {"SCR", "SCL"}:
            return ((),) if operand_count == 0 else ()
        if name == "SCD":
            return ((AssemblerOperandType.VALUE,),) if operand_count == 1 else ()
        return super().assembler_operand_signatures(name, operand_count)

    def assembler_instruction_size(self, mnemonic: str, operand_count: int) -> int:
        """Return the encoded size of valid scrolling instructions."""
        name = mnemonic.upper()
        if name in {"SCR", "SCL"}:
            return 2 if operand_count == 0 else 0
        if name == "SCD":
            return 2 if operand_count == 1 else 0
        return super().assembler_instruction_size(mnemonic, operand_count)

    def encode(self, instruction: AssemblerInstruction) -> int:
        """Encode scrolling opcodes introduced by Super-CHIP 1.1."""
        if instruction.id is InstructionId.SCROLL_DOWN and instruction.n is not None:
            if not 0 <= instruction.n <= 0xF:
                raise ValueError("SCD row count must be in the range 0 to 15.")
            return 0x00C0 | instruction.n
        if instruction.id is InstructionId.SCROLL_RIGHT:
            return 0x00FB
        if instruction.id is InstructionId.SCROLL_LEFT:
            return 0x00FC
        return super().encode(instruction)

    def _decode_id(self, opcode: int) -> InstructionId:
        """Decode scrolling opcodes introduced in Super-CHIP 1.1."""
        if opcode & 0xFFF0 == 0x00C0:
            return InstructionId.SCROLL_DOWN
        if opcode == 0x00FB:
            return InstructionId.SCROLL_RIGHT
        if opcode == 0x00FC:
            return InstructionId.SCROLL_LEFT
        return super()._decode_id(opcode)

    def _execute_drw_16(
        self, machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        """Draw a Super-CHIP 1.1 sprite, preserving its high-res VF quirk."""
        if machine.framebuffer.width == DISPLAY_WIDTH:
            return super()._execute_drw_16(machine, instruction)

        x = machine.registers[instruction.x]
        y = machine.registers[instruction.y]
        collision_rows = 0
        clipped_rows = 0

        for row in range(16):
            row_y = y + row
            if row_y >= machine.framebuffer.height:
                clipped_rows += 1
                continue

            sprite = (
                (machine.memory.read_byte(machine.registers.i + row * 2) << 8)
                | machine.memory.read_byte(machine.registers.i + row * 2 + 1)
            )
            row_collision = False
            for bit in range(16):
                if sprite & (0x8000 >> bit):
                    row_collision |= machine.framebuffer.xor_pixel(x + bit, row_y)
            if row_collision:
                collision_rows += 1

        machine.registers[0xF] = collision_rows + clipped_rows
        return StepResult(display_changed=True)

    def _execute_scroll_down(
        self, machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        # Recreate the original Super-CHIP 1.x lo-res behavior: scroll
        # distances are specified in backing-buffer pixels, while the active
        # lo-res display uses half that resolution. Integer division is
        # intentional; SCD 1 therefore produces no visible lo-res movement.
        rows = instruction.n
        if machine.framebuffer.width == DISPLAY_WIDTH:
            rows //= 2
        machine.framebuffer.scroll_down(rows)
        return StepResult(display_changed=True)

    def _execute_scroll_right(
        self, machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        # SCR shifts four backing-buffer pixels, i.e. two logical lo-res
        # pixels. Keep the full four-pixel distance in high-resolution mode.
        columns = 2 if machine.framebuffer.width == DISPLAY_WIDTH else 4
        machine.framebuffer.scroll_right(columns)
        return StepResult(display_changed=True)

    def _execute_scroll_left(
        self, machine: InstructionExecutionContext, instruction: Instruction
    ) -> StepResult:
        # SCL uses the same resolution-dependent distance as SCR.
        columns = 2 if machine.framebuffer.width == DISPLAY_WIDTH else 4
        machine.framebuffer.scroll_left(columns)
        return StepResult(display_changed=True)

    @staticmethod
    def _format_scroll_down(instruction: Instruction) -> str:
        return f"SCD {instruction.n:X}"

    @staticmethod
    def _format_scroll_right(instruction: Instruction) -> str:
        return "SCR"

    @staticmethod
    def _format_scroll_left(instruction: Instruction) -> str:
        return "SCL"
