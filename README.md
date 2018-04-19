# brotli-rs 2.0.1

Python bindings for Dropbox's safe-Rust `brotli` 2.0.1 crate.

This historical snapshot exposes compression and decompression through the
eventual `brotli_rs` API shape:

```python
import brotli_rs

encoded = brotli_rs.compress(b"some data", quality=5)
decoded = brotli_rs.decompress(encoded)
```

`Compressor` is present, but buffers input until `finish()` because this
crate's streaming writer cannot accept the complete eventual parameter set.
The Rust crate does not yet provide the later incremental decoder interface,
so `Decompressor` is intentionally absent.

See `PROVENANCE.md` for the exact published crates, upstream source commit,
date, and test-oracle choice.

This project is not affiliated with Google, Dropbox, or the maintainers of
the upstream Rust crates.
