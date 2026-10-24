# getsentry/sentry-python

- Repository: <https://github.com/getsentry/sentry-python>
- Commit: `9e4ba4c0248a5c7c6c89b61c61aac20d1c8d8d8f`
- License: MIT; see `LICENSE`

`test_transport_payload.py` adapts the Brotli path in
`sentry_sdk/transport.py::_serialize_envelope` and the compression cases in
`tests/test_transport.py`. It uses Sentry envelope framing and the SDK's
default Brotli quality of 4, while avoiding a test dependency on the SDK.

