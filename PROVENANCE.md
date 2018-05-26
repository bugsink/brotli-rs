# Historical provenance

This snapshot binds the published `brotli` 2.3.0 crate. Its packaged source
matches `dropbox/rust-brotli@e978bb10940a064cda90f2b9179ae0d60bc6f6b0`,
whose author and committer timestamp is `2018-05-26T01:20:53-07:00`.

The crate requires `brotli-decompressor ~1.3`; this reconstruction pins
`brotli-decompressor` 1.3.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.1, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
