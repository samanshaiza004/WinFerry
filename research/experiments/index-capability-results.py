#!/usr/bin/env python3
"""Create a machine-readable manifest for the locally captured probe variants."""
import hashlib
import json
import re
import sys
from pathlib import Path


output = Path(sys.argv[1]).resolve()
variants = [
    ("plain-linker-signed", "ordinary", "linker-generated ad-hoc"),
    ("plain-codesign-adhoc", "ordinary", "explicit ad-hoc"),
    ("layout-linker-signed", "large PAGEZERO", "linker-generated ad-hoc"),
    ("layout-codesign-adhoc", "large PAGEZERO", "explicit ad-hoc"),
]


def read(name):
    path = output / name
    return path.read_text() if path.exists() else ""


records = []
for label, layout, signing in variants:
    signature = read(f"{label}.signature.txt")
    load_commands = read(f"{label}.load-commands.txt")
    pagezero = re.search(
        r"segname __PAGEZERO\s+vmaddr\s+(0x[0-9a-fA-F]+)\s+vmsize\s+(0x[0-9a-fA-F]+)",
        load_commands,
    )
    code_directory = re.search(r"CodeDirectory .*flags=([^ ]+).*", signature)
    page_size = re.search(r"^Page size=(\d+)$", signature, re.MULTILINE)
    team = re.search(r"^TeamIdentifier=(.*)$", signature, re.MULTILINE)
    verify_exit = re.search(r"verify_exit=(\d+)", read(f"{label}.verify.txt"))
    binary_path = output / f"capability-probe-{label.removesuffix('-linker-signed').removesuffix('-codesign-adhoc')}"
    if label == "plain-codesign-adhoc":
        binary_path = output / "capability-probe-plain-codesign-adhoc"
    elif label == "layout-codesign-adhoc":
        binary_path = output / "capability-probe-layout-codesign-adhoc"
    elif label == "plain-linker-signed":
        binary_path = output / "capability-probe-plain"
    elif label == "layout-linker-signed":
        binary_path = output / "capability-probe-layout"

    probe_lines = [line for line in read(f"{label}.result.jsonl").splitlines() if line.strip()]
    probe_records = [json.loads(line) for line in probe_lines]
    digest = hashlib.sha256(binary_path.read_bytes()).hexdigest() if binary_path.exists() else None
    records.append({
        "id": label,
        "layout": layout,
        "signing": signing,
        "binary": binary_path.name,
        "binary_sha256": digest,
        "macho_file": read(f"{label}.file.txt").strip(),
        "pagezero": {
            "vmaddr": pagezero.group(1),
            "vmsize": pagezero.group(2),
        } if pagezero else None,
        "signature_flags": code_directory.group(1) if code_directory else None,
        "signature_hash_page_size": int(page_size.group(1)) if page_size else None,
        "team_identifier": team.group(1) if team else None,
        "signature_verification_exit": int(verify_exit.group(1)) if verify_exit else None,
        "probe": probe_records[0] if probe_records else None,
        "additional_probe_results": probe_records[1:],
        "artifacts": {
            "signature": f"{label}.signature.txt",
            "verification": f"{label}.verify.txt",
            "load_commands": f"{label}.load-commands.txt",
            "unified_log": f"{label}.unified-log.json",
            "stderr": f"{label}.stderr.txt",
        },
    })

manifest = {
    "schema_version": 1,
    "date": "2026-10-10",
    "source_sha256": hashlib.sha256((Path(__file__).parent / "capability-probe.c").read_bytes()).hexdigest(),
    "minimum_macos_target": "26.6",
    "provisioning_profile": None,
    "restricted_entitlements": [],
    "followup_unified_log_query": "unified-log-followup.json",
    "variants": records,
    "interpretation": "Unprovisioned probe only; error 88 is not attributed to a specific cause.",
}
(output / "index.json").write_text(json.dumps(manifest, indent=2) + "\n")
