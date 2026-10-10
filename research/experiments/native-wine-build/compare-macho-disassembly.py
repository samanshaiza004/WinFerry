#!/usr/bin/env python3
"""Compare Mach-O instruction disassembly while accounting for literal offsets.

This macOS-only companion to compare-build-sections.py uses Apple's `otool`.
It normalizes only the encoded immediate on instructions annotated by otool as
addressing a literal-pool string. The strings themselves are compared by the
section-hash report, so this does not claim byte-for-byte identity.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ARTIFACTS = ("loader/wine", "tools/wine/wine", "server/wineserver")
LITERAL_RE = re.compile(r"^(?P<address>\S+\s+)(?P<instruction>add\s+[^;]+?)\s+; literal pool for:")
IMMEDIATE_RE = re.compile(r"#0x[0-9a-fA-F]+")


def normalized_disassembly(path: Path, otool: str) -> tuple[list[str], int]:
    output = subprocess.check_output([otool, "-tvV", str(path)], text=True)
    lines: list[str] = []
    literal_references = 0
    for line in output.splitlines()[1:]:  # omit the file path header
        match = LITERAL_RE.match(line)
        if match:
            instruction = IMMEDIATE_RE.sub("#<literal-offset>", match["instruction"], count=1)
            lines.append(match["address"] + instruction)
            literal_references += 1
        else:
            lines.append(line)
    return lines, literal_references


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    otool = shutil.which("otool")
    if not otool:
        parser.error("otool is required (run on macOS with Xcode command-line tools)")

    artifacts = []
    for relative in ARTIFACTS:
        left, left_literals = normalized_disassembly(args.reference / relative, otool)
        right, right_literals = normalized_disassembly(args.candidate / relative, otool)
        differences = [
            {"line": index + 1, "reference": a, "candidate": b}
            for index, (a, b) in enumerate(zip(left, right))
            if a != b
        ]
        if len(left) != len(right):
            differences.append({"line": min(len(left), len(right)) + 1, "line_count": [len(left), len(right)]})
        artifacts.append(
            {
                "path": relative,
                "normalized_disassembly_identical": not differences,
                "normalized_line_counts": [len(left), len(right)],
                "literal_pool_reference_lines": [left_literals, right_literals],
                "differences": differences[:25],
            }
        )

    result = {
        "method": "otool -tvV; normalize only immediates on instructions explicitly annotated 'literal pool for:'; retain all other disassembly lines; literal strings are separately compared by section hashes",
        "reference_build": str(args.reference.resolve()),
        "candidate_build": str(args.candidate.resolve()),
        "all_normalized_disassemblies_identical": all(item["normalized_disassembly_identical"] for item in artifacts),
        "artifacts": artifacts,
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
