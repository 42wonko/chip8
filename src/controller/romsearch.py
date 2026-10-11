"""Utilities for searching byte sequences in a loaded ROM."""

from __future__ import annotations


def find_byte_sequences(data: bytes, needle: bytes) -> list[int]:
    """Return every offset where *needle* occurs in *data*.

    Matches may overlap. An empty needle is rejected because it would match
    every offset and is not a useful ROM search.
    """
    if not needle:
        raise ValueError("The byte sequence to search for must not be empty.")

    matches: list[int] = []
    offset = data.find(needle)
    while offset != -1:
        matches.append(offset)
        offset = data.find(needle, offset + 1)
    return matches
