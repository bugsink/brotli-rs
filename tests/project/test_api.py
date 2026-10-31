from array import array
from pathlib import Path
import re

import pytest

import brotli_rs


class BytesSubclass(bytes):
    pass


def test_python_and_rust_versions_match():
    cargo = (Path(__file__).parents[2] / "Cargo.toml").read_text()
    cargo_version = re.search(
        r'^version = "([^"]+)"$', cargo, flags=re.MULTILINE
    ).group(1)
    assert brotli_rs.__version__.split(".post", 1)[0] == cargo_version
    assert brotli_rs.version == brotli_rs.__version__


@pytest.mark.parametrize(
    "buffer_type",
    [
        bytes, BytesSubclass, bytearray, memoryview,
        lambda data: array("B", data),
        lambda data: memoryview(data).cast("B", shape=[len(data), 1]),
    ],
    ids=[
        "bytes", "bytes-subclass", "bytearray", "memoryview", "array",
        "multidimensional",
    ],
)
def test_contiguous_buffer_inputs(buffer_type):
    original = b"buffer input" * 100
    encoded = brotli_rs.compress(buffer_type(original))
    assert brotli_rs.decompress(buffer_type(encoded)) == original

    compressor = brotli_rs.Compressor()
    encoded = compressor.process(buffer_type(original)) + compressor.finish()
    decompressor = brotli_rs.Decompressor()
    assert decompressor.process(buffer_type(encoded)) == original
    assert decompressor.is_finished()


@pytest.mark.parametrize("operation", [
    brotli_rs.compress, brotli_rs.decompress,
    lambda data: brotli_rs.Compressor().process(data),
    lambda data: brotli_rs.Decompressor().process(data),
], ids=["compress", "decompress", "stream-compress", "stream-decompress"])
def test_noncontiguous_input_is_rejected(operation):
    with pytest.raises(BufferError):
        operation(memoryview(b"abcdef")[::2])


@pytest.mark.parametrize("operation", [
    brotli_rs.compress, brotli_rs.decompress,
    lambda data: brotli_rs.Compressor().process(data),
    lambda data: brotli_rs.Decompressor().process(data),
], ids=["compress", "decompress", "stream-compress", "stream-decompress"])
def test_text_input_is_rejected(operation):
    with pytest.raises(TypeError):
        operation("not bytes")


def test_one_shot_rejects_incomplete_stream():
    encoded = brotli_rs.compress(b"some content" * 100)
    with pytest.raises(brotli_rs.error, match="incomplete stream"):
        brotli_rs.decompress(encoded[:-1])


@pytest.mark.parametrize("maximum", [0, 1, 99])
def test_one_shot_max_output_rejects_larger_result(maximum):
    encoded = brotli_rs.compress(b"A" * 100)
    with pytest.raises(brotli_rs.error, match="max_output"):
        brotli_rs.decompress(encoded, max_output=maximum)


def test_one_shot_max_output_accepts_exact_result_size():
    encoded = brotli_rs.compress(b"A" * 100)
    assert brotli_rs.decompress(encoded, max_output=100) == b"A" * 100


def test_large_output_buffer_limit_does_not_preallocate_the_limit():
    encoded = brotli_rs.compress(b"small")
    decompressor = brotli_rs.Decompressor()
    assert decompressor.process(encoded, output_buffer_limit=2**40) == b"small"


@pytest.mark.parametrize("name", ["mode", "quality", "lgwin", "lgblock"])
def test_very_large_compression_parameters_raise_codec_error(name):
    with pytest.raises(brotli_rs.error):
        brotli_rs.Compressor(**{name: 2**100})


@pytest.mark.parametrize("name", ["max_output", "output_buffer_limit"])
def test_limits_must_be_nonnegative(name):
    with pytest.raises(ValueError):
        if name == "max_output":
            brotli_rs.Decompressor(max_output=-1)
        else:
            brotli_rs.Decompressor().process(b"", output_buffer_limit=-1)

