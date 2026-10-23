"""Fetch pinned upstream code and weights without putting them in this repository."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from contracts import DEFAULT_ASSETS, MODELS, REPOSITORIES


def prepare(root):
    root.mkdir(parents=True, exist_ok=True)
    for name, (repo, revision, directories) in REPOSITORIES.items():
        directory = root / name
        existing = (directory / ".git").is_dir()
        if not existing:
            if directory.exists() and any(directory.iterdir()):
                raise ValueError(f"Non-checkout directory already exists: {directory}")
            command = (
                ["gh", "repo", "clone", repo, str(directory), "--"]
                if shutil.which("gh")
                else ["git", "clone", f"https://github.com/{repo}", str(directory)]
            )
            subprocess.run(
                command + ["--filter=blob:none", "--no-checkout"], check=True
            )
        current = subprocess.run(
            ["git", "-C", str(directory), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        if existing and current:
            raise ValueError(f"Upstream checkout has local changes: {directory}")
        subprocess.run(
            ["git", "-C", str(directory), "sparse-checkout", "set", *directories],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(directory), "fetch", "--depth", "1", "origin", revision],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(directory), "checkout", "--detach", revision], check=True
        )
    hashes = {}
    for name, (relative, expected) in MODELS.items():
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Pinned model hash differs: {name}")
        hashes[name] = {"path": relative, "sha256": actual}
    (root / "asset-manifest.json").write_text(
        json.dumps(
            {
                "repositories": REPOSITORIES,
                "models": hashes,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Verified pinned kick assets: {root}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    prepare(parser.parse_args().assets.expanduser().resolve())
