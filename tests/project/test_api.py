from pathlib import Path
import re

import pytest

import brotli
import brotli_rs


def test_python_and_rust_versions_match():
    cargo = (Path(__file__).parents[2] / "Cargo.toml").read_text()
    cargo_version = re.search(
        r'^version = "([^"]+)"$', cargo, flags=re.MULTILINE
    ).group(1)
    assert brotli_rs.__version__ == cargo_version
    assert brotli_rs.version == brotli_rs.__version__


@pytest.mark.parametrize(
    "data",
    [b"bytes", bytearray(b"bytearray"), memoryview(b"memoryview")],
)
def test_contiguous_buffer_inputs(data):
    assert brotli_rs.decompress(brotli_rs.compress(data)) == bytes(data)


def test_noncontiguous_input_is_rejected():
    with pytest.raises(BufferError):
        brotli_rs.compress(memoryview(b"abcdef")[::2])


def test_text_input_is_rejected():
    with pytest.raises(TypeError):
        brotli_rs.compress("not bytes")


@pytest.mark.parametrize("mode", range(3))
@pytest.mark.parametrize("quality", [0, 1, 5, 9, 11])
@pytest.mark.parametrize(
    "data",
    [b"", b"hello", bytes(range(256)) * 100, b"A" * 100_000],
    ids=["empty", "hello", "all-byte-values", "repeated-a"],
)
def test_google_and_rust_streams_are_mutually_decodable(data, mode, quality):
    rust_encoded = brotli_rs.compress(data, mode=mode, quality=quality)
    google_encoded = brotli.compress(data, mode=mode, quality=quality)

    assert brotli.decompress(rust_encoded) == data
    assert brotli_rs.decompress(google_encoded) == data


def test_compressor_buffers_until_finish():
    compressor = brotli_rs.Compressor(quality=5)
    assert compressor.process(b"some ") == b""
    assert compressor.flush() == b""
    assert compressor.process(b"content") == b""
    encoded = compressor.finish()
    assert brotli_rs.decompress(encoded) == b"some content"
    assert compressor.finish() == b""


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("mode", 3),
        ("quality", 12),
        ("lgwin", 9),
        ("lgblock", 15),
    ],
)
def test_invalid_compression_parameters_raise_codec_error(name, value):
    with pytest.raises(brotli_rs.error):
        brotli_rs.compress(b"data", **{name: value})
