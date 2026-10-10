#!/usr/bin/env python3
"""Compare pinned Wine build artifacts without treating debug data as code.

Raw SHA-256 values are always reported. Section hashes provide a second,
format-aware comparison that excludes Mach-O DWARF and PE .debug_* sections.
No artifact is modified by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


ARTIFACTS = (
    "loader/wine",
    "tools/wine/wine",
    "server/wineserver",
    "dlls/ntdll/aarch64-windows/ntdll.dll",
    "dlls/kernel32/aarch64-windows/kernel32.dll",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def c_string(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("ascii", "replace")


def macho_sections(data: bytes) -> tuple[str, dict[str, bytes]]:
    if len(data) < 32 or data[:4] != b"\xcf\xfa\xed\xfe":
        raise ValueError("not a little-endian 64-bit Mach-O file")
    _, cpu, _, _, ncmds, _, _, _ = struct.unpack_from("<IiiIIIII", data, 0)
    pos = 32
    sections: dict[str, bytes] = {}
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", data, pos)
        if cmd == 0x19:  # LC_SEGMENT_64
            segname = c_string(data[pos + 8 : pos + 24])
            nsects = struct.unpack_from("<I", data, pos + 64)[0]
            section_pos = pos + 72
            for _ in range(nsects):
                sectname = c_string(data[section_pos : section_pos + 16])
                section_segname = c_string(data[section_pos + 16 : section_pos + 32])
                size = struct.unpack_from("<Q", data, section_pos + 40)[0]
                offset = struct.unpack_from("<I", data, section_pos + 48)[0]
                flags = struct.unpack_from("<I", data, section_pos + 64)[0]
                key = f"{section_segname},{sectname}"
                section_type = flags & 0xFF
                if section_type in {1, 12, 18}:
                    sections[key] = bytes(size)
                else:
                    if offset + size > len(data):
                        raise ValueError(f"Mach-O section {key} extends past end of file")
                    sections[key] = data[offset : offset + size]
                section_pos += 80
            if section_pos > pos + cmdsize:
                raise ValueError("Mach-O segment section table exceeds load command")
        if cmdsize < 8:
            raise ValueError("invalid Mach-O load-command size")
        pos += cmdsize
    return f"Mach-O-64 cpu=0x{cpu:x}", sections


def pe_sections(data: bytes) -> tuple[str, dict[str, bytes]]:
    if len(data) < 64 or data[:2] != b"MZ":
        raise ValueError("not a PE image")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")
    coff = pe_offset + 4
    machine, nsects, _, symptr, nsyms, opt_size, _ = struct.unpack_from("<HHIIIHH", data, coff)
    string_table = b""
    if symptr and nsyms:
        string_pos = symptr + nsyms * 18
        if string_pos + 4 <= len(data):
            string_size = struct.unpack_from("<I", data, string_pos)[0]
            if string_size >= 4 and string_pos + string_size <= len(data):
                string_table = data[string_pos : string_pos + string_size]

    def section_name(raw: bytes) -> str:
        name = c_string(raw)
        if name.startswith("/") and name[1:].isdigit() and string_table:
            offset = int(name[1:])
            if 4 <= offset < len(string_table):
                return c_string(string_table[offset:])
        return name

    pos = coff + 20 + opt_size
    sections: dict[str, bytes] = {}
    for index in range(nsects):
        entry = pos + index * 40
        raw_name = data[entry : entry + 8]
        raw_size, raw_offset = struct.unpack_from("<II", data, entry + 16)
        name = section_name(raw_name)
        if raw_offset + raw_size > len(data):
            raise ValueError(f"PE section {name} extends past end of file")
        sections[name] = data[raw_offset : raw_offset + raw_size]
    return f"PE machine=0x{machine:04x}", sections


def parse_sections(data: bytes) -> tuple[str, dict[str, bytes]]:
    if data.startswith(b"\xcf\xfa\xed\xfe"):
        return macho_sections(data)
    if data.startswith(b"MZ"):
        return pe_sections(data)
    raise ValueError("unsupported artifact format")


def is_debug(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith("__dwarf,") or "__debug_" in lowered or lowered.startswith(".debug_")


def section_record(sections: dict[str, bytes], debug: bool = False) -> dict[str, dict[str, object]]:
    return {
        name: {"size": len(content), "sha256": sha256(content)}
        for name, content in sorted(sections.items())
        if is_debug(name) == debug
    }


def category_names(sections: dict[str, bytes], category: str) -> list[str]:
    if category == "code":
        return [
            name for name in sections
            if name.rsplit(",", 1)[-1].lower() in {"__text", "__stubs", "__stub_helper", ".text"}
        ]
    if category == "abi_metadata":
        return [
            name for name in sections
            if name.rsplit(",", 1)[-1].lower() in {".pdata", ".xdata", ".a64xrm", ".eh_fram", "__unwind_info"}
        ]
    return []


def compare_artifact(left_root: Path, right_root: Path, relative: str) -> dict[str, object]:
    left_path, right_path = left_root / relative, right_root / relative
    left_data, right_data = left_path.read_bytes(), right_path.read_bytes()
    left_format, left_sections = parse_sections(left_data)
    right_format, right_sections = parse_sections(right_data)
    left_record, right_record = section_record(left_sections), section_record(right_sections)
    left_debug, right_debug = section_record(left_sections, debug=True), section_record(right_sections, debug=True)
    common = sorted(set(left_record) | set(right_record))
    mismatched = [
        name for name in common
        if left_record.get(name) != right_record.get(name)
    ]
    code_sections = sorted(set(category_names(left_sections, "code")) | set(category_names(right_sections, "code")))
    abi_sections = sorted(
        set(category_names(left_sections, "abi_metadata"))
        | set(category_names(right_sections, "abi_metadata"))
    )
    return {
        "path": relative,
        "format": left_format,
        "candidate_format": right_format,
        "format_identical": left_format == right_format,
        "size_bytes": {"reference": len(left_data), "candidate": len(right_data)},
        "raw_sha256": {"reference": sha256(left_data), "candidate": sha256(right_data)},
        "raw_identical": left_data == right_data,
        "non_debug_sections_identical": not mismatched,
        "non_debug_section_mismatches": mismatched,
        "debug_sections_identical": left_debug == right_debug,
        "debug_section_mismatches": sorted(
            name for name in set(left_debug) | set(right_debug)
            if left_debug.get(name) != right_debug.get(name)
        ),
        "code_sections_identical": all(left_record.get(n) == right_record.get(n) for n in code_sections),
        "code_sections": code_sections,
        "abi_metadata_sections_identical": all(left_record.get(n) == right_record.get(n) for n in abi_sections),
        "abi_metadata_sections": abi_sections,
        "reference_non_debug_sections": left_record,
        "candidate_non_debug_sections": right_record,
        "reference_debug_sections": left_debug,
        "candidate_debug_sections": right_debug,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, help="first clean out-of-tree build")
    parser.add_argument("candidate", type=Path, help="second clean out-of-tree build")
    parser.add_argument("--output", type=Path, help="write JSON report to this path")
    args = parser.parse_args()
    results = [compare_artifact(args.reference, args.candidate, item) for item in ARTIFACTS]
    result = {
        "comparison_method": "raw file SHA-256 plus format-aware per-section SHA-256; Mach-O DWARF and PE .debug_* sections excluded from normalized section comparison; no bytes rewritten",
        "reference_build": str(args.reference.resolve()),
        "candidate_build": str(args.candidate.resolve()),
        "all_formats_identical": all(item["format_identical"] for item in results),
        "all_code_sections_identical": all(item["code_sections_identical"] for item in results),
        "all_abi_metadata_sections_identical": all(item["abi_metadata_sections_identical"] for item in results),
        "all_non_debug_sections_identical": all(item["non_debug_sections_identical"] for item in results),
        "artifacts": results,
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
