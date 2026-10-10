#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""CI gate: require a real 4 KB child, not merely successful harness completion."""
import json
import sys
from pathlib import Path


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} RESULT.jsonl")

path = Path(sys.argv[1])
try:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
except (OSError, json.JSONDecodeError) as error:
    fail(f"cannot read valid result JSONL: {error}")

parent = next((record for record in records if record.get("mode") == "parent"), None)
child = next((record for record in records if record.get("mode") == "4k_child"), None)
if parent is None:
    fail("parent probe result is missing")
if parent.get("spawnattr_4k_rc") != 0:
    fail(f"4 KB spawn attribute setup returned {parent.get('spawnattr_4k_rc')!r}")
if parent.get("spawn_4k_rc") != 0:
    fail(f"4 KB child spawn returned {parent.get('spawn_4k_rc')!r}")
if parent.get("child_exit") != 0:
    fail(f"4 KB child exit was {parent.get('child_exit')!r}, expected 0")
if parent.get("child_signal") not in (-1, None):
    fail(f"4 KB child terminated by signal {parent.get('child_signal')!r}")
if child is None:
    fail("4 KB child did not report its result")
if child.get("page_size") != 4096:
    fail(f"child page size was {child.get('page_size')!r}, expected 4096")
if child.get("compiled_arch") != "arm64":
    fail(f"child architecture was {child.get('compiled_arch')!r}, expected arm64")

print(json.dumps({
    "status": "PASS",
    "spawn_4k_rc": parent["spawn_4k_rc"],
    "child_exit": parent["child_exit"],
    "child_page_size": child["page_size"],
    "child_compiled_arch": child["compiled_arch"],
}, sort_keys=True))
