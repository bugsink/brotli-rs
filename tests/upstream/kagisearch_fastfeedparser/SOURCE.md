# kagisearch/fastfeedparser

- Repository: <https://github.com/kagisearch/fastfeedparser>
- Commit: `8683ec1381ab6ba2667765f100769b77a531d25f`
- License: MIT; see `LICENSE`

`test_output_limits.py` adapts the Brotli decompression-bomb cases in
`tests/test_decompression_limits.py`. HTTP fetching and feed parsing were
removed. The generated highly compressible output is deliberately reduced
from upstream's 512 MiB to 16 MiB, with the rejection limit reduced from its
configured response limit to 1 MiB. This keeps the binding-level regression
practical on every platform in the CI matrix while retaining a large expansion
ratio and proving that `max_output` stops it well before full materialization.

