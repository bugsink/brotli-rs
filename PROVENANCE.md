# Historical provenance

This snapshot binds the published `brotli` 2.4.1 crate. Its packaged source
matches `dropbox/rust-brotli@2eb765813e955a135ac0abe8e700cc47b7e69ae7`,
whose author timestamp is `2018-06-14T00:21:49-07:00` and committer timestamp is
`2018-06-14T00:21:59-07:00`.

The crate requires `brotli-decompressor ~1.3`; this reconstruction pins
`brotli-decompressor` 1.3.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.1, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
