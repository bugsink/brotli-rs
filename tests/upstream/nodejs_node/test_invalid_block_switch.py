import pytest

import brotli_rs


INVALID_BLOCK_SWITCH = bytes.fromhex(
    "200010414141fcffff07002228f00b60f7f41f000000"
)


def test_one_shot_rejects_invalid_block_switch():
    with pytest.raises(brotli_rs.error, match="ERROR_FORMAT_BLOCK_SWITCH"):
        brotli_rs.decompress(INVALID_BLOCK_SWITCH)


def test_streaming_rejects_invalid_block_switch():
    decoder = brotli_rs.Decompressor()

    with pytest.raises(brotli_rs.error, match="ERROR_FORMAT_BLOCK_SWITCH"):
        for byte in INVALID_BLOCK_SWITCH:
            decoder.process(bytes([byte]))
