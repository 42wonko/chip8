"""
@file codeanalysis.py

@brief Code Analysis subsystem.

@details
Maintains the interpreted representation of CHIP-8 program memory for
the Code View.


@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum

from controller.applicationlogreporter import ApplicationLogReporter
from controller.diagnostics import DiagnosticReporter
from emulator.chip8memory import Chip8Memory
from emulator.constants import CHIP8_STACK_SIZE, PROGRAM_START
from emulator.instruction import Instruction


class CodeStatus(StrEnum):
    """
    @brief Classification of a Code View entry.
    """

    UNKNOWN = "Unknown"
    CODE = "Code"
    DATA = "Data"


@dataclass(frozen=True, slots=True)
class CodeRow:
    """
    @brief One row displayed by the Code View.

    Derived from the number of raw bytes represented by this row.
    """

    address: int
    raw_bytes: bytes
    interpretation: str
    status: CodeStatus

    @property
    def length(self) -> int:
        """
        @brief Length of the represented memory region.
        """
        return len(self.raw_bytes)


@dataclass(frozen=True, slots=True)
class CallFrame:
    """
    @brief One simulated CHIP-8 call frame.

    @details
    Represents one active subroutine invocation during static analysis.

    The frame stores both the callee address and the return address.
    """
    callee: int
    return_address: int


@dataclass(frozen=True, slots=True)
class WorkItem:
    """
    @brief Analysis work item.

    @details
    Represents one analysis state processed by the worklist algorithm.

    Besides the current instruction address, the analysis state carries
    the simulated call stack. This allows future phases to distinguish
    identical program addresses reached with different return paths.
    """
    address: int
    # Simulated CHIP-8 call stack.
    # Every frame stores the active subroutine together with its return address.
    # The tuple is immutable so WorkItem remains hashable.
    call_stack: tuple[CallFrame, ...] = ()


class CodeAnalysis:
    """
    @brief Maintains the interpreted Code View.
    """
    def __init__(self, memory: Chip8Memory, diagnostics: DiagnosticReporter, logger: ApplicationLogReporter) -> None:
        """
        @brief Construct the Code Analysis subsystem.

        @param memory
            Emulator memory.
        """
        self._diagnostics = diagnostics             # connect ourself to the Diagnostics manager in the controller
        self._logger = logger
        self._memory = memory
        self._rows: list[CodeRow] = []

        self._status: list[CodeStatus] = []         # Classification for every memory byte.

        # Instructions discovered by analysis.
        # Key:
        #     Start address.
        # Value:
        #     Decoded instruction.
        self._instructions: dict[int, Instruction] = {}

        # Runtime-observed targets of BNNN instructions.
        # Key:
        #     Address of the BNNN instruction.
        # Value:
        #     Set of observed jump targets.
        self._observed_bnnn_targets: dict[int, set[int]] = {}

        # Address range occupied by the currently loaded ROM.
        # An empty range indicates that no ROM is loaded.
        self._rom_start = PROGRAM_START
        self._rom_end = PROGRAM_START
        self._address_to_row: dict[int, int] = {}


    def set_rom_range(self, start: int, end: int) -> None:
        """
        @brief Set the address range occupied by the loaded ROM.

        @param start
            First ROM address.

        @param end
            First address beyond the ROM.
        """
        if start > end:
            raise ValueError("Invalid ROM range.")
        self._rom_start = start
        self._rom_end = end


    def rebuild(self) -> None:
        """
        @brief Rebuild the complete analysis.
        """
        self._logger.enter("rebuild")
        self._logger.info("Starting code analysis.")
        self._instructions.clear()
        self._address_to_row.clear()
        self._initialize_status()
        self._analyze()
        self._build_rows()
        self._logger.info("Code analysis completed.")
        self._logger.leave("rebuild")

    def observe_bnnn_target( self, instruction_address: int, target: int) -> bool:
        """
        @brief Record an observed BNNN jump target.

        @param instruction_address
            Address of the executed BNNN instruction.

        @param target
            Runtime jump target.

        @return
            True if this target was observed for the first time.
        """
        targets = self._observed_bnnn_targets.setdefault( instruction_address, set())
        if target in targets:
            return False
        targets.add(target)
        self._logger.info( f"BNNN discovered new target {target:03X} from {instruction_address:03X}.")
        return True


    def clear_runtime_observations(self) -> None:
        """
        @brief Forget all runtime-assisted analysis information.
        """
        self._observed_bnnn_targets.clear()


    def observed_bnnn_targets( self, instruction_address: int) -> set[int]:
        """
        @brief Return all observed targets of one BNNN instruction.
        """
        return self._observed_bnnn_targets.get( instruction_address, set())


    def _initialize_status(self) -> None:
        """
        @brief Initialize the byte classification.

        Bytes inside the ROM are initially UNKNOWN.
        Everything else is DATA.
        """
        self._status = []

        for address in range(self._memory.size()):
            if self._rom_start <= address < self._rom_end:
                self._status.append(CodeStatus.UNKNOWN)
            else:
                self._status.append(CodeStatus.DATA)


    def _get_word(self, address: int) -> int | None:
        """
        @brief Read a 16-bit word from memory.

        @param address
            Address of the first byte.

        @return
            The 16-bit big-endian value or None if the word extends beyond
            memory.
        """
        if address < 0:
            return None
        if address + 1 >= self._memory.size():
            return None
        return (self._memory[address] << 8) | self._memory[address + 1]

    def _decode_instruction(self, address: int) -> Instruction | None:
        """
        @brief Decode the instruction at the specified address.

        @param address
            Instruction address.

        @return
            The decoded instruction or None if the instruction extends
            beyond memory.
        """
        opcode = self._get_word(address)
        if opcode is None:
            return None
        return Instruction.decode(address, opcode)


    def analyze_observed_bnnn_target( self, instruction_address: int, target: int) -> bool:
        """
        @brief Analyze a newly observed BNNN jump target.

        @param instruction_address
            Address of the executed BNNN instruction.

        @param target
            Runtime jump destination.

        @return
            True if a previously unknown target was discovered.
        """
        if not self.observe_bnnn_target( instruction_address, target):
            return False
        self.rebuild()
        return True


    def _analyze(self) -> None:
        """
        @brief Perform control-flow analysis.

        @details
        Starting at the program entry point, performs a conservative
        worklist-based traversal to discover executable instructions.

        Previously observed BNNN runtime targets are treated as additional
        analysis entry points.
        """
        self._instructions.clear()
        worklist: deque[WorkItem] = deque()
        visited: set[WorkItem] = set()
        worklist.append(WorkItem(PROGRAM_START))                # Primary program entry point.

        for targets in self._observed_bnnn_targets.values():    # Previously observed runtime targets of BNNN instructions.
            for target in targets:
                worklist.append(WorkItem(target))
        while worklist:
            work = worklist.pop()
            if len(work.call_stack) > CHIP8_STACK_SIZE:
                self._diagnostics.warning( "Maximum CHIP-8 call stack depth exceeded during static analysis." , work.address)
                continue
            if work in visited:
                continue
            visited.add(work)
            address = work.address
            if not (self._rom_start <= address < self._rom_end):
                continue
            instruction = self._decode_instruction(address)
            if instruction is None:
                continue
            self._instructions[address] = instruction
            self._status[address] = CodeStatus.CODE             # Mark the occupied bytes as executable.
            if address + 1 < self._rom_end:
                self._status[address + 1] = CodeStatus.CODE
            successors = self._successors(work, instruction)
            if successors is None:
                self._status[address] = CodeStatus.DATA
                continue
            self._status[address] = CodeStatus.CODE
            for successor in successors:
                if len(successor.call_stack) > CHIP8_STACK_SIZE:
                    self._diagnostics.warning("Maximum CHIP-8 stack depth exceeded.", instruction.address )
                if successor not in visited:
                    worklist.append(successor)


    def _successors( self, work: WorkItem, instruction: Instruction,) -> list[WorkItem] | None:
        """
        @brief Determine successor analysis states.

        @param work
            Current analysis state.

        @param instruction
            Decoded instruction.

        @return
            List of successor work items for valid CHIP-8 instructions,
            an empty list for instructions with no statically known
            successors, or None for invalid instruction encodings.
        """
        #
        # Instructions identified by their complete opcode.
        #
        match instruction.opcode:
            case 0x00EE:      # RET
                if not work.call_stack:
                    return []
                frame = work.call_stack[-1]
                return [WorkItem(frame.return_address, work.call_stack[:-1])]

        #
        # Instructions identified by opcode family.
        #
        match instruction.family:
            case 0x1:         # JP addr
                return [
                    WorkItem(
                        instruction.nnn,
                        work.call_stack,
                    )
                ]

            case 0x2:         # CALL addr
                if any( frame.callee == instruction.nnn for frame in work.call_stack):
                    self._diagnostics.warning( "Potential recursive CALL path detected; analysis terminated this path." , instruction.address)
                    return []
                return [ WorkItem( instruction.nnn, work.call_stack + ( CallFrame( callee=instruction.nnn , return_address=instruction.address + 2),)) ]

            case 0x3:         # SE Vx, byte
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    ),
                    WorkItem(
                        instruction.address + 4,
                        work.call_stack,
                    ),
                ]

            case 0x4:         # SNE Vx, byte
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    ),
                    WorkItem(
                        instruction.address + 4,
                        work.call_stack,
                    ),
                ]

            case 0x5:         # SE Vx, Vy
                if instruction.n != 0:
                    return None
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    ),
                    WorkItem(
                        instruction.address + 4,
                        work.call_stack,
                    ),
                ]

            case 0x8:         # SE Vx, Vy
                if instruction.n in (8,9,0xA,0xB,0xC,0xD,0xF):
                    return None
                return [ WorkItem( instruction.address + 2, work.call_stack,) ]

            case 0x9:         # SNE Vx, Vy
                if instruction.n != 0:
                    return None
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    ),
                    WorkItem(
                        instruction.address + 4,
                        work.call_stack,
                    ),
                ]

            case 0xB:         # JP V0, addr
                #
                # Conservative for now.
                #
                return []

            case 0xE:         # SKP / SKNP
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    ),
                    WorkItem(
                        instruction.address + 4,
                        work.call_stack,
                    ),
                ]

            case _:
                return [
                    WorkItem(
                        instruction.address + 2,
                        work.call_stack,
                    )
                ]


    def _build_rows(self) -> None:
        """
        @brief Build the immutable CodeRow list.
        """
        rows: list[CodeRow] = []
        self._address_to_row.clear()
        address = 0
        while address < self._memory.size():
            instruction = self._instructions.get(address)
            if instruction is not None:
                self._address_to_row[address] = len(rows)
                rows.append( CodeRow( address=address, raw_bytes=bytes( ( self._memory[address], self._memory[address + 1],)), interpretation=str(instruction), status=self._status[address]))
                address += 2
                continue
            self._address_to_row[address] = len(rows)
            rows.append( CodeRow( address=address, raw_bytes=bytes((self._memory[address],)), interpretation=f"{self._memory[address]:02X}", status=self._status[address],))
            address += 1
        self._rows = rows


    def row_count(self) -> int:
        """
        @brief Return the number of visible rows.
        """
        return len(self._rows)

    def row(self, index: int) -> CodeRow:
        """
        @brief Return the specified row.
        """
        return self._rows[index]

    def find_row(self, address: int) -> int | None:
        """
        @brief Find the row representing the specified address.
        @param address Start address of the code or data row to locate.
        """
        return self._address_to_row.get(address)

