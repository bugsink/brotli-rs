# paddor/burli

- Repository: <https://github.com/paddor/burli>
- Commit: `94145f5efa175a9daa622c442d638abd0e23fdea`
- Package version: `0.3.8`
- License: MIT; see `LICENSE`

These are selected and adapted tests, not a wholesale copy of Burli's suite.
They run against brotli-rs's public Python API. Google comparisons use the
mandatory `Brotli` test dependency, without an optional import or network access
at test time. None of the ported cases is skipped or marked as an expected
failure.

## Conformance and corruption

`test_conformance.py` adapts `tests/c_brotli.rs`:

- `c_brotli_parameter_matrix_decodes_through_burli`, including its complete
  quality, mode, and window matrix and input fragments of 1, 17, and 4096 bytes.
  The empty and tiny payloads are omitted from this matrix because the existing
  Google tests already exercise those input shapes. HTML, CSS, JSON, JavaScript,
  and binary generators retain the upstream bytes and sizes.
- `c_brotli_truncated_and_mutated_streams_match_or_error_without_panics`, with
  all seven original payloads, qualities, modes, windows, truncation positions,
  and mutation masks. Both matrices are enabled here although Burli marks them
  `#[ignore]`. Failed pytest assertions identify the parameter combination;
  mutation output also identifies the byte position and mask.

Google's Python streaming API replaces the C FFI oracle so its output can be
bounded on corrupted input. A mutation producing more than the test's output
cap must fail with brotli-rs's corresponding `max_output`. Unlike the C
one-shot function, Google's Python API rejects trailing bytes, so we do not
need Burli's exception for strict trailing-data errors. Successful mutated
decodes must return exactly Google's output; unsuccessful ones must fail or
remain unfinished in the streaming API.

`process()` has no end-of-input operation, so a truncated stream must remain
unfinished rather than raise the EOF error required of Burli's `Read` wrapper.
One-shot truncations still must raise. Rust panics are not caught: a panic
escaping the binding fails the test.

## Independent encoder fixtures and decoder regressions

`generate_vectors.rs` preserves the fixture bit writer from
`tests/fixtures/mod.rs` and the mixed collector payload from
`tests/roundtrip.rs`. It generates the checked-in `testdata/` files using the
pinned Burli checkout. Regenerate by copying it into that checkout's
`examples/brotli_rs_vectors.rs` and running:

```
cargo run --release --example brotli_rs_vectors -- /path/to/testdata
```

The original tests and payload generators represented by these files are:

- `tests/c_brotli.rs::unused_huffman_trees_match_c_decoder`: all four literal
  and distance tree combinations, including every truncation of each stream.
- `tests/roundtrip.rs::distance_ring_survives_collector_switches` and
  `streaming_distance_ring_survives_collector_switches`: all six qualities,
  preserving the explicit 16-bit block size for the one-shot encoder.
- `tests/api.rs::q2_dictionary_after_split_meta_block_uses_global_base`,
  `q4_q5_dictionary_after_split_meta_block_uses_global_base`, and
  `stream_encoder_dictionary_after_split_meta_block_uses_global_base`.
- `tests/push.rs::push_decoder_writes_output_within_a_meta_block`: the original
  text generator and `rust-brotli` 8.0.4 `CompressorWriter` with quality 5,
  window 22, block 24, and a 4096-byte writer buffer.

`.raw` files contain the expected payloads. Collector encodings share
`collectors.raw`, and the streaming q2 dictionary encoding shares
`dictionary_q2.raw`. Every complete fixture is checked with both Google and
brotli-rs and with fragmented input and bounded output. The generator is not
run during tests and does not add a Burli runtime dependency.

`test_decoder_vectors.py` also adapts `tests/errors.rs`'s malformed byte
sequences, fuzzed empty metadata prefix, and every-prefix truncation of the
render payload. The latter uses both Google's and brotli-rs's encoders in
place of Burli's. `long_inputs_round_trip_by_window` from `tests/roundtrip.rs`
retains all original text, binary, and skewed-byte payloads, sizes, qualities,
and windows, testing both these encoders instead of Burli's. Python's integer
arithmetic explicitly wraps the xorshift state at 64 bits.

## Streaming boundaries and limits

`test_push.py` adapts `tests/push.rs`'s corruption generator, split schedules,
output-limit matrix, and within-meta-block output assertion. It applies split
corruption checks to the independent regression fixtures instead of the
upstream generated stream matrix. The original random piece sizes are replaced
by fixed pieces of the same maxima. The 1-byte input / 7-byte output schedule
is checked on valid fixtures up to 60,000 decoded bytes, retaining Burli's
size cutoff; corruption comparisons use the original first four schedules.

An errored `process()` call cannot return that call's partial output, so the
amount returned before an error depends on the split. We compare error text,
unfinished state, or complete successful output across splits, rather than
requiring identical partial output on errors. The helper also checks every
returned chunk against the per-call bound and the cumulative output limit.

### Early return found by the imported test

`test_output_is_available_within_a_meta_block` initially failed with
brotli-decompressor 6.3.0. Burli's unchanged assertion requires more than
75,000 decoded bytes after the first half of its 40,947-byte encoded fixture;
brotli-rs returned 65,536. Additional empty-input calls returned another
65,536 and then 17,829 bytes. Supplying the remainder also completed with the
correct payload. Google Brotli 1.2.1 returned 32,752 bytes on its first call
for the same fixture.

Investigation showed that all three decoders had already decoded the same
148,901 bytes. Both the Rust and Google native decoders can return
`NeedsMoreInput` while also reporting `HasMoreOutput`. Our wrapper provided a
64 KiB temporary output buffer and stopped on `NeedsMoreInput` without
checking for the remaining output. It also reported `can_accept_more_data()`
as true, so a consumer following that signal would stop collecting output
until more compressed input arrived.

The wrapper now checks for held output on this return path. It collects that
output immediately, or retains the pending-output signal when the caller's
per-call limit is reached. The original fixture and assertion pass unchanged.
Project regression tests also cover bounded output and enforcement of the
total output limit before more input arrives.

## Python binding tests

`test_python_bindings.py` selects tests from
`bindings/python/tests/test_burli.py`: cross-decoding all qualities and the
1 KiB/default windows, parameter combinations, randomized input pieces,
flush visibility, mixed text/zeros with per-call output bounds and progress
assertions, and malformed input with persistent failure state. Imports use
`brotli_rs as burli`, and the Google dependency is mandatory. Payloads,
parameters, and random seeds are preserved.

The flush test retains all bytes returned by `process()` (upstream discards
them) and strengthens the prefix check to require every byte supplied so far
to be decodable after each flush.

## Exclusions

- Google corpus tests (`tests/google_conformance.rs`) duplicate our existing
  pinned Google corpus. Generic round trips, buffer argument validation,
  invalid parameters, lifecycle tests, trailing-data rejection, and basic
  per-call limits already have coverage here.
- Reusable one-shot contexts, raw dictionaries, caller-owned output slices,
  `validate`, custom allocators, stack-size guarantees, and retriable `Read` /
  `Write` errors have no corresponding public API in brotli-rs. Internal
  Huffman, copy, and dictionary unit tests access Burli's implementation;
  public decoder vectors are used instead of recreating those internals.
- Local web and Silesia corpus tests require files outside Burli's repository.
  Encoder ratio monotonicity asserts Burli's own quality policy. Neither is
  imported as a runnable brotli-rs test.
- Node, Ruby, JavaScript/Wasm, .NET, and concatenation APIs are outside this
  Python binding. The Python urllib3 test repeats our existing urllib3 bounded
  decoding coverage and adds a live HTTP server; it is not imported.
