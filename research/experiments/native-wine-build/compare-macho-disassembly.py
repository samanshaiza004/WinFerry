#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare Mach-O instruction disassembly while accounting for literal offsets.

This macOS-only companion to compare-build-sections.py uses Apple's `otool`.
It normalizes only the encoded immediate on instructions annotated by otool as
addressing a literal-pool string, then compares the resolved target strings
after normalizing only each build's exact install-prefix path.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ARTIFACTS = ("loader/wine", "tools/wine/wine", "server/wineserver")
LITERAL_RE = re.compile(
    r"^(?P<address>\S+\s+)(?P<instruction>add\s+[^;]+?)\s+; literal pool for: (?P<target>.*)$"
)
IMMEDIATE_RE = re.compile(r"#0x[0-9a-fA-F]+")


def normalized_disassembly(path: Path, build_root: Path, otool: str) -> tuple[list[str], list[str]]:
    output = subprocess.check_output([otool, "-tvV", str(path)], text=True)
    lines: list[str] = []
    literal_targets: list[str] = []
    install_prefix = str((build_root / "install").resolve())
    for line in output.splitlines()[1:]:  # omit the file path header
        match = LITERAL_RE.match(line)
        if match:
            instruction = IMMEDIATE_RE.sub("#<literal-offset>", match["instruction"], count=1)
            lines.append(match["address"] + instruction)
            # otool resolves the immediate to its target string. Normalize only
            # an absolute string beginning with this build's exact /install path.
            literal_targets.append(normalize_literal_target(match["target"], install_prefix))
        else:
            lines.append(line)
    return lines, literal_targets


def normalize_literal_target(target: str, install_prefix: str) -> str:
    quoted_prefix = f'"{install_prefix}'
    if quoted_prefix not in target:
        return target
    if not target.startswith(quoted_prefix) or target.count(quoted_prefix) != 1:
        raise ValueError(f"unexpected install-prefix occurrence in literal target: {target}")
    boundary = target[len(quoted_prefix):len(quoted_prefix) + 1]
    if boundary not in ("/", '"'):
        return target
    return target.replace(quoted_prefix, '"<WINFERRY_INSTALL_PREFIX>', 1)


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
        left, left_targets = normalized_disassembly(args.reference / relative, args.reference, otool)
        right, right_targets = normalized_disassembly(args.candidate / relative, args.candidate, otool)
        differences = [
            {"line": index + 1, "reference": a, "candidate": b}
            for index, (a, b) in enumerate(zip(left, right))
            if a != b
        ]
        if len(left) != len(right):
            differences.append({"line": min(len(left), len(right)) + 1, "line_count": [len(left), len(right)]})
        target_mismatches = [
            {"reference": a, "candidate": b}
            for a, b in zip(left_targets, right_targets)
            if a != b
        ]
        if len(left_targets) != len(right_targets):
            target_mismatches.append({"target_count": [len(left_targets), len(right_targets)]})
        artifacts.append(
            {
                "path": relative,
                "normalized_disassembly_identical": not differences and not target_mismatches,
                "normalized_line_counts": [len(left), len(right)],
                "literal_pool_reference_lines": [len(left_targets), len(right_targets)],
                "literal_pool_targets_identical_after_install_prefix_normalization": not target_mismatches,
                "literal_pool_target_mismatches": target_mismatches[:25],
                "differences": differences[:25],
            }
        )

    result = {
        "method": "otool -tvV; normalize only immediates on instructions explicitly annotated 'literal pool for:'; normalize a target only when the resolved string begins with that build's exact quoted /install path at a path boundary; compare every resolved literal target and retain all other disassembly lines",
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
