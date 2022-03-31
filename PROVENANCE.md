# Historical provenance

This snapshot binds the published `brotli` 3.3.4 crate. Its packaged source
matches `dropbox/rust-brotli@29e3b90b0cdecb924739ca78cbc12a260881726f`,
whose author and committer timestamp is `2022-03-31T00:03:08-07:00`.

The crate requires `brotli-decompressor ~2.3`; this reconstruction pins
`brotli-decompressor` 2.3.2, the newest matching non-yanked release available
when the crate was published. Interoperability tests use Google's PyPI
`Brotli` 1.0.9, the newest release available on that date.

The reconstruction holds current packaging tooling constant and builds with Rust
1.85, the minimum required by its PyO3 tooling. This pin also keeps historical
dependencies reproducible across snapshots.
