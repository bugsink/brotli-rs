# Copyright (c) 2026 Patrik Wenger. MIT license; see LICENSE.
"""Selected Python binding tests from paddor/burli; see SOURCE.md."""

import random

import pytest

import brotli
import brotli_rs as burli

def text(size):
    words = [b"brotli ", b"window ", b"literal ", b"context ", b"copy ", b"the\n"]
    rng = random.Random(size)
    out = bytearray()
    while len(out) < size:
        out += rng.choice(words)
    return bytes(out[:size])



def noise(size):
    return random.Random(size).randbytes(size)



PAYLOADS = {
    "empty": b"",
    "byte": b"x",
    "text": text(100_000),
    "noise": noise(50_000),
    "zeros": bytes(200_000),
    "mixed": text(30_000) + noise(20_000) + text(30_000),
}



def pieces(data, seed, largest):
    rng = random.Random(seed)
    pos = 0
    while pos < len(data):
        size = rng.randint(1, largest)
        yield data[pos : pos + size]
        pos += size



@pytest.mark.parametrize("quality", range(12))
@pytest.mark.parametrize("name", PAYLOADS)
def test_google_decodes_burli_output(name, quality):
    payload = PAYLOADS[name]
    assert brotli.decompress(burli.compress(payload, quality=quality)) == payload



@pytest.mark.parametrize(
    ("mode", "lgwin", "lgblock"),
    [(burli.MODE_TEXT, 16, 0), (burli.MODE_FONT, 10, 16), (burli.MODE_GENERIC, 24, 24)],
)
def test_compress_takes_brotli_parameters(mode, lgwin, lgblock):
    payload = PAYLOADS["mixed"]
    encoded = burli.compress(payload, mode=mode, quality=4, lgwin=lgwin, lgblock=lgblock)
    assert brotli.decompress(encoded) == payload



@pytest.mark.parametrize("quality", range(12))
@pytest.mark.parametrize("lgwin", [10, 22])
@pytest.mark.parametrize("name", PAYLOADS)
def test_decodes_google_output(name, quality, lgwin):
    payload = PAYLOADS[name]
    if quality >= 10:
        payload = payload[:10_000]
    encoded = brotli.compress(payload, quality=quality, lgwin=lgwin)
    assert burli.decompress(encoded) == payload
    decompressor = burli.Decompressor()
    decoded = b"".join(decompressor.process(piece) for piece in pieces(encoded, quality, 999))
    assert decoded == payload
    assert decompressor.is_finished()



@pytest.mark.parametrize("quality", [0, 1, 5, 11])
def test_compressor_writes_streams_in_pieces(quality):
    payload = PAYLOADS["mixed"]
    compressor = burli.Compressor(quality=quality)
    encoded = b"".join(compressor.process(piece) for piece in pieces(payload, 1, 5000))
    encoded += compressor.finish()
    assert brotli.decompress(encoded) == payload



def test_compressor_flush_makes_input_so_far_decodable():
    compressor = burli.Compressor(quality=5)
    decompressor = brotli.Decompressor()
    decoded = b""
    written = 0
    for piece in pieces(PAYLOADS["text"], 2, 20_000):
        written += len(piece)
        encoded = compressor.process(piece) + compressor.process(b"") + compressor.flush()
        decoded += decompressor.process(encoded)
        assert decoded == PAYLOADS["text"][:written]
    decoded += decompressor.process(compressor.finish())
    assert decoded == PAYLOADS["text"]
    assert decompressor.is_finished()



@pytest.mark.parametrize("limit", [1, 1000, 65536])
def test_output_buffer_limit_bounds_each_call(limit):
    payload = PAYLOADS["zeros"] + PAYLOADS["text"]
    encoded = brotli.compress(payload, quality=11)
    decompressor = burli.Decompressor()
    decoded = b""
    # The loop urllib3 runs: drain while the decoder holds input or output.
    for piece in pieces(encoded, limit, 4000):
        chunk = decompressor.process(piece, output_buffer_limit=limit)
        assert len(chunk) <= limit
        decoded += chunk
        while not decompressor.can_accept_more_data():
            chunk = decompressor.process(b"", output_buffer_limit=limit)
            assert len(chunk) <= limit
            # Each call returns output or takes in all held input.
            assert chunk or decompressor.can_accept_more_data()
            decoded += chunk
    assert decoded == payload
    assert decompressor.is_finished()



@pytest.mark.parametrize("corrupt", [b"\xff\xff\xff", b"\x11\x00"])
def test_rejects_malformed_streams(corrupt):
    with pytest.raises(burli.error):
        burli.decompress(corrupt)
    decompressor = burli.Decompressor()
    with pytest.raises(burli.error):
        decompressor.process(corrupt)
    with pytest.raises(burli.error):
        decompressor.process(b"")
