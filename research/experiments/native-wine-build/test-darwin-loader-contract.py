#!/usr/bin/env python3
"""Static contract checks for the experimental Darwin loader patch and recipe."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "patches/darwin-build-only/0001-loader-request-4k-process-pages.patch"
BUILD = ROOT / "build-darwin-loader-only.sh"
VERIFY = ROOT / "verify-darwin-loader-artifact.py"
DISASSEMBLY = ROOT / "compare-macho-disassembly.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    patch = PATCH.read_text()
    build = BUILD.read_text()
    verify = VERIFY.read_text()
    spec = importlib.util.spec_from_file_location("macho_disassembly", DISASSEMBLY)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load the Mach-O comparison helper")
    disassembly = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(disassembly)
    body = patch.split("static void ensure_4k_pages", 1)[1].split("#endif", 1)[0]
    require("defined(__APPLE__) && defined(__aarch64__)" in patch, "patch must be Apple ARM64-only")
    require("if (getpagesize() == 4096) return;" in body, "already-correct page size must bypass re-exec")
    require("__builtin_available(macOS 26.0, *)" in body, "4 KB spawn API must be OS-version guarded")
    require("posix_spawnattr_set_4k_page_size_np( &attr )" in body, "must request the 4 KB process attribute")
    require("POSIX_SPAWN_SETEXEC" in body, "re-exec must replace the loader process")
    require("WINFERRY_PAGE_SIZE_REEXEC_PID" in body and "getpid()" in body, "re-exec must be bounded by a PID guard")
    require("self = get_self_exe();" in body, "re-exec must resolve the running executable")
    require("posix_spawn( NULL, self, NULL, &attr, argv, environ )" in body, "must preserve argv and inherited environment")
    require(patch.index("ensure_4k_pages( argv )") < patch.index("init_reserved_areas()"), "page switch must precede Wine address reservations")
    require(patch.index("ensure_4k_pages( argv )") < patch.index("if ((handle = try_dlopen"), "page switch must precede Wine runtime loading")
    require("x86_64_layout_emulation" in build and "pagezero_size,0x170000000" in build, "build recipe must set the experimental loader layout")
    require("line.startswith(\"  \" + upstream)" in build and "len(rules) != 1" in build, "build recipe must narrowly patch one generated loader link rule")
    require("--without-freetype" in build, "loader-only configure must avoid unrelated font-library discovery")
    require("loader/wine" in build and "RUNTIME=NOT_RUN" in build, "recipe must build and inspect only the loader")
    require("verify-darwin-loader-artifact.py" in build and "EXPECTED_LAYOUT = 0x170000000" in verify, "artifact validation must inspect exact segment records without launch")
    require("cp -R \"$source_dir\" \"$source_copy\"" in build, "recipe must preserve the pinned source tree")
    require("signal_arm64" not in patch and "x18" not in patch.lower(), "this patch tranche must remain independent of x18 and signal work")
    normalize = disassembly.normalize_literal_target
    require(normalize('"/tmp/build/install/lib"', "/tmp/build/install") == '"<WINFERRY_INSTALL_PREFIX>/lib"', "expected install-root literals may normalize")
    require(normalize('"/tmp/build/installable/lib"', "/tmp/build/install") == '"/tmp/build/installable/lib"', "similar path prefixes must not normalize")
    require(normalize('"text /tmp/build/install/lib"', "/tmp/build/install") == '"text /tmp/build/install/lib"', "interior path text must not normalize")
    print("PASS: loader re-exec and build-only scope contract")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
