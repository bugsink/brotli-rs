# nodejs/node

- Repository: <https://github.com/nodejs/node>
- Commit: `03923858417da6a87670cf4c099993dbcc6d8361`
- Original path: `test/parallel/test-zlib-invalid-input.js`
- CVE: <https://www.cve.org/CVERecord?id=CVE-2026-111497>
- License: MIT; see `LICENSE`

`test_invalid_block_switch.py` adapts the invalid-block-switch regression
introduced by the commit above. The fixed 22-byte stream is unchanged. The
one-shot and byte-at-a-time streaming cases exercise brotli-rs directly. Like
the Node.js test, both require the decoder to identify the invalid block
switch rather than continue until a later format error.

Google Brotli 1.2.0 and rust-brotli-decompressor 6.0.1 report
`BROTLI_DECODER_ERROR_FORMAT_BLOCK_LENGTH_1` for this vector, so they fail
these assertions. Their fixed releases report
`BROTLI_DECODER_ERROR_FORMAT_BLOCK_SWITCH` instead.
