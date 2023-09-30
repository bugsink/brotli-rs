# Historical provenance

This snapshot binds the published `brotli` 3.4.0 crate. Its packaged source
matches `dropbox/rust-brotli@c0c36218b2cbf7a24d23acd165fb18b9e9fb6242`,
whose author timestamp is `2023-09-29T23:28:11-07:00` and committer timestamp is
`2023-09-29T23:31:42-07:00`.

The crate requires `brotli-decompressor ~2.5`; this reconstruction pins
`brotli-decompressor` 2.5.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
