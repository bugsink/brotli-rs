from enum import IntEnum
from typing import Final

__version__: Final[str]
version: Final[str]

class error(Exception): ...
Error = error

class BrotliEncoderMode(IntEnum):
    GENERIC = 0
    TEXT = 1
    FONT = 2

MODE_GENERIC: Final[BrotliEncoderMode]
MODE_TEXT: Final[BrotliEncoderMode]
MODE_FONT: Final[BrotliEncoderMode]

class Compressor:
    def __init__(
        self,
        mode: int = ...,
        quality: int = ...,
        lgwin: int = ...,
        lgblock: int = ...,
    ) -> None: ...
    def process(self, data: object) -> bytes: ...
    def flush(self) -> bytes: ...
    def finish(self) -> bytes: ...

class Decompressor:
    def __init__(self, *, max_output: int | None = ...) -> None: ...
    def process(
        self, data: object, output_buffer_limit: int | None = ...
    ) -> bytes: ...
    def can_accept_more_data(self) -> bool: ...
    def is_finished(self) -> bool: ...

def compress(
    data: object,
    mode: int = ...,
    quality: int = ...,
    lgwin: int = ...,
    lgblock: int = ...,
) -> bytes: ...
def decompress(data: object, *, max_output: int | None = ...) -> bytes: ...

