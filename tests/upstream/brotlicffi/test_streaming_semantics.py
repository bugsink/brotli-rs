"""Behavior adapted from python-hyper/brotlicffi's public API tests.

Source: python-hyper/brotlicffi@6fa0ca8ad8092b74590eb2b4bba0398a986784d3
Original paths: test/test_simple_compression.py,
test/test_simple_decompression.py, and test/test_compatibility.py.
"""

import pytest
from hypothesis import given, settings
from hypothesis.strategies import binary, integers, sampled_from

import brotli_rs


@given(binary(max_size=8192))
def test_compressed_data_roundtrips(data):
    assert brotli_rs.decompress(brotli_rs.compress(data)) == data


@settings(max_examples=30, deadline=None)
@given(
    data=binary(max_size=16384),
    chunk_size=integers(min_value=1, max_value=4096),
    mode=sampled_from(list(brotli_rs.BrotliEncoderMode)),
    quality=integers(min_value=0, max_value=11),
    lgwin=integers(min_value=10, max_value=24),
)
def test_streaming_compression(data, chunk_size, mode, quality, lgwin):
    compressor = brotli_rs.Compressor(mode=mode, quality=quality, lgwin=lgwin)
    chunks = [
        compressor.process(data[offset : offset + chunk_size])
        for offset in range(0, len(data), chunk_size)
    ]
    chunks.append(compressor.finish())
    assert brotli_rs.decompress(b"".join(chunks)) == data


def test_streaming_compression_flushes_are_decodable():
    compressor = brotli_rs.Compressor(quality=6)
    chunks = []
    for data in (b"alpha", b"beta" * 1000, b"omega"):
        chunks.extend((compressor.process(data), compressor.flush()))
    chunks.append(compressor.finish())
    assert brotli_rs.decompress(b"".join(chunks)) == (
        b"alpha" + b"beta" * 1000 + b"omega"
    )


@pytest.mark.parametrize("limit", [1, 7, 100, 4096])
def test_output_buffer_limit_is_strict(limit):
    original = b"".join(bytes([65 + i % 26]) * 4096 for i in range(16))
    compressed = brotli_rs.compress(original, lgwin=12)
    decompressor = brotli_rs.Decompressor()
    output = []
    data = compressed

    while not decompressor.is_finished():
        chunk = decompressor.process(data, output_buffer_limit=limit)
        data = b""
        assert len(chunk) <= limit
        output.append(chunk)

    assert b"".join(output) == original


def test_rejects_trailing_data_in_one_shot_and_streaming_apis():
    encoded = brotli_rs.compress(b"A" * 100) + b"tail"
    with pytest.raises(brotli_rs.error):
        brotli_rs.decompress(encoded)
    with pytest.raises(brotli_rs.error):
        brotli_rs.Decompressor().process(encoded)


def test_rejects_trailing_data_after_pending_output_is_drained():
    encoded = brotli_rs.compress(b"A" * 100) + b"tail"
    decompressor = brotli_rs.Decompressor()
    assert decompressor.process(encoded, output_buffer_limit=50) == b"A" * 50

    with pytest.raises(brotli_rs.error, match="trailing data"):
        while not decompressor.is_finished():
            decompressor.process(b"", output_buffer_limit=50)


def test_consumed_prefix_does_not_leave_stale_pending_input():
    original = b"".join(
        bytes([65 + (index % 26)]) * 4096 for index in range(16)
    )
    encoded = brotli_rs.compress(original, lgwin=12)
    assert len(encoded) > 64

    decompressor = brotli_rs.Decompressor()
    result = decompressor.process(encoded[:64])
    assert decompressor.can_accept_more_data()
    result += decompressor.process(encoded[64:])
    assert result == original


@pytest.mark.parametrize(
    "parameter",
    [
        {"mode": 52},
        {"quality": 52},
        {"lgwin": 52},
        {"lgblock": 52},
    ],
)
def test_bad_compressor_parameters(parameter):
    with pytest.raises(brotli_rs.error):
        brotli_rs.Compressor(**parameter)


def test_compatible_mode_names():
    assert brotli_rs.MODE_GENERIC is brotli_rs.BrotliEncoderMode.GENERIC
    assert brotli_rs.MODE_TEXT is brotli_rs.BrotliEncoderMode.TEXT
    assert brotli_rs.MODE_FONT is brotli_rs.BrotliEncoderMode.FONT

