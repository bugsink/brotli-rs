"""Encoder cases adapted from Dropbox's Rust implementation.

Source: dropbox/rust-brotli@a51b65e75f68e3485be12bc816118e523e95647d
Original paths: src/enc/test.rs and src/bin/integration_tests.rs.
"""

from pathlib import Path

import pytest

import brotli_rs


TESTDATA = Path(__file__).with_name("testdata")


@pytest.mark.parametrize(
    ("filename", "quality", "lgwin"),
    [
        ("aaabaaaa", quality, 10) for quality in range(12)
    ]
    + [
        ("ends_with_truncated_dictionary", 11, 22),
        ("random_then_unicode", 0, 20),
        ("random_then_unicode", 6, 20),
        ("random_then_unicode", 9, 20),
        ("random_then_unicode", 11, 20),
    ],
)
def test_encoder_roundtrip_vectors(filename, quality, lgwin):
    original = (TESTDATA / filename).read_bytes()
    encoded = brotli_rs.compress(original, quality=quality, lgwin=lgwin)
    assert brotli_rs.decompress(encoded) == original

