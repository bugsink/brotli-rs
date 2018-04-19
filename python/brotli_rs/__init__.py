"""Safe-Rust Brotli compression for Python."""

from __future__ import annotations

from enum import IntEnum
from importlib.metadata import version as distribution_version
from operator import index
from typing import Final

from ._brotli_rs import _compress, _decompress, error

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


def _parameters(mode: object, quality: object, lgwin: object, lgblock: object):
    return index(mode), index(quality), index(lgwin), index(lgblock)


class Compressor:
    """Collect input and produce a single Brotli stream on ``finish()``.

    The 2.0.0 Rust crate's streaming writer does not accept all encoder
    parameters, so this historical binding deliberately buffers input.
    """

    def __init__(
        self,
        mode: int = MODE_GENERIC,
        quality: int = 11,
        lgwin: int = 22,
        lgblock: int = 0,
    ) -> None:
        self._parameters = _parameters(mode, quality, lgwin, lgblock)
        self._input = bytearray()
        self._finished = False

    def process(self, data: object) -> bytes:
        data = _as_bytes(data)
        if self._finished:
            if not data:
                return b""
            raise error("Compressor has already been finished")
        self._input.extend(data)
        return b""

    def flush(self) -> bytes:
        return b""

    def finish(self) -> bytes:
        if self._finished:
            return b""
        self._finished = True
        return _compress(bytes(self._input), *self._parameters)


def compress(
    data: object,
    mode: int = MODE_GENERIC,
    quality: int = 11,
    lgwin: int = 22,
    lgblock: int = 0,
) -> bytes:
    """Compress a bytes-like object into one Brotli stream."""

    return _compress(
        _as_bytes(data), *_parameters(mode, quality, lgwin, lgblock)
    )


def decompress(data: object) -> bytes:
    """Decode one complete Brotli stream."""

    return _decompress(_as_bytes(data))


Error = error

__all__ = [
    "BrotliEncoderMode",
    "Compressor",
    "Error",
    "MODE_FONT",
    "MODE_GENERIC",
    "MODE_TEXT",
    "compress",
    "decompress",
    "error",
    "version",
]
