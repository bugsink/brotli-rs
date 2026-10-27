"""Adapt rust-brotli's portable-float quality-11 output regression.

Source: dropbox/rust-brotli@a3cb9311ac6874a379c56b62b61885cc09a5c0d1
Original path: src/bin/integration_tests.rs
Issue: https://github.com/dropbox/rust-brotli/issues/271
Implementation: https://github.com/dropbox/rust-brotli/pull/259

The upstream test pins the compressed length. This adaptation drives the
public Python API and also pins the complete output by SHA-256.
"""

from hashlib import sha256
from pathlib import Path

import brotli_rs


ALICE29 = (
    Path(__file__).parents[1] / "google_brotli" / "testdata" / "alice29.txt"
).read_bytes()


def test_quality_11_output_is_stable_across_platforms():
    compressed = brotli_rs.compress(ALICE29, quality=11, lgwin=22)

    assert len(compressed) == 46_496
    assert sha256(compressed).hexdigest() == (
        "532649848d9537bb7c3d90d6548b08d22536d3e2069d31b25fc00b57730ba331"
    )
