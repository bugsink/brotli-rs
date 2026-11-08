# Copyright (c) 2026 Patrik Wenger. MIT license; see LICENSE.
"""Input/output split and limit tests adapted from tests/push.rs."""

import pytest

import brotli
import brotli_rs

from ._helpers import DATA, STREAMS, decode_fragmented


SCHEDULES = [(2**30, None), (17, None), (2**30, 29), (3000, 5000), (1, 7)]


def text(length):
    words = [
        b"brotli ", b"window ", b"meta-block ", b"literal ", b"context ",
        b"copy ", b"the ", b"of ", b"distance\n", b"decoder, ", b"Huffman ",
        b"code ",
    ]
    state = 0x9E3779B9
    output = bytearray()
    while len(output) < length:
        state = (state * 1_664_525 + 1_013_904_223) & 0xFFFFFFFF
        output.extend(words[(state >> 28) % len(words)])
    return bytes(output[:length])


def corruptions(encoded):
    length = len(encoded)
    for position in (0, 1, 2, 3, 5, length // 4, length // 3,
                     length // 2, length * 2 // 3, length - 1):
        for bit in (0, 3, 6):
            flipped = bytearray(encoded)
            flipped[min(position, length - 1)] ^= 1 << bit
            yield bytes(flipped)
    for cut in (1, length // 3, length // 2, length - 1):
        yield encoded[:cut]
    yield encoded + b"\0"


def outcome(encoded, chunk_size, output_limit):
    try:
        output, finished = decode_fragmented(
            encoded, chunk_size, output_limit, max_output=1 << 20
        )
    except brotli_rs.error as error:
        return "error", str(error)
    # A process() call that errors cannot return its partial output, so the
    # amount emitted before an error depends on the split. Successful output
    # and the final error/unfinished state must still agree.
    return ("finished", output) if finished else ("truncated", None)


@pytest.mark.parametrize("path", STREAMS, ids=lambda path: path.stem)
def test_corruption_outcome_is_independent_of_input_and_output_splits(path):
    encoded = path.read_bytes()
    for index, corrupted in enumerate(corruptions(encoded)):
        whole = outcome(corrupted, 2**30, None)
        for chunk_size, output_limit in SCHEDULES[1:4]:
            assert outcome(corrupted, chunk_size, output_limit) == whole, (
                f"corruption {index}, input={chunk_size}, output={output_limit}"
            )


@pytest.mark.parametrize("quality", [0, 3, 5])
@pytest.mark.parametrize("limit", [0, 1, 50_000, 99_999, 100_000])
@pytest.mark.parametrize("schedule", SCHEDULES[:4])
def test_output_limit_across_splits(quality, limit, schedule):
    payload = text(100_000)
    encoded = brotli.compress(payload, quality=quality)
    chunk_size, output_limit = schedule
    if limit < len(payload):
        with pytest.raises(brotli_rs.error, match="max_output"):
            brotli_rs.decompress(encoded, max_output=limit)
        with pytest.raises(brotli_rs.error, match="max_output"):
            decode_fragmented(encoded, chunk_size, output_limit, max_output=limit)
    else:
        assert brotli_rs.decompress(encoded, max_output=limit) == payload
        decoded = decode_fragmented(
            encoded, chunk_size, output_limit, max_output=limit
        )
        assert decoded == (payload, True)


def test_output_is_available_within_a_meta_block():
    # Keep Burli's original >1/4 assertion. This caught the wrapper returning
    # before collecting output already held by the decoder; see SOURCE.md.
    payload = (DATA / "within_meta_block.raw").read_bytes()
    encoded = (DATA / "within_meta_block.br").read_bytes()
    decoder = brotli_rs.Decompressor()
    output = decoder.process(encoded[:len(encoded) // 2])
    assert len(output) > len(payload) // 4
    assert payload.startswith(output)
    assert not decoder.is_finished()
    assert output + decoder.process(encoded[len(encoded) // 2:]) == payload
    assert decoder.is_finished()
