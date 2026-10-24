# Third-party licenses

This directory contains the license files shipped by every Rust crate in
`Cargo.lock`. Each directory name is the exact crate name and version.

`alloc-stdlib 0.3.0` is published from the same repository and under the same
BSD-3-Clause license as `alloc-no-stdlib`; its crate archive does not contain a
license file, so that repository's license is copied into its directory here.

The files are included in both wheels and source distributions. When
dependencies change, regenerate this directory from the locked crate archives
and review the resulting license expressions with `cargo metadata`.

