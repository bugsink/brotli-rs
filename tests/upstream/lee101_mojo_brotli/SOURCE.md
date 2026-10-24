# lee101/mojo-brotli

- Repository: <https://github.com/lee101/mojo-brotli>
- Commit: `61a566e0033775cb920a23a6e2f92432a3f56646`
- License: MIT; see `LICENSE`

`test_binding_boundaries.py` adapts cases from `tests/test_parity.py`: output
allocation boundaries, compression parameter matrices, flush behavior, and
independent encoder state. Assertions that mojo-brotli's C encoder is
byte-identical to Google's encoder were changed to cross-implementation decode
assertions because brotli-rs deliberately does not promise identical encoded
bytes.

mojo-brotli's post-finish and non-contiguous-buffer expectations were not
copied because they intentionally differ from the Google `Brotli` compatibility
surface selected by brotli-rs.

