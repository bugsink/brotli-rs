# Historical provenance

This snapshot binds the published `brotli` 3.3.1 crate. Its packaged source
matches `dropbox/rust-brotli@e85e7cc8346d6bc20cf226a50aa7956e431a2805`,
whose author and committer timestamp is `2021-07-31T10:10:45-07:00`.

The crate requires `brotli-decompressor ~2.3`; this reconstruction pins
`brotli-decompressor` 2.3.2, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.9, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
