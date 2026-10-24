import random

import pytest

import brotli_rs


RNG = random.Random(4211)
PAYLOAD = b"".join(
    b"line %d of the arrived-feed payload\n" % index for index in range(500)
) + RNG.randbytes(3000)
JUNK = b"appended signature\n"


@pytest.mark.parametrize(
    "position", ["header", "near-start", "middle", "last-byte"]
)
def test_cut_streams_are_rejected(position):
    compressed = brotli_rs.compress(PAYLOAD, quality=5)
    cut = {
        "header": 1,
        "near-start": 50,
        "middle": len(compressed) // 2,
        "last-byte": -1,
    }[position]
    with pytest.raises(brotli_rs.error):
        brotli_rs.decompress(compressed[:cut])


@pytest.mark.parametrize("trailing", [JUNK, bytes(64)], ids=["junk", "zeros"])
def test_bytes_after_the_stream_are_rejected(trailing):
    compressed = brotli_rs.compress(PAYLOAD, quality=5)
    with pytest.raises(brotli_rs.error, match="trailing data"):
        brotli_rs.decompress(compressed + trailing)


def test_concatenated_streams_are_rejected():
    first = brotli_rs.compress(PAYLOAD, quality=5)
    second = brotli_rs.compress(b"second stream", quality=5)
    with pytest.raises(brotli_rs.error, match="trailing data"):
        brotli_rs.decompress(first + second)


@pytest.mark.parametrize("piece_size", [1, 7, 4096])
def test_trailing_data_is_rejected_at_any_input_boundary(piece_size):
    data = brotli_rs.compress(PAYLOAD, quality=5) + JUNK
    decoder = brotli_rs.Decompressor()

    with pytest.raises(brotli_rs.error, match="trailing data"):
        for offset in range(0, len(data), piece_size):
            decoder.process(data[offset : offset + piece_size])


def test_bit_damage_rejected_by_one_shot_is_rejected_at_any_input_boundary():
    compressed = brotli_rs.compress(PAYLOAD, quality=5)
    rejected = None
    for position in range(len(compressed) // 2, len(compressed)):
        damaged = bytearray(compressed)
        damaged[position] ^= 0xFF
        try:
            brotli_rs.decompress(damaged)
        except brotli_rs.error:
            rejected = bytes(damaged)
            break

    assert rejected is not None

    for piece_size in (1, 7, 4096):
        decoder = brotli_rs.Decompressor()
        with pytest.raises(brotli_rs.error):
            for offset in range(0, len(rejected), piece_size):
                decoder.process(rejected[offset : offset + piece_size])

