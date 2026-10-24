"""Cross-implementation tests against Google's independent C package."""

import pytest

import brotli
import brotli_rs


@pytest.mark.parametrize("mode", range(3))
@pytest.mark.parametrize("quality", [0, 1, 5, 9, 11])
@pytest.mark.parametrize(
    "data",
    [b"", b"hello", bytes(range(256)) * 1000, b"A" * 1_000_000],
    ids=["empty", "hello", "all-byte-values", "repeated-a"],
)
def test_google_and_rust_streams_are_mutually_decodable(data, mode, quality):
    rust_encoded = brotli_rs.compress(data, mode=mode, quality=quality)
    google_encoded = brotli.compress(data, mode=mode, quality=quality)

    assert brotli.decompress(rust_encoded) == data
    assert brotli_rs.decompress(google_encoded) == data

