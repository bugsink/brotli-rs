# Historical provenance

This snapshot binds the published `brotli` 1.0.6 crate. Its packaged source
matches `dropbox/rust-brotli@61cc75ce7e7004a07b6e48c60e8bf9358104a05b`,
whose author and committer timestamp is `2016-06-20T14:38:28-07:00`.

Version 1.0.6 contains the decoder directly and has no separate
`brotli-decompressor` dependency. Google's `Brotli` Python distribution was
not yet available on PyPI on this date, so tests use the known-input and
known-output vector included in the published Rust crate.

The binding builds with Rust 1.85, the minimum required by its current PyO3
tooling. Newer Rust releases reject macro syntax accepted by the historical
crate, so CI and release builds deliberately pin 1.85 for this snapshot.
