# Historical provenance

This snapshot binds the published `brotli` 5.0.0 crate. Its packaged source
matches `dropbox/rust-brotli@2c601f48c4b6ab107761179efa2579edb7fee8fa`,
whose author and committer timestamp is `2024-04-12T00:08:29-07:00`.

The crate requires `brotli-decompressor ~4.0`; this reconstruction pins
`brotli-decompressor` 4.0.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
