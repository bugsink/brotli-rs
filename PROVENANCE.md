# Historical provenance

This snapshot binds the published `brotli` 8.0.4 crate. Its packaged source
matches `dropbox/rust-brotli@9651aa3ebfd23be83ca14d914fba2d7c12b32d2f`,
whose author timestamp is `2026-06-14T12:05:39-07:00` and committer timestamp is
`2026-06-14T12:26:12-07:00`.

The crate requires `brotli-decompressor ~5.0`; this reconstruction pins
`brotli-decompressor` 5.0.3, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.2.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
