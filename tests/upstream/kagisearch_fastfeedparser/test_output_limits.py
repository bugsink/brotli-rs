import pytest

import brotli_rs


OUTPUT_SIZE = 16 * 2**20
OUTPUT_LIMIT = 1 * 2**20


def test_decompression_bomb_is_refused_by_one_shot_limit():
    bomb = brotli_rs.compress(bytes(OUTPUT_SIZE), quality=1)
    assert len(bomb) < OUTPUT_LIMIT

    with pytest.raises(brotli_rs.error, match="max_output"):
        brotli_rs.decompress(bomb, max_output=OUTPUT_LIMIT)


def test_decompression_bomb_is_refused_across_streaming_calls():
    bomb = brotli_rs.compress(bytes(OUTPUT_SIZE), quality=1)
    decoder = brotli_rs.Decompressor(max_output=OUTPUT_LIMIT)

    with pytest.raises(brotli_rs.error, match="max_output"):
        decoder.process(bomb, output_buffer_limit=64 * 1024)
        while not decoder.is_finished():
            decoder.process(b"", output_buffer_limit=64 * 1024)

