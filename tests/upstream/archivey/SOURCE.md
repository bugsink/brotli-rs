# archivey-dev/archivey

- Repository: <https://github.com/archivey-dev/archivey>
- Commit: `d7a7cb75d3a38d2262c293e772bbc42096220d6e`
- License: MIT; see `LICENSE`

`test_malformed_streams.py` adapts Brotli cases and case generation from
`tests/test_arrived_codec_input.py`, `tests/test_stream_trailing_data.py`, and
`tests/test_cve_regressions_codecs.py`. Archive-reader setup and diagnostics
were removed. The remaining tests directly cover cuts at different positions,
bit damage, concatenated streams, trailing bytes, and chunk-boundary-independent
rejection.

