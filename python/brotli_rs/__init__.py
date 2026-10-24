"""Safe-Rust Brotli compression for Python."""

from __future__ import annotations

from enum import IntEnum
from importlib.metadata import version as distribution_version
from operator import index
from typing import Final

from ._brotli_rs import (
    _Compressor,
    _Decompressor,
    error,
)

__version__: Final = distribution_version("brotli-rs")
version: Final = __version__


class BrotliEncoderMode(IntEnum):
    """Values accepted by the ``mode`` compression parameter."""

    GENERIC = 0
    TEXT = 1
    FONT = 2


MODE_GENERIC: Final = BrotliEncoderMode.GENERIC
MODE_TEXT: Final = BrotliEncoderMode.TEXT
MODE_FONT: Final = BrotliEncoderMode.FONT


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


def _optional_nonnegative_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    try:
        result = index(value)
    except TypeError:
        raise TypeError(f"{name} must be an integer or None") from None
    if result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


class Compressor:
    """Incrementally produce a single Brotli stream."""

    def __init__(
        self,
        mode: int = MODE_GENERIC,
        quality: int = 11,
        lgwin: int = 22,
        lgblock: int = 0,
    ) -> None:
        mode = index(mode)
        quality = index(quality)
        lgwin = index(lgwin)
        lgblock = index(lgblock)
        if mode not in range(3):
            raise error("Invalid mode")
        if quality not in range(12):
            raise error("Invalid quality")
        if lgwin not in range(10, 25):
            raise error("Invalid lgwin")
        if lgblock != 0 and lgblock not in range(16, 25):
            raise error("Invalid lgblock")
        self._inner = _Compressor(mode, quality, lgwin, lgblock)

    def process(self, data: object) -> bytes:
        return self._inner.process(_as_bytes(data))

    def flush(self) -> bytes:
        return self._inner.flush()

    def finish(self) -> bytes:
        return self._inner.finish()


class Decompressor:
    """Incrementally decode one Brotli stream."""

    def __init__(self, *, max_output: int | None = None) -> None:
        self._inner = _Decompressor(
            _optional_nonnegative_int(max_output, "max_output")
        )

    def process(
        self, data: object, output_buffer_limit: int | None = None
    ) -> bytes:
        limit = _optional_nonnegative_int(
            output_buffer_limit, "output_buffer_limit"
        )
        return self._inner.process(_as_bytes(data), limit)

    def can_accept_more_data(self) -> bool:
        return self._inner.can_accept_more_data()

    def is_finished(self) -> bool:
        return self._inner.is_finished()


def compress(
    data: object,
    mode: int = MODE_GENERIC,
    quality: int = 11,
    lgwin: int = 22,
    lgblock: int = 0,
) -> bytes:
    """Compress a bytes-like object into one Brotli stream."""

    compressor = Compressor(mode, quality, lgwin, lgblock)
    return compressor.process(data) + compressor.finish()


def decompress(data: object, *, max_output: int | None = None) -> bytes:
    """Decode exactly one complete Brotli stream."""

    decompressor = Decompressor(max_output=max_output)
    output = decompressor.process(data)
    if not decompressor.is_finished():
        raise error("BrotliDecompress failed: incomplete stream")
    return output


Error = error

__all__ = [
    "BrotliEncoderMode",
    "Compressor",
    "Decompressor",
    "Error",
    "MODE_FONT",
    "MODE_GENERIC",
    "MODE_TEXT",
    "compress",
    "decompress",
    "error",
    "version",
]

