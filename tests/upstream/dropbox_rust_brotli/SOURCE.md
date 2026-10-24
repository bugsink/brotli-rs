# dropbox/rust-brotli

- Repository: <https://github.com/dropbox/rust-brotli>
- Tag: `9.0.0`
- Commit: `a51b65e75f68e3485be12bc816118e523e95647d`
- License: BSD-3-Clause AND MIT; see both license files

The three files in `testdata/` are byte-for-byte copies of their namesakes in
the upstream `testdata/` directory. They cover input shapes not present in the
Google corpus. `test_encoder_vectors.py` adapts round-trip cases from
`src/enc/test.rs` and `src/bin/integration_tests.rs`; output-size assertions
are intentionally omitted because Python API compatibility does not promise
byte-identical encoding.

