"""Public-API adaptations of Burli's fragmented decoder tests."""

from pathlib import Path

import brotli_rs


DATA = Path(__file__).with_name("testdata")
STREAMS = sorted(DATA.glob("*.br"))
assert len(STREAMS) == 21, "missing Burli regression fixtures"


def decode_fragmented(encoded, chunk_size, output_limit=None, max_output=None):
    decoder = brotli_rs.Decompressor(max_output=max_output)
    output = []
    total = 0
    for offset in range(0, len(encoded), chunk_size):
        chunk = decoder.process(
            encoded[offset : offset + chunk_size],
            output_buffer_limit=output_limit,
        )
        assert output_limit is None or len(chunk) <= output_limit
        total += len(chunk)
        assert max_output is None or total <= max_output
        output.append(chunk)
        while not decoder.can_accept_more_data():
            chunk = decoder.process(b"", output_buffer_limit=output_limit)
            assert chunk or decoder.can_accept_more_data(), "decoder made no progress"
            assert output_limit is None or len(chunk) <= output_limit
            total += len(chunk)
            assert max_output is None or total <= max_output
            output.append(chunk)
    return b"".join(output), decoder.is_finished()
