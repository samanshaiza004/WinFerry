#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record Mach-O signature load commands and codesign metadata on macOS."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ARTIFACTS = ("loader/wine", "tools/wine/wine", "server/wineserver")
SIGNATURE_COMMAND_RE = re.compile(
    r"cmd LC_CODE_SIGNATURE\s+cmdsize (\d+)\s+dataoff (\d+)\s+datasize (\d+)", re.MULTILINE
)


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.returncode, result.stdout.strip()


def audit(path: Path, otool: str, codesign: str) -> dict[str, object]:
    load_rc, load_output = run([otool, "-l", str(path)])
    verify_rc, verify_output = run([codesign, "--verify", "--strict", "--verbose=2", str(path)])
    display_rc, display_output = run([codesign, "-dv", "--verbose=4", str(path)])
    signature = SIGNATURE_COMMAND_RE.search(load_output)
    fields = {
        key: re.search(rf"^{key}=(.*)$", display_output, re.MULTILINE)
        for key in ("Identifier", "Signature", "TeamIdentifier", "CDHash", "Page size")
    }
    cd_flags = re.search(r"CodeDirectory .*flags=([^\s]+)", display_output)
    return {
        "path": str(path),
        "otool_exit_code": load_rc,
        "lc_code_signature_present": signature is not None,
        "lc_code_signature": (
            {"cmdsize": int(signature[1]), "dataoff": int(signature[2]), "datasize": int(signature[3])}
            if signature
            else None
        ),
        "codesign_display_exit_code": display_rc,
        "identifier": fields["Identifier"][1] if fields["Identifier"] else None,
        "signature_kind": fields["Signature"][1] if fields["Signature"] else None,
        "team_identifier": fields["TeamIdentifier"][1] if fields["TeamIdentifier"] else None,
        "code_directory_flags": cd_flags[1] if cd_flags else None,
        "cdhash": fields["CDHash"][1] if fields["CDHash"] else None,
        "page_size": fields["Page size"][1] if fields["Page size"] else None,
        "codesign_verify_exit_code": verify_rc,
        "codesign_verify_output": verify_output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    otool, codesign = shutil.which("otool"), shutil.which("codesign")
    if not otool or not codesign:
        parser.error("otool and codesign are required (run on macOS)")

    builds = []
    for label, root in (("reference", args.reference), ("candidate", args.candidate)):
        builds.append(
            {
                "build": label,
                "root": str(root.resolve()),
                "artifacts": [audit(root / relative, otool, codesign) for relative in ARTIFACTS],
            }
        )
    artifacts = [item for build in builds for item in build["artifacts"]]
    result = {
        "method": "otool -l LC_CODE_SIGNATURE inspection; codesign -dv --verbose=4 metadata; codesign --verify --strict --verbose=2 validation",
        "all_have_lc_code_signature": all(item["lc_code_signature_present"] for item in artifacts),
        "all_signatures_are_adhoc": all(item["signature_kind"] == "adhoc" for item in artifacts),
        "all_signatures_verify": all(item["codesign_verify_exit_code"] == 0 for item in artifacts),
        "builds": builds,
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
