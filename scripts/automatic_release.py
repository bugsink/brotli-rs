#!/usr/bin/env python3
"""Prepare a release after a Cargo dependency update on main."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from upstream_release_notes import release_notes


ROOT = Path(
    os.environ.get("AUTOMATIC_RELEASE_ROOT", Path(__file__).resolve().parent.parent)
).resolve()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def cargo_value(path: str, name: str, commit: str | None = None) -> str:
    if commit is None:
        text = (ROOT / path).read_text()
    else:
        text = git("show", f"{commit}:{path}")
    match = re.search(rf"^{re.escape(name)}\s*=\s*\"([^\"]+)\"$", text, re.MULTILINE)
    if match is None:
        raise SystemExit(f"could not find {name!r} in {path}")
    return match.group(1)


def dependency_version(path: str, dependency: str, commit: str | None = None) -> str:
    if commit is None:
        text = (ROOT / path).read_text()
    else:
        text = git("show", f"{commit}:{path}")
    match = re.search(
        rf"^\s*{re.escape(dependency)}\s*=\s*\"=([^\"]+)\"$",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise SystemExit(f"could not find pinned {dependency!r} in {path}")
    return match.group(1)


def replace_project_version(version: str) -> None:
    path = ROOT / "pyproject.toml"
    text = path.read_text()
    updated, count = re.subn(
        r'(?m)^(version\s*=\s*)"[^"]+"$',
        rf'\1"{version}"',
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("could not find the project version in pyproject.toml")
    path.write_text(updated)


def replace_cargo_package_version(version: str) -> None:
    path = ROOT / "Cargo.toml"
    text = path.read_text()
    package, separator, rest = text.partition("\n[")
    if not separator:
        raise SystemExit("could not find the Cargo.toml package section")
    updated, count = re.subn(
        r'(?m)^(version\s*=\s*)"[^"]+"$',
        rf'\1"{version}"',
        package,
        count=1,
    )
    if count != 1:
        raise SystemExit("could not find the package version in Cargo.toml")
    path.write_text(updated + separator + rest)


def next_post(version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)(?:\.post(\d+))?", version)
    if match is None:
        raise SystemExit(f"cannot calculate a post release from {version!r}")
    number = int(match.group(2) or "0") + 1
    return f"{match.group(1)}.post{number}"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: automatic_release.py <previous-commit>")

    previous = sys.argv[1]
    old_brotli = dependency_version("Cargo.toml", "brotli", previous)
    new_brotli = dependency_version("Cargo.toml", "brotli")
    old_decompressor = dependency_version(
        "Cargo.toml", "brotli-decompressor", previous
    )
    new_decompressor = dependency_version("Cargo.toml", "brotli-decompressor")

    main_changed = old_brotli != new_brotli
    decompressor_changed = old_decompressor != new_decompressor
    if not main_changed and not decompressor_changed:
        print("No release-triggering Cargo dependency changed.")
        return 0

    current_version = cargo_value("Cargo.toml", "version")
    if main_changed:
        release_version = new_brotli
        project_version = release_version
        reason = f"Update to brotli {new_brotli} and decompressor {new_decompressor}"
        replace_cargo_package_version(release_version)
    else:
        project_version = next_post(current_version)
        reason = f"Update to brotli-decompressor {new_decompressor}"

    replace_project_version(project_version)
    subprocess.run(["cargo", "check"], cwd=ROOT, check=True)

    subprocess.run(
        ["git", "add", "Cargo.toml", "Cargo.lock", "pyproject.toml"],
        cwd=ROOT,
        check=True,
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False
    )
    if staged.returncode == 1:
        subprocess.run(
            ["git", "config", "user.name", "github-actions[bot]"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [
                "git",
                "config",
                "user.email",
                "41898282+github-actions[bot]@users.noreply.github.com",
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(["git", "commit", "-m", reason], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)
    elif staged.returncode == 0:
        print("Release version is already prepared; using the tested commit.")
    else:
        raise SystemExit("could not determine whether release files changed")

    tag = f"v{project_version}"
    head = git("rev-parse", "HEAD")
    existing_tag = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if existing_tag.returncode == 0:
        if existing_tag.stdout.strip() != head:
            raise SystemExit(f"{tag} already points at a different commit")
        print(f"{tag} already points at the tested commit; reusing it.")
    elif existing_tag.returncode == 128:
        subprocess.run(["git", "tag", tag], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", tag], cwd=ROOT, check=True)
    else:
        raise SystemExit(f"could not determine whether {tag} already exists")

    if main_changed:
        notes = release_notes("brotli", new_brotli, reason)
    else:
        notes = release_notes("brotli-decompressor", new_decompressor, reason)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as notes_file:
        notes_file.write(notes)
        notes_file.flush()
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                tag,
                "--notes-file",
                notes_file.name,
                "--title",
                tag,
            ],
            cwd=ROOT,
            check=True,
        )
    subprocess.run(
        [
            "gh",
            "workflow",
            "run",
            "release.yml",
            "--ref",
            "main",
            "-f",
            f"tag={tag}",
        ],
        cwd=ROOT,
        check=True,
    )
    print(f"Created {tag} ({reason}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
