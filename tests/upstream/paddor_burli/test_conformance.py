# Copyright (c) 2026 Patrik Wenger. MIT license; see LICENSE.
"""Adapted from tests/c_brotli.rs at the commit recorded in SOURCE.md."""

import pytest

import brotli
import brotli_rs

from ._helpers import decode_fragmented


INPUTS = {
    "html": (
        b'<!doctype html><main class="card"><h1>Burli</h1>'
        b'<p data-id="42">decode conformance</p></main>'
    ) * 16,
    "css": (
        b".card{display:grid;grid-template-columns:repeat(auto-fit,"
        b"minmax(16rem,1fr));gap:1rem;color:#1b1f23}"
    ) * 32,
    "json": (
        b'{"items":[{"name":"burli","kind":"brotli","ok":true},'
        b'{"name":"decoder","kind":"crate","ok":true}]}'
    ) * 32,
    "js": (
        b'export function render(items){return items.map((item)=>'
        b'`<li data-id="${item.id}">${item.name}</li>`).join("")}'
    ) * 32,
    "binary": bytes(index * 37 % 251 for index in range(4096)),
}


@pytest.mark.parametrize("name", INPUTS)
@pytest.mark.parametrize("quality", range(12))
@pytest.mark.parametrize("mode", range(3))
@pytest.mark.parametrize("lgwin", [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24])
def test_c_parameter_matrix(name, quality, mode, lgwin):
    payload = INPUTS[name]
    encoded = brotli.compress(payload, quality=quality, mode=mode, lgwin=lgwin)
    assert brotli_rs.decompress(encoded) == payload
    for chunk_size in (1, 17, 4096):
        assert decode_fragmented(encoded, chunk_size) == (payload, True)


@pytest.mark.parametrize("name", ["empty", "tiny", *INPUTS])
@pytest.mark.parametrize("quality", [0, 1, 5, 9, 11])
@pytest.mark.parametrize("mode", range(3))
@pytest.mark.parametrize("lgwin", [10, 16, 22])
def test_truncated_and_mutated_streams_match_c(name, quality, mode, lgwin):
    payload = {"empty": b"", "tiny": b"a", **INPUTS}[name]
    encoded = brotli.compress(payload, quality=quality, mode=mode, lgwin=lgwin)
    length = len(encoded)
    cuts = range(length) if length <= 512 else sorted(
        {0, 1, length // 4, length // 2, length * 3 // 4, length - 1}
    )
    for cut in cuts:
        truncated = encoded[:cut]
        with pytest.raises(brotli_rs.error):
            brotli_rs.decompress(truncated, max_output=65536)
        # process() has no EOF operation: incomplete input must stay unfinished.
        output, finished = decode_fragmented(truncated, 17, max_output=65536)
        assert not finished, f"accepted truncation at {cut}/{length}"
        assert payload.startswith(output)

    positions = sorted({0, length // 4, length // 2, length * 3 // 4, length - 1})
    maximum = len(payload) * 4 + 1024
    for position in positions:
        for mask in (0x01, 0x55, 0xFF):
            mutated = bytearray(encoded)
            mutated[position] ^= mask
            label = f"position={position}, mask={mask:#04x}, bytes={mutated.hex()}"
            try:
                # Bound the independent oracle too: corrupt lengths can expand.
                oracle = brotli.Decompressor()
                expected = oracle.process(
                    bytes(mutated), output_buffer_limit=maximum + 1
                )
                accepted = oracle.is_finished() and len(expected) <= maximum
            except brotli.error:
                accepted = False

            if accepted:
                decoded = brotli_rs.decompress(mutated, max_output=maximum)
                assert decoded == expected, label
                streamed = decode_fragmented(mutated, 17, max_output=maximum)
                assert streamed == (expected, True), label
            else:
                with pytest.raises(brotli_rs.error):
                    brotli_rs.decompress(mutated, max_output=maximum)
                try:
                    _, finished = decode_fragmented(mutated, 17, max_output=maximum)
                except brotli_rs.error:
                    pass
                else:
                    assert not finished, label
