"""Tests for target selection with expanded-source provenance."""
import tempfile
import unittest
from pathlib import Path

from assembler.includeprocessor import IncludeProcessor, SourceOrigin
from assembler.target import Target
from assembler.target_selector import TargetSelectionError, TargetSelector


class TargetSelectorSourceMappingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.selector = TargetSelector()

    def test_duplicate_target_in_same_file_reports_both_locations(self) -> None:
        source = "TARGET COSMAC\nCLS\nTARGET SCHIPC\n"
        origins = (
            SourceOrigin(Path("main.asm"), 1),
            SourceOrigin(Path("main.asm"), 2),
            SourceOrigin(Path("main.asm"), 3)
        )

        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select(source, None, origins)

        self.assertIn("main.asm:1", str(context.exception))
        self.assertIn("main.asm:3", str(context.exception))

    def test_duplicate_same_target_is_rejected(self) -> None:
        source = "TARGET COSMAC\nTARGET COSMAC\n"
        origins = (
            SourceOrigin(Path("main.asm"), 4),
            SourceOrigin(Path("included.asm"), 9)
        )

        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select(source, None, origins)

        self.assertIn("main.asm:4", str(context.exception))
        self.assertIn("included.asm:9", str(context.exception))

    def test_target_in_nested_include_reports_original_locations(self) -> None:
        source = "TARGET COSMAC\nTARGET SCHIP11\n"
        origins = (
            SourceOrigin(Path("main.asm"), 2),
            SourceOrigin(Path("nested/targets.asm"), 17)
        )

        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select(source, None, origins)

        self.assertIn("main.asm:2", str(context.exception))
        self.assertIn("nested/targets.asm:17", str(context.exception))

    def test_single_target_in_included_file_is_selected(self) -> None:
        source = "CLS\nTARGET SCHIPC\n"
        origins = (
            SourceOrigin(Path("main.asm"), 1),
            SourceOrigin(Path("parts/target.asm"), 6)
        )

        result = self.selector.select(source, None, origins)

        self.assertEqual(result.target, Target.SCHIPC)
        self.assertTrue(result.from_source)

    def test_unknown_target_reports_original_location(self) -> None:
        source = "TARGET UNKNOWN\n"
        origins = (SourceOrigin(Path("parts/target.asm"), 12),)

        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select(source, None, origins)

        self.assertIn("parts/target.asm:12", str(context.exception))

    def test_invalid_target_directive_reports_original_location(self) -> None:
        source = "TARGET COSMAC EXTRA\n"
        origins = (SourceOrigin(Path("parts/target.asm"), 12),)

        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select(source, None, origins)

        self.assertIn("parts/target.asm:12", str(context.exception))

    def test_missing_origin_mapping_retains_expanded_line_diagnostic(self) -> None:
        with self.assertRaises(TargetSelectionError) as context:
            self.selector.select("TARGET COSMAC\nTARGET SCHIPC", None)

        self.assertIn("line 1", str(context.exception))
        self.assertIn("line 2", str(context.exception))

    def test_duplicate_target_across_included_file_reports_both_locations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            main_file = root / "main.asm"
            included_file = root / "parts" / "target.asm"
            included_file.parent.mkdir()
            included_file.write_text( "TARGET SCHIPC\n", encoding="utf-8")
            expanded = IncludeProcessor().expand(
                'TARGET COSMAC\nINCLUDE "parts/target.asm"\n',
                main_file
            )
            with self.assertRaises(TargetSelectionError) as context:
                self.selector.select(
                    expanded.source,
                    None,
                    expanded.line_origins
                )
            message = str(context.exception)
            self.assertIn(f"{main_file.resolve()}:1", message)
            self.assertIn(f"{included_file.resolve()}:1", message)

if __name__ == "__main__":
    unittest.main()
