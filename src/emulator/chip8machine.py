"""
@file chip8machine.py

@brief CHIP-8 virtual machine.

@details
Owns all hardware components of the CHIP-8 virtual machine.

The machine provides a single point of access to the virtual hardware.
Instruction execution will be added in a later milestone.

@author
Michael Dlubatz

@copyright
MIT License
"""

from __future__ import annotations

import random

from controller.executiontracereporter import ExecutionTraceReporter
from emulator.chip8framebuffer import Chip8Framebuffer
from emulator.chip8keyboard import Chip8Keyboard
from emulator.chip8memory import Chip8Memory
from emulator.chip8registers import Chip8Registers
from emulator.chip8stack import Chip8Stack
from emulator.chip8timers import Chip8Timers
from emulator.constants import FONT_CHARACTER_SIZE, FONT_START, FONTSET, PROGRAM_START
from emulator.instruction import Instruction
from emulator.stepresult import StepResult
from emulator.tracerecord import TraceRecord


class Chip8Machine:
    """
    @brief CHIP-8 virtual machine.
    """
    def __init__(self, tracer: ExecutionTraceReporter) -> None:

        """
        @brief Construct the virtual machine.
        @detai All members are private to prevent other classes from accidentally
        replacing any of the hardware components. By decorating them with @property
        we can still use them, though.
        """
        self._memory            = Chip8Memory()
        self._registers         = Chip8Registers()
        self._stack             = Chip8Stack()
        self._timers            = Chip8Timers()
        self._keyboard          = Chip8Keyboard()
        self._framebuffer       = Chip8Framebuffer()
        self._trace_reporter    = tracer
        self.reset()

    ###########################################################################
    # Hardware access
    ###########################################################################
    @property
    def memory(self) -> Chip8Memory:
        """
        @brief Return the main memory.
        """
        return self._memory


    @property
    def registers(self) -> Chip8Registers:
        """
        @brief Return the CPU registers.
        """
        return self._registers


    @property
    def stack(self) -> Chip8Stack:
        """
        @brief Return the call stack.
        """
        return self._stack


    @property
    def timers(self) -> Chip8Timers:
        """
        @brief Return the timer registers.
        """
        return self._timers


    @property
    def keyboard(self) -> Chip8Keyboard:
        """
        @brief Return the hexadecimal keypad.
        """
        return self._keyboard


    @property
    def framebuffer(self) -> Chip8Framebuffer:
        """
        @brief Return the framebuffer.
        """
        return self._framebuffer


    ###########################################################################
    # Machine control
    ###########################################################################
    def reset(self) -> None:
        """
        @brief Reset the complete virtual machine.
        """
        self._memory.reset()
        self._registers.reset()
        self._stack.reset()
        self._timers.reset()
        self._keyboard.reset()
        self._framebuffer.reset()
        for offset, byte in enumerate(FONTSET):                 # init the builtin font
            self._memory.write_byte(FONT_START + offset, byte)

    def load_rom(self, data: bytes) -> None:
        """
        @brief Load a ROM image.

        @param data
            ROM contents.
        """
        self.reset()
        self._memory.load_rom(data)
        self._registers.pc = PROGRAM_START


    def tick_timers(self) -> None:
        """
        @brief Advance the hardware timers.
        """
        self._timers.tick()


    def fetch_instruction(self) -> Instruction:
        """
        @brief Fetch and decode the next instruction.
        """
        address = self._registers.pc
        msb = self._memory.read_byte(address)
        lsb = self._memory.read_byte(address + 1)
        opcode = (msb << 8) | lsb
        self._registers.pc += 2
        return Instruction.decode( address, opcode)

    def peek_instruction(self) -> Instruction:
        address = self._registers.pc
        msb = self._memory.read_byte(address)
        lsb = self._memory.read_byte(address + 1)
        opcode = (msb << 8) | lsb
        return Instruction.decode( address, opcode)

    def execute_cycle(self) -> StepResult:
        """
        @brief Execute one instruction.
        """
        result = StepResult()
        ptrace_rec = TraceRecord()

        instruction = self.fetch_instruction()
        ptrace_rec.pc_before = instruction.address
        ptrace_rec.instruction = instruction

        self._execute_instruction(instruction, result)
        if instruction.family == 0xB:
            result.bnnn_target = ( instruction.address, self.registers.pc)
        ptrace_rec.pc_after = self._registers.pc
        self._trace_reporter.trace(ptrace_rec)
        return result


    ###########################################################################
    # private helpers
    ###########################################################################
    def _execute_instruction(self, instruction: Instruction, result: StepResult) -> None:
        """
        @brief Execute one decoded CHIP-8 instruction.

        @param instruction
            Decoded instruction.
        """

        match instruction.opcode & 0xF000:
            #######################################################################
            # 0NNN family
            #######################################################################
            case 0x0000:
                match instruction.opcode:
                    case 0x00E0:                                        # 00E0 - CLS
                        self._framebuffer.clear()
                        result.display_changed = True

                    case 0x00EE:                                        # 00EE - RET
                        self._registers.pc = self._stack.pop()

                    case _:                                             # Unsupported 0NNN instruction
                        raise NotImplementedError( f"Opcode {instruction.opcode:04X} is not implemented.")

            case 0x1000:                                                # 1NNN - JP addr
                self._registers.pc = instruction.nnn

            case 0x2000:                                                # 2NNN - CALL addr
                self._stack.push(self._registers.pc)
                self._registers.pc = instruction.nnn

            case 0x3000:                                                # 3XNN - SE Vx, Byte
                if self._registers[instruction.x] == instruction.nn:
                    self._registers.pc += 2

            case 0x4000:                                                # 4XNN - SNE Vx, Byte
                if self._registers[instruction.x] != instruction.nn:
                    self._registers.pc += 2

            case 0x5000:                                                # 5XY0 - SE Vx, Vy
                if instruction.n != 0:
                    raise NotImplementedError( f"Opcode {instruction.opcode:04X} is not implemented.")

                if self._registers[instruction.x] == self._registers[instruction.y]:
                    self._registers.pc += 2

            case 0x6000:                                                # 6XNN - LD Vx, byte
                self._registers[instruction.x] = instruction.nn

            case 0x7000:                                                # 7XNN - ADD Vx, byte
                self._registers[instruction.x] += instruction.nn

            #######################################################################
            # 8NNN family
            #######################################################################
            case 0x8000:
                match instruction.n:
                    case 0x0:                                           # 8XY0 - LD Vx, Vy
                        self._registers[instruction.x] = self._registers[instruction.y]

                    case 0x1:                                           # 8XY1 - OR Vx, Vy
                        self._registers[instruction.x] |= self._registers[instruction.y]

                    case 0x2:                                           # 8XY2 - AND Vx, Vy
                        self._registers[instruction.x] &= self._registers[instruction.y]

                    case 0x3:                                           # 8XY3 - XOR Vx, Vy
                        self._registers[instruction.x] ^= self._registers[instruction.y]

                    case 0x4:                                           # 8XY4 - ADD Vx, Vy with Carry
                        vx = self._registers[instruction.x]
                        vy = self._registers[instruction.y]
                        sum = vx + vy
                        self._registers[0xF] = 1 if sum > 0xFF else 0
                        self._registers[instruction.x] = sum

                    case 0x5:                                           # 8XY5 - SUB Vx, Vy
                        vx = self._registers[instruction.x]
                        vy = self._registers[instruction.y]
                        self._registers[0xF] = 1 if vx >= vy else 0
                        self._registers[instruction.x] = vx - vy

                    case 0x6:                                           # 8XY6 - SHR Vx (original COSMAC VIP behaviour)
                        vx = self._registers[instruction.x]
                        self._registers[0xF] = vx & 0x01
                        self._registers[instruction.x] = vx >> 1

                    case 0x7:                                           # 8XY7 - SUBN Vx, Vy
                        vx = self._registers[instruction.x]
                        vy = self._registers[instruction.y]
                        self._registers[0xF] = 1 if vy >= vx else 0
                        self._registers[instruction.x] = vy - vx

                    case 0xE:                                           # 8XYE - SHL Vx (original COSMAC VIP behaviour)
                        vx = self._registers[instruction.x]
                        self._registers[0xF] = (vx >> 7) & 0x01
                        self._registers[instruction.x] = vx << 1

            case 0x9000:                                                # 9 XY0 - SNE Vx,Vy
                if instruction.n != 0:
                    raise NotImplementedError( f"Opcode {instruction.opcode:04X} is not implemented.")

                if self._registers[instruction.x] != self._registers[instruction.y]:
                    self._registers.pc += 2

            case 0xA000:                                                # ANNN - LD I, addr
                self._registers.i = instruction.nnn

            case 0xB000:
                self._registers.pc = instruction.nnn + self._registers[0]    # BNNN - JP V0, nnn

            case 0xC000:                                                # set vx to a random value masked (bitwise AND) with NN
                self._registers[instruction.x] = random.randint(0, 0xFF) & instruction.nn

            case 0xD000:                                                # original chip8 only has this draw instruction
                collision = False

                x = self._registers[instruction.x]
                y = self._registers[instruction.y]

                for row in range(instruction.n):
                    sprite = self._memory.read_byte(self._registers.i + row)

                    for bit in range(8):
                        if sprite & (0x80 >> bit):
                            if self._framebuffer.xor_pixel(x + bit, y + row):
                                collision = True

                self._registers[0xF] = 1 if collision else 0
                result.display_changed = True
