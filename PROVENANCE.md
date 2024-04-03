# Historical provenance

This snapshot binds the published `brotli` 4.0.0 crate. Its packaged source
matches `dropbox/rust-brotli@c9afcec684d5c7b37bab624dd7d6961719b6cfc4`,
whose author and committer timestamp is `2024-04-03T00:57:48-07:00`.

The crate requires `brotli-decompressor ~3.0`; this reconstruction pins
`brotli-decompressor` 3.0.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
