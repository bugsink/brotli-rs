#!/usr/bin/env python3
"""Build release notes from the source commit of a published Rust crate."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import tarfile
import urllib.request


UPSTREAM_REPOSITORIES = {
    "brotli": "dropbox/rust-brotli",
    "brotli-decompressor": "dropbox/rust-brotli-decompressor",
}
SHA1 = re.compile(r"[0-9a-f]{40}")


def download_crate(crate: str, version: str) -> bytes:
    url = f"https://crates.io/api/v1/crates/{crate}/{version}/download"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "bugsink/brotli-rs release automation"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def source_commit_from_archive(archive_bytes: bytes, crate: str, version: str) -> str:
    metadata_path = f"{crate}-{version}/.cargo_vcs_info.json"
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        try:
            metadata = archive.extractfile(metadata_path)
        except KeyError:
            metadata = None
        if metadata is None:
            raise RuntimeError(f"{crate} {version} has no .cargo_vcs_info.json")
        vcs_info = json.load(metadata)

    commit = vcs_info.get("git", {}).get("sha1", "")
    if SHA1.fullmatch(commit) is None:
        raise RuntimeError(f"{crate} {version} has no valid source commit")
    return commit


def source_commit(crate: str, version: str) -> str:
    return source_commit_from_archive(download_crate(crate, version), crate, version)


def commit_message(repository: str, commit: str) -> str:
    url = f"https://api.github.com/repos/{repository}/commits/{commit}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "bugsink/brotli-rs release automation",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    message = data.get("commit", {}).get("message", "").strip()
    if not message:
        raise RuntimeError(f"upstream commit {repository}@{commit} has no message")
    return message


def format_release_notes(
    crate: str,
    version: str,
    repository: str,
    commit: str,
    message: str,
    project_notes: str | None = None,
) -> str:
    source_url = f"https://github.com/{repository}/commit/{commit}"
    notes = (
        f"## Upstream {crate} {version} release notes\n\n"
        f"{message.strip()}\n\n"
        f"[Upstream source commit {commit[:12]}]({source_url})"
    )
    if project_notes:
        notes += f"\n\n## brotli-rs notes\n\n{project_notes.strip()}"
    return notes + "\n"


def release_notes(crate: str, version: str, project_notes: str | None = None) -> str:
    try:
        repository = UPSTREAM_REPOSITORIES[crate]
    except KeyError as error:
        raise RuntimeError(f"no upstream repository configured for {crate}") from error
    commit = source_commit(crate, version)
    message = commit_message(repository, commit)
    return format_release_notes(
        crate,
        version,
        repository,
        commit,
        message,
        project_notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("crate", choices=sorted(UPSTREAM_REPOSITORIES))
    parser.add_argument("version")
    parser.add_argument("--project-notes")
    args = parser.parse_args()
    print(release_notes(args.crate, args.version, args.project_notes), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
