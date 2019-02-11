# Historical provenance

This snapshot binds the published `brotli` 3.2.0 crate. Its packaged source
matches `dropbox/rust-brotli@1b2a153177b021d0fa1d32519a67b10ad97f099e`,
whose author and committer timestamp is `2019-02-10T22:53:16-08:00`.

The crate requires `brotli-decompressor ~2.2`; this reconstruction pins
`brotli-decompressor` 2.2.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.7, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
