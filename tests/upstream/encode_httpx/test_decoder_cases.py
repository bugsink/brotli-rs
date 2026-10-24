import pytest

import brotli_rs


# Fixed bytes from HTTPX rather than bytes produced by the implementation under
# test. See SOURCE.md.
HTTPX_TEST_123 = b"\x8b\x03\x80test 123\x03"


def test_fixed_http_response_vector():
    assert brotli_rs.decompress(HTTPX_TEST_123) == b"test 123"


def test_fixed_vector_one_input_byte_at_a_time():
    decoder = brotli_rs.Decompressor()
    output = b"".join(decoder.process(bytes([byte])) for byte in HTTPX_TEST_123)
    assert output == b"test 123"
    assert decoder.is_finished()


def test_empty_streaming_content_is_empty_but_incomplete():
    decoder = brotli_rs.Decompressor()
    assert decoder.process(b"") == b""
    assert not decoder.is_finished()


def test_invalid_http_response_content_raises():
    with pytest.raises(brotli_rs.error):
        brotli_rs.decompress(b"invalid")

