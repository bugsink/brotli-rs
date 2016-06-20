from pathlib import Path
import re

import pytest

import brotli_rs


TESTDATA = Path(__file__).parents[1] / "upstream" / "dropbox_rust_brotli" / "testdata"


def test_python_and_rust_versions_match():
    cargo = (Path(__file__).parents[2] / "Cargo.toml").read_text()
    cargo_version = re.search(
        r'^version = "([^"]+)"$', cargo, flags=re.MULTILINE
    ).group(1)
    assert brotli_rs.__version__ == cargo_version
    assert brotli_rs.version == brotli_rs.__version__


@pytest.mark.parametrize(
    "wrapper",
    [bytes, bytearray, memoryview],
)
def test_contiguous_buffer_inputs(wrapper):
    encoded = (TESTDATA / "quickfox.compressed").read_bytes()
    expected = (TESTDATA / "quickfox").read_bytes()
    assert brotli_rs.decompress(wrapper(encoded)) == expected


def test_noncontiguous_input_is_rejected():
    with pytest.raises(BufferError):
        brotli_rs.decompress(memoryview(b"abcdef")[::2])


def test_text_input_is_rejected():
    with pytest.raises(TypeError):
        brotli_rs.decompress("not bytes")
