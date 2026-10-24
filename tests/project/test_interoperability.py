"""Cross-implementation tests using Google's C package only as an oracle."""

import pytest

import brotli_rs


brotli = pytest.importorskip("brotli", reason="install the 'oracle' extra")


@pytest.mark.parametrize("mode", range(3))
@pytest.mark.parametrize("quality", [0, 1, 5, 9, 11])
@pytest.mark.parametrize(
    "data",
    [b"", b"hello", bytes(range(256)) * 1000, b"A" * 1_000_000],
)
def test_google_and_rust_streams_are_mutually_decodable(data, mode, quality):
    rust_encoded = brotli_rs.compress(data, mode=mode, quality=quality)
    google_encoded = brotli.compress(data, mode=mode, quality=quality)

    assert brotli.decompress(rust_encoded) == data
    assert brotli_rs.decompress(google_encoded) == data

