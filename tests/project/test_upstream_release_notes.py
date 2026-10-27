import io
import json
import tarfile

import pytest

from scripts.upstream_release_notes import format_release_notes
from scripts.upstream_release_notes import source_commit_from_archive


def crate_archive(crate, version, vcs_info):
    contents = json.dumps(vcs_info).encode()
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        member = tarfile.TarInfo(f"{crate}-{version}/.cargo_vcs_info.json")
        member.size = len(contents)
        archive.addfile(member, io.BytesIO(contents))
    return output.getvalue()


def test_source_commit_comes_from_published_crate_metadata():
    commit = "0123456789abcdef0123456789abcdef01234567"
    archive = crate_archive("brotli", "9.1.0", {"git": {"sha1": commit}})

    assert source_commit_from_archive(archive, "brotli", "9.1.0") == commit


def test_source_commit_requires_cargo_vcs_metadata():
    archive = crate_archive("brotli", "9.1.0", {})

    with pytest.raises(RuntimeError, match="no valid source commit"):
        source_commit_from_archive(archive, "brotli", "9.1.0")


def test_release_notes_preserve_upstream_message_and_add_attribution():
    commit = "0123456789abcdef0123456789abcdef01234567"

    notes = format_release_notes(
        "brotli",
        "9.1.0",
        "dropbox/rust-brotli",
        commit,
        "Fix the encoder\n\n* Keep this upstream detail",
        "Update to brotli 9.1.0",
    )

    assert notes == (
        "## Upstream brotli 9.1.0 release notes\n\n"
        "Fix the encoder\n\n"
        "* Keep this upstream detail\n\n"
        "[Upstream source commit 0123456789ab]"
        "(https://github.com/dropbox/rust-brotli/commit/"
        "0123456789abcdef0123456789abcdef01234567)\n\n"
        "## brotli-rs notes\n\n"
        "Update to brotli 9.1.0\n"
    )
