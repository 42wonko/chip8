"""
@file test_includeprocessor.py

@brief Unit tests for architecture-independent INCLUDE expansion.
"""

import tempfile
import unittest
from pathlib import Path

from assembler.includeprocessor import IncludeError, IncludeProcessor


class IncludeProcessorTest(unittest.TestCase):
    """Tests for recursive source inclusion and path resolution."""

    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.main_file = self.root / "main.asm"

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def write_file(self, relative_path: str, source: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def test_source_without_include_is_unchanged(self) -> None:
        source = "TARGET COSMAC\nCLS\n"
        result = IncludeProcessor().expand(source, self.main_file)
        self.assertEqual(result.source, source)
        self.assertEqual(
            [(origin.filename, origin.line) for origin in result.line_origins],
            [(self.main_file.resolve(), 1), (self.main_file.resolve(), 2)]
        )

    def test_include_replaces_its_directive_line(self) -> None:
        self.write_file("parts/code.asm", "LD V0, 1\nLD V1, 2\n")
        source = 'CLS\nINCLUDE "parts/code.asm"\nRET\n'
        result = IncludeProcessor().expand(source, self.main_file)
        self.assertEqual(result.source, "CLS\nLD V0, 1\nLD V1, 2\nRET\n")
        self.assertEqual(
            [(origin.filename.name, origin.line) for origin in result.line_origins],
            [("main.asm", 1), ("code.asm", 1), ("code.asm", 2), ("main.asm", 3)]
        )

    def test_include_directive_is_case_insensitive_and_allows_comment(self) -> None:
        self.write_file("code.asm", "CLS\n")
        result = IncludeProcessor().expand('include "code.asm" ; comment\n', self.main_file)
        self.assertEqual(result.source, "CLS\n")

    def test_nested_include_uses_including_file_directory_when_path_is_empty(self) -> None:
        self.write_file("sub/first.asm", 'INCLUDE "second.asm"\n')
        self.write_file("sub/second.asm", "RET\n")
        result = IncludeProcessor().expand('INCLUDE "sub/first.asm"\n', self.main_file)
        self.assertEqual(result.source, "RET\n")
        self.assertEqual(result.line_origins[0].filename, (self.root / "sub/second.asm").resolve())

    def test_nonempty_include_path_is_used_for_nested_includes(self) -> None:
        include_root = self.root / "includes"
        (include_root / "nested").mkdir(parents=True)
        (include_root / "first.asm").write_text('INCLUDE "nested/second.asm"\n', encoding="utf-8")
        (include_root / "nested/second.asm").write_text("RET\n", encoding="utf-8")
        self.write_file("sub/first.asm", "SHOULD NOT BE USED\n")
        result = IncludeProcessor(str(include_root)).expand('INCLUDE "first.asm"\n', self.main_file)
        self.assertEqual(result.source, "RET\n")

    def test_relative_include_path_is_anchored_at_main_source_directory(self) -> None:
        self.write_file("config/includes/code.asm", "CLS\n")
        processor = IncludeProcessor("config/includes")
        result = processor.expand('INCLUDE "code.asm"\n', self.main_file)
        self.assertEqual(result.source, "CLS\n")

    def test_absolute_include_filename_is_used_directly(self) -> None:
        included = self.write_file("outside.asm", "RET\n")
        result = IncludeProcessor().expand(f'INCLUDE "{included}"\n', self.main_file)
        self.assertEqual(result.source, "RET\n")

    def test_missing_file_reports_including_file_and_line(self) -> None:
        with self.assertRaises(IncludeError) as context:
            IncludeProcessor().expand('CLS\nINCLUDE "missing.asm"\n', self.main_file)
        self.assertEqual(context.exception.filename, self.main_file.resolve())
        self.assertEqual(context.exception.line, 2)
        self.assertIn("missing.asm", str(context.exception))

    def test_malformed_include_is_rejected(self) -> None:
        with self.assertRaises(IncludeError) as context:
            IncludeProcessor().expand("INCLUDE code.asm\n", self.main_file)
        self.assertEqual(context.exception.line, 1)
        self.assertIn('Expected INCLUDE "filename"', str(context.exception))

    def test_empty_filename_is_rejected(self) -> None:
        with self.assertRaises(IncludeError):
            IncludeProcessor().expand('INCLUDE ""\n', self.main_file)

    def test_trailing_tokens_are_rejected(self) -> None:
        with self.assertRaises(IncludeError):
            IncludeProcessor().expand('INCLUDE "code.asm" EXTRA\n', self.main_file)

    def test_circular_include_is_rejected(self) -> None:
        self.write_file("first.asm", 'INCLUDE "second.asm"\n')
        self.write_file("second.asm", 'INCLUDE "first.asm"\n')
        with self.assertRaises(IncludeError) as context:
            IncludeProcessor().expand('INCLUDE "first.asm"\n', self.main_file)
        self.assertIn("Circular INCLUDE", str(context.exception))
        self.assertEqual(context.exception.filename, (self.root / "second.asm").resolve())
        self.assertEqual(context.exception.line, 1)

    def test_same_file_can_be_included_more_than_once(self) -> None:
        self.write_file("code.asm", "CLS\n")
        result = IncludeProcessor().expand(
            'INCLUDE "code.asm"\nINCLUDE "code.asm"\n',
            self.main_file
        )
        self.assertEqual(result.source, "CLS\nCLS\n")

    def test_included_file_without_final_newline_does_not_join_parent_line(self) -> None:
        self.write_file("code.asm", "CLS")
        result = IncludeProcessor().expand('INCLUDE "code.asm"\nRET\n', self.main_file)
        self.assertEqual(result.source, "CLS\nRET\n")
        self.assertEqual(
            [(origin.filename.name, origin.line) for origin in result.line_origins],
            [("code.asm", 1), ("main.asm", 2)]
        )

    def test_empty_included_file_preserves_parent_line_boundary(self) -> None:
        self.write_file("empty.asm", "")
        result = IncludeProcessor().expand('INCLUDE "empty.asm"\nRET\n', self.main_file)
        self.assertEqual(result.source, "\nRET\n")
        self.assertEqual(
            [(origin.filename.name, origin.line) for origin in result.line_origins],
            [("main.asm", 1), ("main.asm", 2)]
        )

    def test_detects_include_directive(self) -> None:
        self.assertTrue( IncludeProcessor.has_include_directives('INCLUDE "code.asm"\n'))

    def test_detects_case_insensitive_include_directive(self) -> None:
        self.assertTrue( IncludeProcessor.has_include_directives('  include "code.asm"\n'))

    def test_does_not_detect_include_in_comment(self) -> None:
        self.assertFalse( IncludeProcessor.has_include_directives("; INCLUDE \"code.asm\"\n"))

    def test_does_not_detect_include_in_instruction(self) -> None:
        self.assertFalse( IncludeProcessor.has_include_directives('LD V0, "INCLUDE"\n'))

    def test_detects_malformed_include_directive(self) -> None:
        self.assertTrue( IncludeProcessor.has_include_directives("INCLUDE code.asm\n"))

    def test_source_without_include_directive(self) -> None:
        self.assertFalse( IncludeProcessor.has_include_directives("TARGET COSMAC\nCLS\n"))

    def test_configured_include_path_does_not_fall_back_to_source_directory(self) -> None:
        """Verify a configured IncludePath is authoritative."""
        self.write_file("code.asm", "CLS\n")
        configured_path = self.root / "configured"
        configured_path.mkdir()
        processor = IncludeProcessor(str(configured_path))
        with self.assertRaises(IncludeError) as context:
            processor.expand('INCLUDE "code.asm"\n', self.main_file)
        self.assertEqual(context.exception.filename, self.main_file.resolve())
        self.assertEqual(context.exception.line, 1)
        self.assertIn("code.asm", str(context.exception))

if __name__ == "__main__":
    unittest.main()
