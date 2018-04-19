# Historical provenance

This snapshot binds the published `brotli` 2.0.1 crate. Its packaged source
matches `dropbox/rust-brotli@569fa32e9a3fad7c368d99745f018f8d5ccbc6c9`,
whose author and committer timestamp is `2018-04-19T01:50:06-07:00`.

The crate requires `brotli-decompressor ~1.2`; this reconstruction pins
`brotli-decompressor` 1.2.1, the newest matching non-yanked release available
when the source commit was made. Interoperability tests use Google's PyPI
`Brotli` 1.0.1, the newest release available on that date.

The binding builds with Rust 1.85, the minimum required by its current PyO3
tooling. Newer Rust releases reject macro syntax accepted by the historical
crate, so CI and release builds deliberately pin 1.85 for this snapshot.
