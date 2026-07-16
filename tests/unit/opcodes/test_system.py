"""
@file test_system.py

@brief Tests for CHIP-8 system instructions.
"""

import unittest

from emulator.instruction import Instruction
from tests.helpers import create_machine, write_opcode


class TestSystemInstructions(unittest.TestCase):
    """
    @brief Tests for system instructions.
    """
    ###########################################################################
    # 00E0 - CLS
    ###########################################################################

    def test_cls(self) -> None:
        """
        @brief Test if CLD actually clears the screen.
        """
        machine = create_machine()
        machine.framebuffer.set_pixel(10, 5, True)
        write_opcode(machine, 0x00E0)
        result = machine.execute_cycle()
        self.assertFalse(machine.framebuffer.get_pixel(10, 5))
        self.assertTrue(result.display_changed)


    def test_instruction_str_cls(self) -> None:
        """
        @brief test if mnemonic is correct.
        """
        instruction = Instruction.decode(0x200, 0x00E0)
        self.assertEqual(str(instruction), "CLS")


    ###########################################################################
    # 00EE - RET
    ###########################################################################
    def test_ret(self) -> None:
        machine = create_machine()
        machine.stack.push(0x456)
        write_opcode(machine, 0x00EE)
        machine.execute_cycle()
        self.assertEqual(machine.registers.pc, 0x456)

    def test_unknown_opcode_raises(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        with self.assertRaises(NotImplementedError):
            machine.execute_cycle()

    def test_unknown_opcode_raises_2(self) -> None:
        machine = create_machine()
        write_opcode(machine, 0xFFFF)
        with self.assertRaisesRegex( NotImplementedError, r"FFFF",):
            machine.execute_cycle()


if __name__ == "__main__":
    unittest.main(verbosity=2)
