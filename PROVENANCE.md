# Historical provenance

This snapshot binds the published `brotli` 3.0.2 crate. Its packaged source
matches `dropbox/rust-brotli@3c9a0c48b76a257b106b1c34a7baeb2fe0aaccf1`,
whose author and committer timestamp is `2018-11-05T18:49:17-08:00`.

The crate requires `brotli-decompressor ~2.0`; this reconstruction pins
`brotli-decompressor` 2.0.3, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.7, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
