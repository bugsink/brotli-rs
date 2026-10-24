"""Run the generated vectors in Google's Go test through brotli-rs.

Source: google/brotli@db24a98aed38a16de78cc05ca15cdd8dc2a0d92d
Original path: go/brotli/synth_test.go
"""

import ast
from pathlib import Path
import re

import pytest

import brotli_rs


SOURCE = Path(__file__).with_name("synth_test.go").read_text()
FUNCTION_RE = re.compile(r"^func (Test\w+)\(.*?^}\n", re.MULTILINE | re.DOTALL)
STRING_RE = r'"(?:\\.|[^"\\])*"'
OUTPUT_TOKEN_RE = re.compile(
    rf"times\(\s*(\d+)\s*,\s*({STRING_RE})\s*\)|({STRING_RE})"
)


def _go_string_bytes(literal):
    return ast.literal_eval(literal).encode("latin-1")


def _expected_output(expression):
    output = bytearray()
    consumed = []
    for match in OUTPUT_TOKEN_RE.finditer(expression):
        consumed.append(match.span())
        if match.group(1) is None:
            output.extend(_go_string_bytes(match.group(3)))
        else:
            output.extend(
                int(match.group(1)) * _go_string_bytes(match.group(2))
            )

    remainder = expression
    for start, end in reversed(consumed):
        remainder = remainder[:start] + remainder[end:]
    assert not remainder.replace("+", "").replace(",", "").strip()
    return bytes(output)


def _vectors():
    vectors = []
    for function in FUNCTION_RE.finditer(SOURCE):
        block = function.group(0)
        if "t.Skip(" in block:
            continue
        encoded_source = re.search(
            r"compressed := \[\]uint8\{(.*?)\n  \};", block, re.DOTALL
        ).group(1)
        encoded = bytes(
            int(value, 16)
            for value in re.findall(r"0x([0-9a-fA-F]+)", encoded_source)
        )
        verify = block.rsplit("verify(t,", 1)[1]
        expectation = re.search(
            r"\bcompressed,\s*(true|false),\s*(.*?)\n  \);",
            verify,
            re.DOTALL,
        )
        succeeds = expectation.group(1) == "true"
        output = (
            _expected_output(expectation.group(2)) if succeeds else None
        )
        vectors.append((function.group(1), encoded, output))
    assert len(vectors) == 45
    return vectors


VECTORS = _vectors()


@pytest.mark.parametrize(
    ("encoded", "expected"),
    [(encoded, expected) for _, encoded, expected in VECTORS],
    ids=[name for name, _, _ in VECTORS],
)
def test_synthetic_decoder_vector(encoded, expected):
    if expected is None:
        with pytest.raises(brotli_rs.error):
            brotli_rs.decompress(encoded)
    else:
        assert brotli_rs.decompress(encoded) == expected

