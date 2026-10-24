# rustls/rustls

- Repository: <https://github.com/rustls/rustls>
- Commit: `07477355db64854d58dee1ab890236f226c5ab8a`
- Original path: `rustls/src/compress.rs`
- Security advisory: <https://rustsec.org/advisories/RUSTSEC-2026-0348.html>
- License: MIT, selected from Apache-2.0 OR ISC OR MIT; see `LICENSE-MIT`

`test_large_window.py` adapts `test_brotli_rejects_large_window`, introduced
by the commit above. The fixed two-byte large-window stream is unchanged. The
rustls certificate-decompressor call is replaced with brotli-rs's one-shot and
streaming Python APIs, and the upstream check showing that the permissive Rust
API accepts the extension is omitted because brotli-rs does not expose that
API.
