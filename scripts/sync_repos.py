#!/usr/bin/env python3
"""Clone and fast-forward the sibling repos in this workspace.

Usage: scripts/sync_repos.py [repo-name ...]
"""
import subprocess
import sys
from pathlib import Path

ORG = "resideo"
REPOS = [
    "ds-notification-service",
    "ds-event-definitions",
    "notification-definitions",
    "ds-message-template-api",
    "integration-services",
]
ROOT = Path(__file__).resolve().parent.parent


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=check
    )


def primary_branch(path):
    r = git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    if r.returncode != 0:
        git(path, "remote", "set-head", "origin", "-a", check=False)
        r = git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    if r.returncode == 0:
        return r.stdout.strip().removeprefix("origin/")
    for name in ("main", "master"):
        if git(path, "rev-parse", "--verify", f"origin/{name}", check=False).returncode == 0:
            return name
    raise RuntimeError("cannot determine primary branch")


def sync(name):
    path = ROOT / name
    if not path.exists():
        subprocess.run(
            ["git", "clone", f"git@github.com:{ORG}/{name}.git", str(path)], check=True
        )
        return "cloned"
    notes = []
    git(path, "fetch", "--prune")
    primary = primary_branch(path)
    current = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    dirty = bool(git(path, "status", "--porcelain").stdout.strip())
    if dirty:
        git(path, "stash", "push", "-u", "-m", "sync_repos auto-stash")
        notes.append(f"stashed changes from '{current}' (see `git stash list`)")
    if current != primary:
        git(path, "checkout", primary)
        notes.append(f"switched from '{current}' to '{primary}'")
    git(path, "merge", "--ff-only", f"origin/{primary}")
    head = git(path, "rev-parse", "--short", "HEAD").stdout.strip()
    return f"{primary} @ {head}" + "".join(f"; {n}" for n in notes)


def main():
    names = sys.argv[1:] or REPOS
    unknown = [n for n in names if n not in REPOS]
    if unknown:
        sys.exit(f"unknown repo(s): {', '.join(unknown)}; known: {', '.join(REPOS)}")
    failed = False
    for name in names:
        try:
            result = sync(name)
        except (subprocess.CalledProcessError, RuntimeError) as e:
            detail = getattr(e, "stderr", None) or str(e)
            result = f"FAILED: {detail.strip()}"
            failed = True
        print(f"{name}: {result}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