#
            #######################################################################
            # EX00 family
            #######################################################################
            case 0xE000:
                match instruction.nn:
                    case 0x9E:                                          # Skip if key Vx pressed
                        if self._keyboard.is_pressed( self._registers[instruction.x]):
                            self._registers.pc += 2
                    case 0xA1:                                          # Skip if key Vx not pressed
                        if not self._keyboard.is_pressed( self._registers[instruction.x]):
                            self._registers.pc += 2

            case 0xF000:                                                #
                match instruction.nn:
                    case 0x07:                                          # FX07 - LD Vx, DT
                        self._registers[instruction.x] = self._timers.delay_timer

                    case 0x0A:
                        key = self._keyboard.first_pressed()
                        if key is None:
                            self._registers.pc -= 2
                        else:
                            self._registers[instruction.x] = key

                    case 0x15:                                          # FX15 - LD DT, Vx
                        self._timers.delay_timer = self._registers[instruction.x]

                    case 0x18:                                          # FX18 - LD ST, Vx
                        self._timers.sound_timer = self._registers[instruction.x]

                    case 0x1E:                                          # FX1E — ADD I, Vx
                        self._registers.i += self._registers[instruction.x]

                    case 0x29:                                          # FX29 — LD F, Vx
                        digit = self._registers[instruction.x] & 0x0F
                        self._registers.i = FONT_START + digit * FONT_CHARACTER_SIZE

                    case 0x33:                                          # FX33 - write the value of vX as BCD value at the addresses I, I+1 and I+2
                        value = self._registers[instruction.x]
                        self._memory.write_byte(self._registers.i + 0, value // 100)
                        self._memory.write_byte(self._registers.i + 1, (value // 10) % 10)
                        self._memory.write_byte(self._registers.i + 2, value % 10)
                        result.memory_range = (self.registers.i, self.registers.i + 2)

                    case 0x55:                                          # Store v0 to vX at the memory pointed to by I, I is not channged
                        for register in range(instruction.x + 1):
                            self._memory.write_byte( self._registers.i + register, self._registers[register])

                    case 0x65:                                          # read the bytes from memory pointed to by I into the registers v0 to vX, I is unchanged
                        for register in range(instruction.x + 1):
                            self._registers[register] = self._memory.read_byte( self._registers.i + register)
                        result.memory_range = (self.registers.i, self.registers.i + instruction.x)

                    case _:
                        raise NotImplementedError(f"{instruction.opcode:04X}")

            #######################################################################
            # Unsupported instruction
            #######################################################################
            case _:
                raise NotImplementedError(
                    f"Opcode {instruction.opcode:04X} is not implemented."
                )
