#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
toolchain=${LLVM_MINGW:?Set LLVM_MINGW to an llvm-mingw toolchain directory}
out=${1:-"$here/build"}
mkdir -p "$out"

"$toolchain/bin/x86_64-w64-mingw32-clang" \
    -O2 -Wall -Wextra -Werror \
    -o "$out/hello-console-x64.exe" "$here/hello-console.c"
"$toolchain/bin/aarch64-w64-mingw32-clang" \
    -O2 -Wall -Wextra -Werror \
    -o "$out/hello-console-arm64.exe" "$here/hello-console.c"

"$toolchain/bin/llvm-readobj" --file-headers "$out/hello-console-x64.exe"
"$toolchain/bin/llvm-readobj" --file-headers "$out/hello-console-arm64.exe"
shasum -a 256 "$here/hello-console.c" "$out/hello-console-x64.exe" "$out/hello-console-arm64.exe"
