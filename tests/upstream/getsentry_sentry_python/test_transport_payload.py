import pytest

import brotli_rs


google_brotli = pytest.importorskip("brotli", reason="install the 'oracle' extra")


EVENT = (
    b'{"event_id":"0123456789abcdef0123456789abcdef"}\n'
    b'{"type":"event","content_type":"application/json"}\n'
    b'{"message":"l\xc3\xb6l","level":"info"}\n'
)


@pytest.mark.parametrize("quality", [0, 4, 9])
def test_sentry_envelope_one_shot_compression(quality):
    encoded = brotli_rs.compress(EVENT, quality=quality)
    assert google_brotli.decompress(encoded) == EVENT

