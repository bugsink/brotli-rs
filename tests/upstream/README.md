# Upstream test provenance

Tests are grouped by their source project. Each source directory records an
immutable Git commit, the original paths, licensing, and local adaptations.
Binary corpus files are copied byte-for-byte. Adapted Python files retain their
upstream copyright headers.

The source snapshots are deliberately copied rather than fetched during a test
run. This keeps tests reproducible and lets source distributions test without
network access.

Project-specific behavior belongs in `tests/project`, not here.

