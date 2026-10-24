# brotli-rs

Python bindings for Dropbox's safe-Rust
[`brotli`](https://github.com/dropbox/rust-brotli) crate.

The public API follows the `Brotli` Python package where that can be done
without inheriting its C extension. The distribution and import names are
both `brotli-rs` / `brotli_rs`, deliberately avoiding a collision with the
existing `brotli` module.

```python
import brotli_rs as brotli

compressed = brotli.compress(b"hello")
assert brotli.decompress(compressed) == b"hello"
```

Streaming compression and decompression are available through `Compressor`
and `Decompressor`. `Decompressor.process()` supports a strict
`output_buffer_limit`, and both streaming and one-shot decompression accept an
optional `max_output` limit.

```python
decoder = brotli.Decompressor(max_output=16 * 1024 * 1024)
parts = []
for compressed_chunk in source:
    while not decoder.is_finished() and not decoder.can_accept_more_data():
        parts.append(decoder.process(b"", output_buffer_limit=64 * 1024))
    parts.append(decoder.process(compressed_chunk, output_buffer_limit=64 * 1024))
while not decoder.is_finished() and not decoder.can_accept_more_data():
    parts.append(decoder.process(b"", output_buffer_limit=64 * 1024))
if not decoder.is_finished():
    raise brotli.error("incomplete stream")
```

The compatibility surface consists of `compress`, `decompress`,
`Compressor.process()` / `.flush()` / `.finish()`,
`Decompressor.process()` / `.can_accept_more_data()` / `.is_finished()`, the
three `MODE_*` constants, `error`, `version`, and `__version__`. Contiguous
buffer-protocol inputs are accepted. `version` is a string alias of
`__version__`, as it is in the current `Brotli` package.

Compressed bytes are not promised to be byte-identical to Google's encoder.
They are Brotli-compatible streams, tested in both directions against Google
Brotli 1.2.1. Exception text, subclassing, pickling, non-contiguous buffers,
and private implementation names are outside the compatibility contract.

The base package version tracks the Rust `brotli` crate exactly.
Python-binding-only fixes use PEP 440 post releases, such as `9.0.0.post1`,
while still pinning `brotli = 9.0.0`.

## Why?

What do you think is more secure? World class engineers working at one of
the world's largest tech companies trying to juggle chainsaws in their spare
time, or an entirely vibe-coded wrapper in a memory-safe language with a Rust
crate on the inside?

If you bet on the latter, you've come to the right place.

## Development

Install Rust and Python 3.11 or newer, then:

```console
python -m venv .venv
. .venv/bin/activate
python -m pip install maturin
maturin develop --extras=test
pytest
```

See `tests/upstream/README.md` for the provenance of imported and adapted
upstream tests.

