# brotli-rs 3.1.5

Python bindings for Dropbox's safe-Rust `brotli` 3.1.5 crate.

This historical snapshot exposes compression and decompression through the
eventual `brotli_rs` API shape:

```python
import brotli_rs

encoded = brotli_rs.compress(b"some data", quality=5)
decoded = brotli_rs.decompress(encoded)
```

`Compressor` is present, but retains a buffered implementation because the
historical writer does not yet provide the output-extraction lifecycle needed
by the eventual Python streaming API.
The Rust crate does not yet provide the later incremental decoder interface,
so `Decompressor` is intentionally absent.

See `PROVENANCE.md` for the exact published crates, upstream source commit,
date, and test-oracle choice.

This project is not affiliated with Google, Dropbox, or the maintainers of
the upstream Rust crates.
