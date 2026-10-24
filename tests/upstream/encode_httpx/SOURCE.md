# encode/httpx

- Repository: <https://github.com/encode/httpx>
- Commit: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- License: BSD-3-Clause; see `LICENSE`

`test_decoder_cases.py` is adapted from the Brotli cases in
`tests/test_decoders.py`. It keeps HTTPX's fixed, independently encoded wire
vector and its empty and invalid-content cases, but exercises `brotli_rs`
directly instead of going through HTTPX's response decoder.

