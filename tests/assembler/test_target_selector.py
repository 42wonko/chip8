"""
@file test_target_selector.py

@brief Unit tests for assembler target selection.
"""

import unittest

from assembler.target import Target
from assembler.target_selector import TargetSelectionError, TargetSelector


class TargetSelectorTest(unittest.TestCase):
    """
    @brief Tests for TargetSelector.
    """

    def setUp(self) -> None:
        self.selector = TargetSelector()

    def test_source_target_is_selected(self) -> None:
        result = self.selector.select( "TARGET COSMAC", None)
        self.assertEqual(result.target, Target.COSMAC)
        self.assertTrue(result.from_source)

    def test_external_target_is_selected_without_source_target(self) -> None:
        result = self.selector.select( "CLS", Target.COSMAC)
        self.assertEqual(result.target, Target.COSMAC)
        self.assertFalse(result.from_source)

    def test_source_target_takes_precedence(self) -> None:
        result = self.selector.select( "TARGET COSMAC", Target.COSMAC)
        self.assertEqual(result.target, Target.COSMAC)
        self.assertTrue(result.from_source)

    def test_missing_target_is_rejected(self) -> None:
        with self.assertRaises(TargetSelectionError):
            self.selector.select( "CLS", None)

    def test_unknown_source_target_is_rejected(self) -> None:
        with self.assertRaises(TargetSelectionError):
            self.selector.select( "TARGET UNKNOWN", None)

    def test_target_requires_architecture_name(self) -> None:
        with self.assertRaises(TargetSelectionError):
            self.selector.select( "TARGET", None)

    def test_target_rejects_extra_operands(self) -> None:
        with self.assertRaises(TargetSelectionError):
            self.selector.select( "TARGET COSMAC EXTRA", None)

    def test_multiple_target_directives_are_rejected(self) -> None:
        source = """
TARGET COSMAC
TARGET COSMAC
"""
        with self.assertRaises(TargetSelectionError):
            self.selector.select( source, None)

    def test_target_is_case_insensitive(self) -> None:
        result = self.selector.select( "target cosmac", None)
        self.assertEqual(result.target, Target.COSMAC)
        self.assertTrue(result.from_source)

    def test_target_may_be_surrounded_by_whitespace(self) -> None:
        result = self.selector.select( "   TARGET   COSMAC   ", None)
        self.assertEqual(result.target, Target.COSMAC)

    def test_target_may_have_comment(self) -> None:
        result = self.selector.select( "TARGET COSMAC ; target architecture", None)
        self.assertEqual(result.target, Target.COSMAC)

    def test_comment_does_not_define_target(self) -> None:
        source = """
; TARGET COSMAC
CLS
"""
        with self.assertRaises(TargetSelectionError):
            self.selector.select( source, None)

    def test_non_target_statement_is_ignored(self) -> None:
        result = self.selector.select( "CLS", Target.COSMAC)
        self.assertEqual(result.target, Target.COSMAC)
        self.assertFalse(result.from_source)
