# python-hyper/brotlicffi

- Repository: <https://github.com/python-hyper/brotlicffi>
- Commit: `6fa0ca8ad8092b74590eb2b4bba0398a986784d3`
- License: MIT; see `LICENSE`

`test_streaming_semantics.py` is adapted from
`test/test_simple_compression.py`, `test/test_simple_decompression.py`, and
`test/test_compatibility.py`. The adaptations change the import, remove
`brotlicffi`-only methods and private-attribute assertions, use generated data
instead of that project's fixtures, and exercise the stricter output limit
promised by brotli-rs.

The upstream multithreaded-sharing tests are not copied: brotli-rs does not
release the GIL during codec calls, so they would test Python scheduling rather
than the binding's codec contract.

