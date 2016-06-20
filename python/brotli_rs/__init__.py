"""Safe-Rust Brotli decompression for Python."""

from __future__ import annotations

from importlib.metadata import version as distribution_version
from typing import Final

from ._brotli_rs import _decompress, error

__version__: Final = distribution_version("brotli-rs")
version: Final = __version__


def _as_bytes(data: object) -> bytes:
    if isinstance(data, bytes):
        return data
    try:
        view = memoryview(data)
    except TypeError:
        raise TypeError("a bytes-like object is required") from None
    if not view.c_contiguous:
        raise BufferError("memoryview: underlying buffer is not C-contiguous")
    try:
        return view.cast("B").tobytes()
    except TypeError:
        return view.tobytes()


def decompress(data: object) -> bytes:
    """Decode one complete Brotli stream."""

    return _decompress(_as_bytes(data))


Error = error

__all__ = ["Error", "decompress", "error", "version"]
