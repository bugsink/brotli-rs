# Historical provenance

This snapshot binds the published `brotli` 2.1.0 crate. Its packaged source
matches `dropbox/rust-brotli@796e8a6dc41c06d6bd3d2cd1b069386ed3818778`,
whose author and committer timestamp is `2018-05-02T12:15:54-07:00`.

The crate requires `brotli-decompressor ~1.3`; this reconstruction pins
`brotli-decompressor` 1.3.0, the newest matching non-yanked release available
when the source commit was made. Interoperability tests use Google's PyPI
`Brotli` 1.0.1, the newest release available on that date.

The binding builds with Rust 1.85, the minimum required by its current PyO3
tooling. Newer Rust releases reject macro syntax accepted by the historical
crate, so CI and release builds deliberately pin 1.85 for this snapshot.
