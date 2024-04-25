# Historical provenance

This snapshot binds the published `brotli` 6.0.0 crate. Its packaged source
matches `dropbox/rust-brotli@8e0b2a87608a6db12c5d66102ec77857a3c8a131`,
whose author timestamp is `2024-04-25T12:58:42-04:00` and committer timestamp is
`2024-05-04T09:30:05-07:00`.

The crate requires `brotli-decompressor ~4.0`; this reconstruction pins
`brotli-decompressor` 4.0.0, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.1.0, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
