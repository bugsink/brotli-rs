# brotli-rs 1.0.6

Python bindings for Dropbox's safe-Rust `brotli` 1.0.6 crate.

This historical snapshot exposes the decompression operation supported by
that crate through the eventual `brotli_rs` API shape:

```python
import brotli_rs

decoded = brotli_rs.decompress(encoded)
```

Compression was not part of `brotli` 1.0.6 and is intentionally absent.
See `PROVENANCE.md` for the exact published crate, upstream source commit,
date, and test-oracle choice.

This project is not affiliated with Google, Dropbox, or the maintainers of
the upstream Rust crates.
