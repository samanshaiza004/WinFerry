#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 BISON_ARCHIVE PREFIX" >&2
    exit 2
fi

archive=$(CDPATH= cd -- "$(dirname -- "$1")" && pwd -P)/$(basename -- "$1")
prefix=$2
expected=9bba0214ccf7f1079c5d59210045227bcf619519840ebfa80cd3849cff5a5bf2
actual=$(shasum -a 256 "$archive" | awk '{print $1}')
test "$actual" = "$expected" || {
    echo "Bison archive SHA-256 mismatch" >&2; exit 1;
}

base=${TMPDIR:-/private/tmp}/winferry-bison-3.8.2
source_dir=$base/source/bison-3.8.2
build_dir=$base/build
mkdir -p "$base/source" "$build_dir"
tar -xJf "$archive" -C "$base/source"
cd "$source_dir"
./configure --prefix="$prefix" > "$base/configure.log" 2>&1
make -j"${JOBS:-2}" > "$base/build.log" 2>&1
make install > "$base/install.log" 2>&1
"$prefix/bin/bison" --version | head -1
