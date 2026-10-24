import pytest
from hypothesis import given, settings
from hypothesis.strategies import binary, integers

import brotli_rs


def test_zero_output_limit_retains_input_until_drained():
    encoded = brotli_rs.compress(b"A" * 1000)
    decompressor = brotli_rs.Decompressor()
    assert decompressor.process(encoded, output_buffer_limit=0) == b""
    assert not decompressor.can_accept_more_data()

    output = []
    while not decompressor.is_finished():
        output.append(decompressor.process(b"", output_buffer_limit=11))
    assert b"".join(output) == b"A" * 1000


def test_exact_output_limit_does_not_claim_zero_length_output_is_pending():
    original = b"A" * 8192
    encoded = brotli_rs.compress(original)
    decompressor = brotli_rs.Decompressor()

    assert decompressor.process(encoded, output_buffer_limit=8192) == original
    assert decompressor.can_accept_more_data() or decompressor.is_finished()

    if not decompressor.is_finished():
        assert decompressor.process(b"", output_buffer_limit=8192) == b""
        assert decompressor.is_finished()


def test_finished_decompressor_accepts_empty_input():
    decompressor = brotli_rs.Decompressor()
    assert decompressor.process(brotli_rs.compress(b"done")) == b"done"
    assert decompressor.is_finished()
    assert decompressor.can_accept_more_data()
    assert decompressor.process(b"") == b""
    assert decompressor.can_accept_more_data()


def test_new_input_is_rejected_while_output_is_pending():
    encoded = brotli_rs.compress(b"A" * 1000)
    decompressor = brotli_rs.Decompressor()
    decompressor.process(encoded, output_buffer_limit=1)
    assert not decompressor.can_accept_more_data()
    with pytest.raises(brotli_rs.error, match="cannot accept more data"):
        decompressor.process(b"new input", output_buffer_limit=1)


def test_max_output_applies_across_streaming_calls():
    encoded = brotli_rs.compress(b"A" * 1000)
    decompressor = brotli_rs.Decompressor(max_output=999)
    with pytest.raises(brotli_rs.error, match="max_output"):
        for byte in encoded:
            decompressor.process(bytes([byte]))


def test_compressor_lifecycle():
    compressor = brotli_rs.Compressor()
    prefix = compressor.process(b"payload")
    suffix = compressor.finish()
    assert brotli_rs.decompress(prefix + suffix) == b"payload"
    with pytest.raises(brotli_rs.error, match="already been finished"):
        compressor.process(b"more")
    assert compressor.process(b"") == b""
    assert compressor.flush() == b""
    assert compressor.finish() == b""


@settings(max_examples=40, deadline=None)
@given(
    data=binary(max_size=32768),
    input_chunk=integers(min_value=1, max_value=1024),
    output_limit=integers(min_value=1, max_value=1024),
)
def test_random_input_and_output_boundaries(data, input_chunk, output_limit):
    encoded = brotli_rs.compress(data, quality=3)
    decompressor = brotli_rs.Decompressor()
    output = []
    offset = 0

    while not decompressor.is_finished():
        chunk = b""
        if decompressor.can_accept_more_data() and offset < len(encoded):
            chunk = encoded[offset : offset + input_chunk]
            offset += len(chunk)
        result = decompressor.process(
            chunk, output_buffer_limit=output_limit
        )
        assert len(result) <= output_limit
        output.append(result)

    assert offset == len(encoded)
    assert b"".join(output) == data

