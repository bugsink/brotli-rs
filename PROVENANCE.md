# Historical provenance

This snapshot binds the published `brotli` 2.2.0 crate. Its packaged source
matches `dropbox/rust-brotli@a58fb3843200ca491114e3bf55c2a64c0953400f`,
whose author timestamp is `2018-05-17T23:40:38-07:00` and committer timestamp is
`2018-05-17T23:42:10-07:00`.

The crate requires `brotli-decompressor ~1.3`; this reconstruction pins
`brotli-decompressor` 1.3.1, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.1, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
