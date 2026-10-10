#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 DOWNLOAD_DIR" >&2
    exit 2
fi

dir=$1
mkdir -p "$dir"
curl -fL --retry 2 -o "$dir/wine-a15ee2ccf20e2fc9f470badd916855801933d31f.tar.gz" \
    https://github.com/wine-mirror/wine/archive/a15ee2ccf20e2fc9f470badd916855801933d31f.tar.gz
curl -fL --retry 2 -o "$dir/llvm-mingw-20261006-ucrt-macos-universal.tar.xz" \
    https://github.com/mstorsjo/llvm-mingw/releases/download/20261006/llvm-mingw-20261006-ucrt-macos-universal.tar.xz
curl -fL --retry 2 -o "$dir/bison-3.8.2.tar.xz" \
    https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz

cd "$dir"
shasum -a 256 -c <<'CHECKSUMS'
f87b071f5f19f4cc5b6a51d3000ae03ee791325d5873ba221da191fd5b933a41  wine-a15ee2ccf20e2fc9f470badd916855801933d31f.tar.gz
a7a19b11048e89372637d26279cdb7c430ed3cf8c1e224310421312bf986ebf6  llvm-mingw-20261006-ucrt-macos-universal.tar.xz
9bba0214ccf7f1079c5d59210045227bcf619519840ebfa80cd3849cff5a5bf2  bison-3.8.2.tar.xz
CHECKSUMS
