"""
@file bufferedfilesink.py

@brief Buffered text output for logging and tracing.
"""

from __future__ import annotations
from pathlib import Path
from typing import TextIO


class BufferedFileSink:
    """
    @brief Text output sink for log and trace files.

    @details
    The current implementation writes directly to disk.

    The implementation may later be replaced by a buffered writer without
    changing the public interface.
    """

    def __init__(self) -> None:
        self._file: TextIO | None = None


    def open(self, filename: str) -> None:
        """
        @brief Open the output file.

        Any previously open file is closed first.
        """
        self.close()
        if not filename:
            return
        self._file = Path(filename).open( mode="a", encoding="utf-8")


    def close(self) -> None:
        """
        @brief Close the output file.
        """
        if self._file is not None:
            self._file.close()
            self._file = None


    def is_open(self) -> bool:
        """
        @brief Return whether a file is currently open.
        """
        return self._file is not None


    def write(self, text: str) -> None:
        """
        @brief Write one line.

        Nothing is written if no file is open.
        """
        if self._file is None:
            return

        self._file.write(text)
        self._file.write("\n")
        self._file.flush()
