# Historical provenance

This snapshot binds the published `brotli` 3.1.6 crate. Its packaged source
matches `dropbox/rust-brotli@d01b04daace387ab06da7b259358d137312a8efb`,
whose author timestamp is `2019-01-14T13:05:27-08:00` and committer timestamp is
`2019-01-14T13:05:41-08:00`.

The crate requires `brotli-decompressor ~2.1`; this reconstruction pins
`brotli-decompressor` 2.1.2, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.7, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
