# Historical provenance

This snapshot binds the published `brotli` 7.0.0 crate. Its packaged source
matches `dropbox/rust-brotli@08a4a9a7496edef311ea405222854536a63c5da7`,
whose author timestamp is `2024-10-02T00:04:31-07:00` and committer timestamp is
`2024-10-02T00:05:25-07:00`.

The crate requires `brotli-decompressor ~4.0`; this reconstruction pins
`brotli-decompressor` 4.0.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
