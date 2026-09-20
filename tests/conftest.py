"""Shared test fixtures and helpers."""

import os


class FakeMedia:
    """Minimal stand-in for a :class:`Media` object.

    The filename-based strategies only touch ``original_name`` and ``path``;
    this fake lets us exercise them without creating real files. For strategies
    that read the filesystem (EXIF, mtime), pass a ``path`` pointing at a real
    file on disk.
    """

    def __init__(self, original_name: str, path: str = "") -> None:
        self.original_name = original_name
        self.path = path


def touch(directory: str, name: str) -> str:
    """Create an empty file ``name`` inside ``directory`` and return its path."""
    full = os.path.join(directory, name)
    with open(full, "w"):
        pass
    return full
