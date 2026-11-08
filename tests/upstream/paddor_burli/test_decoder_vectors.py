# Copyright (c) 2026 Patrik Wenger. MIT license; see LICENSE.
"""Burli decoder regressions, including independent encoder streams."""

import pytest

import brotli
import brotli_rs

from ._helpers import DATA, STREAMS, decode_fragmented


def expected_payload(path):
    if path.stem.startswith("collectors"):
        return (DATA / "collectors.raw").read_bytes()
    if path.stem == "dictionary_stream_q2":
        return (DATA / "dictionary_q2.raw").read_bytes()
    return path.with_suffix(".raw").read_bytes()


@pytest.mark.parametrize("path", STREAMS, ids=lambda path: path.stem)
def test_burli_encoded_regressions(path):
    encoded = path.read_bytes()
    expected = expected_payload(path)
    assert brotli.decompress(encoded) == expected
    assert brotli_rs.decompress(encoded) == expected
    schedules = [(1, None), (17, None), (len(encoded), 29)]
    if len(expected) <= 60_000:
        schedules.append((1, 7))
    for chunk_size, output_limit in schedules:
        assert decode_fragmented(encoded, chunk_size, output_limit) == (
            expected, True
        )


@pytest.mark.parametrize("literal", [False, True])
@pytest.mark.parametrize("distance", [False, True])
def test_truncated_unused_huffman_trees(literal, distance):
    name = f"unused_{str(literal).lower()}_{str(distance).lower()}.br"
    encoded = (DATA / name).read_bytes()
    for cut in range(len(encoded)):
        with pytest.raises(brotli_rs.error):
            brotli_rs.decompress(encoded[:cut])
        output, finished = decode_fragmented(encoded[:cut], 1)
        assert not finished
        assert b"A".startswith(output)


@pytest.mark.parametrize(
    "encoded",
    [b"", b"\x00", b"\xff", b"not brotli", b"\x06\x00", b"\x06\x01",
     b"\x21\x03\x20\x00\x08h"],
    ids=["empty", "zero", "ff", "text", "empty-trailing-zero",
         "empty-trailing-one", "truncated-stored"],
)
def test_malformed_inputs(encoded):
    with pytest.raises(brotli_rs.error):
        brotli_rs.decompress(encoded)
    for size in (1, 7, 64):
        try:
            _, finished = decode_fragmented(encoded, size)
        except brotli_rs.error:
            pass
        else:
            assert not finished


def test_fuzz_empty_metadata_prefix():
    # errors.rs: stream_decoder_matches_one_shot_on_fuzz_empty_metadata_prefix.
    encoded = b"\x0c\x03"
    assert brotli.decompress(encoded) == b""
    assert brotli_rs.decompress(encoded) == b""
    assert decode_fragmented(encoded, 1) == (b"", True)


@pytest.mark.parametrize("quality", range(6))
def test_every_truncation_of_render_payload(quality):
    payload = (
        b"function render(items){return items.map((item)=>item.name).join(',')};"
    ) * 512
    # errors.rs used Burli's encoder; exercise our encoder and Google's here.
    for codec in (brotli, brotli_rs):
        encoded = codec.compress(payload, quality=quality)
        for cut in range(len(encoded)):
            with pytest.raises(brotli_rs.error):
                brotli_rs.decompress(encoded[:cut])
            output, finished = decode_fragmented(encoded[:cut], 17)
            assert not finished
            assert payload.startswith(output)


def long_payloads():
    text = (DATA / "collectors.raw").read_bytes() * 2
    binary = bytes(value for index in range(150_000)
                   for value in ((index * 7 % 251), 0, index % 13, 0))
    state = 0x9E3779B97F4A7C15
    skewed = bytearray()
    for _ in range(700_000):
        state ^= (state << 13) & 0xFFFFFFFFFFFFFFFF
        state ^= state >> 7
        state ^= (state << 17) & 0xFFFFFFFFFFFFFFFF
        skewed.append(0x80 | (state & (state >> 8) & 0xFF))
    return {"text": text, "binary": binary, "skewed": bytes(skewed)}


LONG_PAYLOADS = long_payloads()


@pytest.mark.parametrize("name", LONG_PAYLOADS)
@pytest.mark.parametrize("lgwin", [16, 17, 18, 22])
@pytest.mark.parametrize("quality", range(3))
def test_long_inputs_across_windows(name, lgwin, quality):
    payload = LONG_PAYLOADS[name]
    for codec in (brotli, brotli_rs):
        encoded = codec.compress(payload, quality=quality, lgwin=lgwin)
        assert brotli.decompress(encoded) == payload
        assert brotli_rs.decompress(encoded) == payload
        assert decode_fragmented(encoded, 4096, 5000) == (payload, True)
