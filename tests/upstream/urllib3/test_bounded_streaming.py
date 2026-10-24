import pytest

import brotli_rs


def _decode_in_bounded_calls(compressed, limits):
    decoder = brotli_rs.Decompressor()
    output = []
    limit_iterator = iter(limits)
    limit = next(limit_iterator)
    output.append(decoder.process(compressed, output_buffer_limit=limit))

    for _ in range(100_000):
        if decoder.is_finished():
            return output
        assert not decoder.can_accept_more_data(), "complete input was lost"
        limit = next(limit_iterator, limit)
        output.append(decoder.process(b"", output_buffer_limit=limit))

    raise AssertionError("bounded Brotli decoding did not terminate")


def test_decoding_one_output_byte_at_a_time():
    original = b"foobarbaz"
    chunks = _decode_in_bounded_calls(brotli_rs.compress(original), [1])
    assert all(len(chunk) <= 1 for chunk in chunks)
    assert b"".join(chunks) == original


def test_large_expansion_stays_within_each_requested_limit():
    original = b"A" * (5 * 2**20)
    limits = [1024 * 1024, 1024]
    chunks = _decode_in_bounded_calls(brotli_rs.compress(original, quality=1), limits)

    assert len(chunks[0]) == limits[0]
    assert all(len(chunk) <= limits[1] for chunk in chunks[1:])
    assert b"".join(chunks) == original


def test_bounded_decode_with_trailing_data_errors_instead_of_hanging():
    compressed = brotli_rs.compress(b"A" * 100) + b"tail"
    with pytest.raises(brotli_rs.error, match="trailing data"):
        _decode_in_bounded_calls(compressed, [50])

