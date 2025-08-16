# Historical provenance

This snapshot binds the published `brotli` 8.0.2 crate. Its packaged source
matches `dropbox/rust-brotli@769efcbca153bfc4737f1986459da5d9d23368b8`,
whose author and committer timestamp is `2025-08-16T02:41:54-07:00`.

The crate requires `brotli-decompressor ~5.0`; this reconstruction pins
`brotli-decompressor` 5.0.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
