"""End-to-end assembler tests for the Super-CHIP Modern ISA."""

import unittest

from assembler.assembler import Assembler
from assembler.classicparser import ClassicParser
from chip8.isa.superchipmodernisa import SuperChipModernInstructionSetArchitecture
from controller.diagnostics import AssemblerDiagnostics


class TestSuperChipModernAssembler(unittest.TestCase):
    """Verify Modern-specific user-flag register encodings."""

    def setUp(self) -> None:
        self._isa = SuperChipModernInstructionSetArchitecture()
        self._assembler = Assembler(
            AssemblerDiagnostics().reporter(),
            self._isa,
            ClassicParser(self._isa),
        )

    def test_user_flag_transfers_support_vf(self) -> None:
        result = self._assembler.assemble("LD R, VF\nLD VF, R")
        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(result.binary_image, bytes.fromhex("FF 75 FF 85"))

    def test_modern_profile_assembles_inherited_superchip_instructions(self) -> None:
        source = "\n".join(
            (
                "LOW",
                "HIGH",
                "EXIT",
                "SCD 3",
                "SCR",
                "SCL",
                "LD HF, V3",
                "DRW V1, V2, 0",
                "LD R, VF",
                "LD VF, R",
            )
        )
        result = self._assembler.assemble(source)
        self.assertTrue(result.success, result.diagnostics)
        self.assertEqual(
            result.binary_image,
            bytes.fromhex(
                "00 FE 00 FF 00 FD 00 C3 00 FB 00 FC "
                "F3 30 D1 20 FF 75 FF 85"
            ),
        )

    def test_modern_profile_rejects_unknown_instruction(self) -> None:
        result = self._assembler.assemble("NOT_AN_INSTRUCTION")
        self.assertFalse(result.success)
        self.assertTrue(result.diagnostics)

if __name__ == "__main__":
    unittest.main(verbosity=2)
