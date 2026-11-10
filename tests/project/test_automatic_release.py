import runpy
import subprocess
import sys
from pathlib import Path


def test_decompressor_update_increments_existing_post_release(tmp_path, monkeypatch):
    scripts = Path(__file__).parents[2] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    monkeypatch.setenv("AUTOMATIC_RELEASE_ROOT", str(tmp_path))
    script = runpy.run_path(scripts / "automatic_release.py")

    def git(*args):
        return subprocess.check_output(
            ["git", *args], cwd=tmp_path, text=True
        ).strip()

    git("init", "--bare", "origin.git")
    git("init", "--initial-branch=main")
    git("config", "user.name", "Release test")
    git("config", "user.email", "release@example.com")
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text(
        '[package]\nname = "brotli-rs-python"\nversion = "9.1.1"\n'
        '\n[dependencies]\nbrotli = "=9.1.1"\n'
        'brotli-decompressor = "=6.3.0"\n'
    )
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nversion = "9.1.1.post1"\n')
    (tmp_path / "Cargo.lock").write_text("")
    git("add", "Cargo.toml", "Cargo.lock", "pyproject.toml")
    git("commit", "-m", "Release decompressor 6.3.0")
    previous = git("rev-parse", "HEAD")
    git("tag", "v9.1.1.post1")
    cargo.write_text(cargo.read_text().replace("6.3.0", "6.3.1"))
    git("add", "Cargo.toml")
    git("commit", "-m", "Update decompressor to 6.3.1")

    run = subprocess.run
    commands = []

    def run_command(args, **kwargs):
        if args[0] in ("cargo", "gh"):
            commands.append(args)
            return subprocess.CompletedProcess(args, 0)
        return run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run_command)
    monkeypatch.setitem(
        script["main"].__globals__, "release_notes", lambda *args: "Notes"
    )
    monkeypatch.setattr(sys, "argv", ["automatic_release.py", previous])

    assert script["main"]() == 0

    assert project.read_text() == '[project]\nversion = "9.1.1.post2"\n'
    assert 'version = "9.1.1"' in cargo.read_text()
    assert git("rev-parse", "v9.1.1.post1") == previous
    assert git("rev-parse", "v9.1.1.post2") == git("rev-parse", "HEAD")
    assert git("--git-dir=origin.git", "rev-parse", "refs/tags/v9.1.1.post2") == git(
        "rev-parse", "HEAD"
    )
    assert any(
        command[:4] == ["gh", "release", "create", "v9.1.1.post2"]
        for command in commands
    )
    assert commands[-1] == [
        "gh", "workflow", "run", "release.yml",
        "--ref", "main", "-f", "tag=v9.1.1.post2",
    ]
