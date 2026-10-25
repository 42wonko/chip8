
import tempfile
import unittest
from pathlib import Path

from controller.bufferedfilesink import BufferedFileSink


class BufferedFileSinkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.sink = BufferedFileSink()
        self.addCleanup(self.sink.close)

    def test_initially_closed(self) -> None:
        self.assertFalse(self.sink.is_open())

    def test_write_while_closed_does_nothing(self) -> None:
        self.sink.write("ignored")

        self.assertFalse(self.sink.is_open())

    def test_open_write_and_close(self) -> None:
        filename = str(Path(self.temp_dir.name) / "output.txt")

        self.sink.open(filename)
        self.assertTrue(self.sink.is_open())

        self.sink.write("first line")
        self.sink.write("second line")
        self.sink.close()

        self.assertFalse(self.sink.is_open())
        self.assertEqual(
            Path(filename).read_text(encoding="utf-8"),
            "first line\nsecond line\n"
        )

    def test_open_empty_filename_leaves_sink_closed(self) -> None:
        self.sink.open("")

        self.assertFalse(self.sink.is_open())

    def test_reopening_closes_previous_file(self) -> None:
        first_filename = str(Path(self.temp_dir.name) / "first.txt")
        second_filename = str(Path(self.temp_dir.name) / "second.txt")

        self.sink.open(first_filename)
        self.sink.write("first")
        self.sink.open(second_filename)
        self.sink.write("second")
        self.sink.close()

        self.assertEqual(
            Path(first_filename).read_text(encoding="utf-8"),
            "first\n"
        )
        self.assertEqual(
            Path(second_filename).read_text(encoding="utf-8"),
            "second\n"
        )

    def test_open_existing_file_appends(self) -> None:
        filename = Path(self.temp_dir.name) / "existing.txt"
        filename.write_text("existing\n", encoding="utf-8")

        self.sink.open(str(filename))
        self.sink.write("appended")
        self.sink.close()

        self.assertEqual(
            filename.read_text(encoding="utf-8"),
            "existing\nappended\n"
        )


if __name__ == "__main__":
    unittest.main()

