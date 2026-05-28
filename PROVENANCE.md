# Historical provenance

This snapshot binds the published `brotli` 8.0.3 crate. Its packaged source
matches `dropbox/rust-brotli@21de815f394796ef6ad2b312b7a00da2efa7b226`,
whose author and committer timestamp is `2026-05-27T20:10:01-07:00`.

The crate requires `brotli-decompressor ~5.0`; this reconstruction pins
`brotli-decompressor` 5.0.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.2.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
