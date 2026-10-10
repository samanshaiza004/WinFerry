#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect the loader Mach-O layout and local signature without launching it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


EXPECTED_LAYOUT = 0x170000000


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def segments(load_commands: str) -> dict[str, dict[str, int]]:
    found: dict[str, dict[str, int]] = {}
    blocks = re.split(r"(?m)^Load command \d+\s*$", load_commands)
    for block in blocks:
        if not re.search(r"(?m)^\s*cmd LC_SEGMENT_64\s*$", block):
            continue
        name = re.search(r"(?m)^\s*segname (\S+)\s*$", block)
        vmaddr = re.search(r"(?m)^\s*vmaddr (0x[0-9a-fA-F]+)\s*$", block)
        vmsize = re.search(r"(?m)^\s*vmsize (0x[0-9a-fA-F]+)\s*$", block)
        if not name or not vmaddr or not vmsize:
            raise ValueError("incomplete LC_SEGMENT_64 record in otool output")
        if name[1] in found:
            raise ValueError(f"duplicate {name[1]} segment")
        found[name[1]] = {"vmaddr": int(vmaddr[1], 16), "vmsize": int(vmsize[1], 16)}
    return found


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} MACH_O_LOADER")
    binary = Path(sys.argv[1]).resolve()
    file_result = run("file", str(binary))
    if file_result.returncode:
        raise SystemExit(file_result.stderr.strip())
    if "Mach-O 64-bit executable arm64" not in file_result.stdout:
        raise SystemExit(f"not a native ARM64 Mach-O executable: {file_result.stdout.strip()}")

    load_result = run("otool", "-l", str(binary))
    if load_result.returncode:
        raise SystemExit(load_result.stderr.strip())
    layout = segments(load_result.stdout)
    pagezero = layout.get("__PAGEZERO")
    text = layout.get("__TEXT")
    if not pagezero or pagezero["vmaddr"] != 0 or pagezero["vmsize"] != EXPECTED_LAYOUT:
        raise SystemExit(f"unexpected __PAGEZERO layout: {pagezero}")
    if not text or text["vmaddr"] != EXPECTED_LAYOUT:
        raise SystemExit(f"unexpected __TEXT base: {text}")
    has_signature = bool(re.search(r"(?m)^\s*cmd LC_CODE_SIGNATURE\s*$", load_result.stdout))
    if not has_signature:
        raise SystemExit("missing LC_CODE_SIGNATURE")

    verify = run("codesign", "--verify", "--strict", str(binary))
    if verify.returncode:
        raise SystemExit(f"codesign verification failed: {verify.stderr.strip()}")
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    print(json.dumps({
        "path": str(binary),
        "format": file_result.stdout.strip(),
        "sha256": digest,
        "segments": layout,
        "lc_code_signature_present": has_signature,
        "codesign_verify_exit_code": verify.returncode,
        "runtime_executed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
