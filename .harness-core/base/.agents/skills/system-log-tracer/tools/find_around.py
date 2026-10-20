#!/usr/bin/env python3
"""find_around.py - Bounded time-window read-only search around an ISO timestamp."""
import argparse
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

p = argparse.ArgumentParser(description="Search a bounded time window around a timestamp")
p.add_argument("--timestamp", required=True)
p.add_argument("--minutes", type=float, default=5)
p.add_argument("--body-contains", action="append", default=[])
p.add_argument("--url", action="append", default=[])
p.add_argument("--source")
p.add_argument("--env")
p.add_argument("--root")
p.add_argument("--confirm-prod", action="store_true")
a = p.parse_args()

s = a.timestamp.replace("Z", "+00:00")
dt = datetime.fromisoformat(s)
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
lo = (dt - timedelta(minutes=a.minutes)).isoformat().replace("+00:00", "Z")
hi = (dt + timedelta(minutes=a.minutes)).isoformat().replace("+00:00", "Z")

cmd = [sys.executable, str(Path(__file__).with_name("search_logs.py")), "--from", lo, "--to", hi]
for x in a.body_contains:
    cmd += ["--body-contains", x]
for x in a.url:
    cmd += ["--url", x]
if a.source:
    cmd += ["--source", a.source]
if a.env:
    cmd += ["--env", a.env]
if a.root:
    cmd += ["--root", a.root]
if a.confirm_prod:
    cmd += ["--confirm-prod"]
raise SystemExit(subprocess.call(cmd))
