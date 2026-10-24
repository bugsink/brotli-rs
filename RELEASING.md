# Releasing

The Python base version follows the pinned `brotli` crate version. Keep these
three values aligned for a new upstream release:

- `[project].version` in `pyproject.toml`
- `[package].version` and `brotli = "=<version>"` in `Cargo.toml`
- `Cargo.lock`

For a binding-only fix, change only the Python version to a PEP 440 post
release such as `9.0.0.post1`.

## One-time PyPI setup

The release workflow uses PyPI Trusted Publishing and needs no password or API
token in GitHub. In PyPI, create a pending publisher for:

- PyPI project: `brotli-rs`
- GitHub owner: `bugsink`
- GitHub repository: `brotli-rs`
- Workflow: `release.yml`
- Environment: `pypi`

Create the matching `pypi` environment in the GitHub repository. Requiring a
reviewer for that environment gives publication an explicit approval step.

See <https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/>
for PyPI's current first-release instructions.

## Each release

1. Update versions and dependencies as described above.
2. Run `cargo fmt --check`, `cargo clippy --locked --all-targets -- -D warnings`,
   and `pytest`.
3. Build locally with `maturin build --release --locked --sdist` and run
   `twine check dist/*`.
4. Commit the release changes and push `main`.
5. Create a GitHub release whose tag is `v<python-version>`, for example
   `v9.0.0` or `v9.0.0.post1`.

Publishing the GitHub release builds the platform wheels and source
distribution, then uploads them to PyPI through Trusted Publishing.

