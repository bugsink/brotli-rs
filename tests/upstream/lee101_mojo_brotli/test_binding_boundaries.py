import random

import pytest

import brotli_rs


google_brotli = pytest.importorskip("brotli", reason="install the 'oracle' extra")


def _payload(size=250_000):
    record = (
        b'{"timestamp":"2026-07-29T12:00:00Z","service":"mojo-brotli",'
        b'"status":200,"message":"request complete"}\n'
    )
    return (record * (size // len(record) + 1))[:size]


@pytest.mark.parametrize("size", [32767, 32768, 32769, 1048575, 1048576, 1048577])
def test_contiguous_decoder_growth_boundaries(size):
    source = _payload(size)
    encoded = google_brotli.compress(source, quality=5)
    decoded = brotli_rs.decompress(encoded)
    assert type(decoded) is bytes
    assert decoded == source


@pytest.mark.parametrize("lgwin", [10, 12, 18, 22, 24])
def test_window_sizes_produce_interoperable_streams(lgwin):
    source = _payload(70_000)
    encoded = brotli_rs.compress(source, quality=5, lgwin=lgwin)
    assert google_brotli.decompress(encoded) == source


@pytest.mark.parametrize("lgblock", [0, 16, 18, 20, 24])
def test_block_sizes_produce_interoperable_streams(lgblock):
    source = _payload(150_000)
    encoded = brotli_rs.compress(source, quality=5, lgblock=lgblock)
    assert google_brotli.decompress(encoded) == source


def test_incremental_flush_keeps_encoder_open():
    first = _payload(50_000)
    second = random.Random(1701).randbytes(40_000)
    compressor = brotli_rs.Compressor(quality=5)
    encoded = (
        compressor.process(first)
        + compressor.flush()
        + compressor.process(second)
        + compressor.flush()
        + compressor.finish()
    )
    assert google_brotli.decompress(encoded) == first + second


def test_multiple_encoder_instances_are_independent():
    left = _payload(30_000)
    right = random.Random(1702).randbytes(30_000)
    left_encoder = brotli_rs.Compressor(quality=3)
    right_encoder = brotli_rs.Compressor(quality=8)

    left_frame = left_encoder.process(left) + left_encoder.finish()
    right_frame = right_encoder.process(right) + right_encoder.finish()

    assert brotli_rs.decompress(left_frame) == left
    assert brotli_rs.decompress(right_frame) == right


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("mode", 3),
        ("quality", 12),
        ("lgwin", 9),
        ("lgwin", 25),
        ("lgblock", 15),
        ("lgblock", 25),
    ],
)
def test_invalid_settings_fail_for_streaming_and_one_shot(keyword, value):
    with pytest.raises(brotli_rs.error):
        brotli_rs.Compressor(**{keyword: value})
    with pytest.raises(brotli_rs.error):
        brotli_rs.compress(b"data", **{keyword: value})

