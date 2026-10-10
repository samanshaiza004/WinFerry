#!/bin/sh
set -eu

if [ "$#" -ne 4 ]; then
    echo "usage: $0 WINE_SOURCE LLVM_MINGW_ROOT BISON_BIN_DIR BUILD_DIR" >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$1" && pwd -P)
toolchain=$(CDPATH= cd -- "$2" && pwd -P)
bison_bin=$(CDPATH= cd -- "$3" && pwd -P)
build_dir=$4
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd -P)
log_dir=${WINFERRY_NATIVE_BUILD_LOG_DIR:-"$repo_dir/research/experiments/native-wine-build/logs"}
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
if [ -x /opt/homebrew/bin/pkg-config ]; then
    PKG_CONFIG=/opt/homebrew/bin/pkg-config
    export PKG_CONFIG
fi
test "$(bison --version | sed -n '1s/.* //p')" = "3.8.2" || {
    echo "Bison 3.8.2 is required" >&2; exit 2;
}

mkdir -p "$build_dir" "$log_dir"
build_dir=$(CDPATH= cd -- "$build_dir" && pwd -P)
cd "$build_dir"
export CC=/usr/bin/clang CXX=/usr/bin/clang++
export CFLAGS='-O2 -g -arch arm64' CXXFLAGS='-O2 -g -arch arm64'
export LDFLAGS='-arch arm64'

if ! "$source_dir/configure" \
    --enable-archs=aarch64,arm64ec \
    --disable-tests \
    --without-x --without-cups --without-pulse --without-alsa \
    --without-gstreamer --without-vulkan \
    --prefix="$build_dir/install" > "$log_dir/configure.log" 2>&1; then
    tail -80 "$log_dir/configure.log" >&2
    exit 1
fi

if ! /usr/bin/make -j"$jobs" > "$log_dir/build.log" 2>&1; then
    tail -100 "$log_dir/build.log" >&2
    exit 1
fi

printf 'CONFIGURE=PASS\nBUILD=PASS\nRUNTIME=NOT_RUN\nBUILD_DIR=%s\n' "$build_dir"
