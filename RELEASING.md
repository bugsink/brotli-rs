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
4. Commit the release changes, push `main`, and wait for CI to pass.
5. On GitHub, draft a release. In **Choose a tag**, create
   `v<python-version>` (for example `v9.0.0` or `v9.0.0.post1`) and target the
   exact commit just tested on `main`. Add the release notes and publish the
   release.
6. When the build jobs have passed, approve the `pypi` deployment if the
   GitHub environment requires a reviewer.

The tag is the immutable identity of the source being built. The GitHub
release is the publication switch and the place for release notes. Merely
pushing the tag does not run the release workflow, and saving a draft release
does not run it either. Publishing the release creates the tag when necessary
and triggers the workflow from that tag. The workflow rejects a tag whose name
does not match the version in `pyproject.toml`.

The workflow builds the platform wheels and source distribution, retains them
as GitHub Actions artifacts, then uploads them to PyPI through Trusted
Publishing. It does not attach the wheels to the GitHub release; PyPI is the
binary distribution channel. Because the workflow listens to every
`published` release, mark a GitHub release as a pre-release only when its
package version is itself a PEP 440 pre-release.

Do not move a published tag or replace files for a version already uploaded to
PyPI. Release a binding-only correction as the next `.postN` version.

