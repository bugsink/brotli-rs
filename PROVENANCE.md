# Historical provenance

This snapshot binds the published `brotli` 3.0.1 crate. Its packaged source
matches `dropbox/rust-brotli@c2b73b98c44b3ea91177eae522e72db4e38561ee`,
whose author and committer timestamp is `2018-11-05T17:25:20-08:00`.

The crate requires `brotli-decompressor ~2.0`; this reconstruction pins
`brotli-decompressor` 2.0.3, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.7, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
