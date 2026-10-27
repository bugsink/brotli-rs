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

`test_portable_output.py` adapts the `alice29.txt` quality-11 output assertion
from `src/bin/integration_tests.rs` at rust-brotli
`a3cb9311ac6874a379c56b62b61885cc09a5c0d1` (crate 9.1.1), together with the
platform-dependence reported in upstream issue
[#271](https://github.com/dropbox/rust-brotli/issues/271) and implemented in
upstream [PR #259](https://github.com/dropbox/rust-brotli/pull/259). It uses the
existing byte-for-byte `alice29.txt` corpus under
`tests/upstream/google_brotli/testdata` rather than keeping a second copy. This
is an adapted test, not a byte-for-byte copy: upstream pins the portable-float
compressed length at 46,496 bytes; this version drives the public Python API
and additionally pins the output digest.

