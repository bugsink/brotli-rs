# Historical provenance

This snapshot binds the published `brotli` 2.5.1 crate. Its packaged source
matches `dropbox/rust-brotli@6972b1d8c296f89a94bb31805afb6590b36aa4e6`,
whose author and committer timestamp is `2018-09-27T14:12:50-07:00`.

The crate requires `brotli-decompressor ~1.3`; this reconstruction pins
`brotli-decompressor` 1.3.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.6, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
