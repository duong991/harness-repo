#!/usr/bin/env python3
"""Compare a worktree's changes since BASE with an allowlist.

Usage: check-scope.py --worktree DIR --base REV ALLOWED...

ALLOWED entries are exact repo-relative file paths, or directories ending in
"/". Changes = tracked differences between BASE and the working tree (which
includes anything the worker committed) plus untracked, non-ignored files.

Prints one JSON object and exits 0 when everything is in scope, 2 when any path
is out of scope, 1 on error.
"""
import argparse
import json
import subprocess
import sys


def git(wt, *args):
    out = subprocess.run(["git", "-C", wt, *args], capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def in_scope(path, allowed):
    for a in allowed:
        if a.endswith("/") and path.startswith(a):
            return True
        if path == a:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("allowed", nargs="+")
    args = ap.parse_args()
    allowed = [a[2:] if a.startswith("./") else a for a in args.allowed]

    try:
        tracked = git(args.worktree, "diff", "--name-only", "-z", "--no-renames", args.base)
        untracked = git(args.worktree, "ls-files", "--others", "--exclude-standard", "-z")
        head = git(args.worktree, "rev-parse", "HEAD")[0].strip()
        base = git(args.worktree, "rev-parse", args.base)[0].strip()
    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": e.stderr.decode(errors="replace").strip()}))
        return 1

    changed = sorted(set(tracked) | set(untracked))
    out_of_scope = [p for p in changed if not in_scope(p, allowed)]
    result = {
        "in_scope": not out_of_scope,
        "changed": changed,
        "out_of_scope": out_of_scope,
        "untracked": sorted(untracked),
        "worker_committed": head != base,
    }
    print(json.dumps(result, indent=2))
    return 0 if not out_of_scope else 2


if __name__ == "__main__":
    sys.exit(main())
