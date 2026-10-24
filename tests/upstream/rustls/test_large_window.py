import pytest

import brotli_rs


LARGE_WINDOW_EMPTY = bytes([0x11, 0xD0])


def test_one_shot_rejects_large_window_stream():
    with pytest.raises(brotli_rs.error):
        brotli_rs.decompress(LARGE_WINDOW_EMPTY)


def test_streaming_rejects_large_window_stream():
    decoder = brotli_rs.Decompressor()

    with pytest.raises(brotli_rs.error):
        decoder.process(LARGE_WINDOW_EMPTY)
