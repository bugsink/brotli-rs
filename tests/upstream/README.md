# Upstream test provenance

Tests are grouped by their source project. Each source directory records an
immutable Git commit, the original paths, licensing, and local adaptations.
Binary corpus files are copied byte-for-byte. Adapted Python files retain their
upstream copyright headers.

A copied test keeps the upstream assertions and parameters, with only the
mechanical import and fixture-path changes recorded in its source directory.
An adapted test is a new brotli-rs test derived from a behavior exercised by a
consumer's test suite. Adapted tests may remove that consumer's surrounding
HTTP or archive setup, select only cases relevant to the binding, or change a
resource size; every such change belongs in that source directory's
`SOURCE.md`. Adapted tests must not be described as wholesale copies.

The source snapshots are deliberately copied rather than fetched during a test
run. This keeps tests reproducible and lets source distributions test without
network access.

Project-specific behavior belongs in `tests/project`, not here.

