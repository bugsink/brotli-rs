# Historical provenance

This snapshot binds the published `brotli` 3.5.0 crate. Its packaged source
matches `dropbox/rust-brotli@b9a4857b18b21c9d49760bcaa2ff2eb39c9d9e74`,
whose author and committer timestamp is `2024-03-16T20:25:01-07:00`.

The crate requires `brotli-decompressor ~2.5`; this reconstruction pins
`brotli-decompressor` 2.5.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
