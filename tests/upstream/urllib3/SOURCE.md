# urllib3/urllib3

- Repository: <https://github.com/urllib3/urllib3>
- Commit: `8883fd900057ee65f553586389ecd70269f05e04`
- License: MIT; see `LICENSE`

`test_bounded_streaming.py` adapts the Brotli cases in
`test/test_response.py`, notably `test_chunked_decoding_brotli`, the bounded
read tests, and `test_read_chunked_with_trailing_data_does_not_hang`.
HTTPResponse setup was removed so the same stresses apply directly to the
binding's `output_buffer_limit`, `can_accept_more_data()`, and pending-input
contract.

