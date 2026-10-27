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
5. Generate the upstream section of the release notes from the published
   crate's recorded source commit:

   ```sh
   python scripts/upstream_release_notes.py brotli <version>
   ```

   This is deliberately sourced from `.cargo_vcs_info.json` in the crate
   archive. Upstream GitHub releases have empty notes and its tags do not cover
   every published crate version.
6. On GitHub, draft a release. In **Choose a tag**, create
   `v<python-version>` (for example `v9.0.0` or `v9.0.0.post1`) and target the
   exact commit just tested on `main`. Add the generated upstream release notes
   and publish the release.
7. When the build jobs have passed, approve the `pypi` deployment if the
   GitHub environment requires a reviewer.

## Automatic dependency releases

Dependabot keeps the two Rust dependencies together and the Google Brotli
Python package used as the test oracle separately. After CI passes for a
merged Cargo update on `main`, the Automatic Release Check workflow starts. A new
`brotli` crate version
becomes the Python and Rust package version. A decompressor-only update keeps
the Rust package version and creates the next Python `.postN` release. An
oracle-only update does not create a release.

A separate workflow squash-merges Dependabot pull requests after their entire
CI workflow succeeds. It verifies the pull-request author, repository, target
branch, and exact tested commit before merging. Because a merge made with its
`GITHUB_TOKEN` does not emit a push workflow, it explicitly dispatches CI on
the resulting `main`; that run is what can start an automatic dependency
release. Failed Dependabot updates remain open for investigation.

The workflow commits the version change, tags it, creates the GitHub release,
and explicitly dispatches the build and PyPI publication workflow for that
tag. Release notes quote the source commit message recorded in the published
crate's `.cargo_vcs_info.json` and link to that exact upstream commit. A normal
release uses `brotli`; a decompressor-only post release uses
`brotli-decompressor`. An explicit dispatch is required because GitHub does not
start another workflow from a release created with the automatic workflow's
`GITHUB_TOKEN`.
For a manually dispatched backfill whose version files are already aligned,
provide the exact tested target commit and its comparison commit. The workflow
uses that target directly instead of creating an empty version commit. It
dispatches the current build workflow from `main`, which then checks out the
historical tag; the automation therefore need not exist in the tagged source.
If GitHub's workflow token refuses to create a historical tag because that
commit contains older workflow files, an administrator may push the exact tag
first; the check verifies and reuses a tag that already points to its target.
The workflow is deliberately limited to Cargo dependency changes, so updating
the PyPI test oracle cannot publish a `brotli-rs` release.

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

Reconstructed releases below version 9 build the same artifacts but are never
submitted to PyPI. Version 9.0.0 was the first public package release, so this
guard keeps the historical GitHub record separate from the package index.
Release builds use Rust 1.85, which is both the binding's declared minimum and
new enough for the current packaging layer while still accepting syntax in the
oldest reconstructed Rust crates.

Do not move a published tag or replace files for a version already uploaded to
PyPI. Release a binding-only correction as the next `.postN` version.

