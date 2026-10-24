# kagisearch/fastfeedparser

- Repository: <https://github.com/kagisearch/fastfeedparser>
- Commit: `8683ec1381ab6ba2667765f100769b77a531d25f`
- License: MIT; see `LICENSE`

`test_output_limits.py` adapts the Brotli decompression-bomb cases in
`tests/test_decompression_limits.py`. HTTP fetching and feed parsing were
removed. The generated highly compressible input is smaller than upstream's
512 MiB case so this binding-level regression remains practical on every CI
job, while retaining the important large expansion ratio.

