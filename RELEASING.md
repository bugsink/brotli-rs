# Releasing reconstructed versions

Each commit on `historic-versions` is a complete historical snapshot. Its
author and committer dates match the corresponding upstream Rust source
commit, and its `v<version>` tag points to that exact snapshot.

Historical GitHub releases build wheels and a source distribution but are
never published to PyPI. Version 9.0.0 remains the first PyPI release.
