# Historical provenance

This snapshot binds the published `brotli` 3.1.0 crate. Its packaged source
matches `dropbox/rust-brotli@9b756f118958c65616f4b06659177c41c14dccf2`,
whose author and committer timestamp is `2018-11-22T01:48:01-08:00`.

The crate requires `brotli-decompressor ~2.1`; this reconstruction pins
`brotli-decompressor` 2.1.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.7, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
