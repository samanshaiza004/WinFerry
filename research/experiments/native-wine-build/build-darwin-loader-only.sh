#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

if [ "$#" -ne 4 ]; then
    echo "usage: $0 PINNED_WINE_SOURCE LLVM_MINGW_ROOT BISON_BIN_DIR OUTPUT_DIR" >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$1" && pwd -P)
toolchain=$(CDPATH= cd -- "$2" && pwd -P)
bison_bin=$(CDPATH= cd -- "$3" && pwd -P)
output_dir=$4
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd -P)
patch_dir=$repo_dir/research/experiments/native-wine-build/patches/darwin-build-only
loader_patch=$patch_dir/0001-loader-request-4k-process-pages.patch
layout_patch=$patch_dir/0002-darwin-arm64-low-address-layout.patch
jobs=${JOBS:-2}

case "$(basename -- "$source_dir")" in
    wine-a15ee2ccf20e2fc9f470badd916855801933d31f) ;;
    *) echo "source directory must be the pinned Wine archive root" >&2; exit 2 ;;
esac
test -x "$toolchain/bin/aarch64-w64-mingw32-clang" || {
    echo "missing llvm-mingw ARM64 compiler" >&2; exit 2;
}
test -x "$toolchain/bin/arm64ec-w64-mingw32-clang" || {
    echo "missing llvm-mingw ARM64EC compiler" >&2; exit 2;
}
PATH="$toolchain/bin:$bison_bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH
test "$(bison --version | sed -n '1s/.* //p')" = "3.8.2" || {
    echo "Bison 3.8.2 is required" >&2; exit 2;
}
test "$(uname -s)" = Darwin || {
    echo "this build-only experiment requires macOS and Xcode command-line tools" >&2; exit 2;
}
command -v otool >/dev/null && command -v file >/dev/null || {
    echo "otool and file are required for artifact inspection" >&2; exit 2;
}

mkdir -p "$output_dir"
output_dir=$(CDPATH= cd -- "$output_dir" && pwd -P)
source_copy=$output_dir/source
build_dir=$output_dir/build
logs=$output_dir/logs
test ! -e "$source_copy" && test ! -e "$build_dir" || {
    echo "output directory already contains source or build; choose a fresh output directory" >&2; exit 2;
}
mkdir -p "$logs"
{
    sw_vers
    xcodebuild -version
    xcrun --sdk macosx --show-sdk-version
    /usr/bin/clang --version
    bison --version | sed -n '1p'
    /opt/homebrew/bin/pkg-config --version 2>/dev/null || true
    "$toolchain/bin/aarch64-w64-mingw32-clang" --version | sed -n '1p'
} > "$logs/host-environment.txt" 2>&1
cp -R "$source_dir" "$source_copy"
if ! (
    cd "$source_copy"
    patch -p1 < "$loader_patch"
    patch -p1 < "$layout_patch"
) > "$logs/patch.log" 2>&1; then
    cat "$logs/patch.log" >&2
    exit 1
fi

if [ -x /opt/homebrew/bin/pkg-config ]; then
    PKG_CONFIG=/opt/homebrew/bin/pkg-config
    export PKG_CONFIG
fi
mkdir -p "$build_dir"
build_dir=$(CDPATH= cd -- "$build_dir" && pwd -P)
cd "$build_dir"
export CC=/usr/bin/clang CXX=/usr/bin/clang++
export CFLAGS='-O2 -g -arch arm64' CXXFLAGS='-O2 -g -arch arm64'
export LDFLAGS='-arch arm64'

if ! "$source_copy/configure" \
    --enable-archs=aarch64,arm64ec \
    --disable-tests \
    --without-freetype \
    --without-x --without-cups --without-pulse --without-alsa \
    --without-gstreamer --without-vulkan \
    --prefix="$build_dir/install" > "$logs/configure.log" 2>&1; then
    tail -80 "$logs/configure.log" >&2
    exit 1
fi

wine_loader_ldflags='-Wl,-x86_64_layout_emulation,-no_fixup_chains,-no_huge,-image_base,0x170000000,-pagezero_size,0x170000000,-segalign,0x1000,-sectcreate,__TEXT,__info_plist,loader/wine_info.plist'
python3 - "$build_dir/Makefile" "$wine_loader_ldflags" > "$logs/linker-flags.txt" <<'PY'
from pathlib import Path
import sys

makefile = Path(sys.argv[1])
flags = sys.argv[2]
matches = [line.partition(" = ")[2] for line in makefile.read_text().splitlines()
           if line.startswith("WINELOADER_LDFLAGS = ")]
if len(matches) != 1:
    raise SystemExit(f"expected one configured WINELOADER_LDFLAGS assignment, found {len(matches)}")
if matches[0] != flags:
    raise SystemExit(f"configured loader flags differ from expectation: {matches[0]}")
print(flags)
PY
if ! /usr/bin/make -j"$jobs" loader/wine > "$logs/build-loader.log" 2>&1; then
    tail -100 "$logs/build-loader.log" >&2
    exit 1
fi

file "$build_dir/loader/wine" > "$logs/file.txt"
otool -l "$build_dir/loader/wine" > "$logs/load-commands.txt"
codesign -dv --verbose=4 "$build_dir/loader/wine" > "$logs/codesign-display.txt" 2>&1 || true
if ! python3 "$repo_dir/research/experiments/native-wine-build/verify-darwin-loader-artifact.py" \
    "$build_dir/loader/wine" > "$logs/artifact-verification.json" 2> "$logs/artifact-verification.err"; then
    cat "$logs/artifact-verification.err" >&2
    exit 1
fi

printf 'PATCH=PASS\nCONFIGURE=PASS\nLOADER_LINK=PASS\nARTIFACT_ARCH=arm64\nRUNTIME=NOT_RUN\nOUTPUT_DIR=%s\n' "$output_dir"
