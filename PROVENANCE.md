# Historical provenance

This snapshot binds the published `brotli` 8.0.1 crate. Its packaged source
matches `dropbox/rust-brotli@a017e2d0c02ac9539be8594aaa821f864bb69669`,
whose author and committer timestamp is `2025-05-05T00:29:31-07:00`.

The crate requires `brotli-decompressor ~5.0`; this reconstruction pins
`brotli-decompressor` 5.0.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
