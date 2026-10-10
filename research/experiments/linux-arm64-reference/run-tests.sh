#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build=${1:-"$here/build"}
results=${2:-"$build/results"}
prefix=${WINEPREFIX:-"$build/wine-prefix"}
mkdir -p "$results"
expected="$results/expected.stdout"
printf 'WinFerry Windows console smoke\r\n' > "$expected"

set +e
WINEPREFIX="$prefix" WINEDEBUG=+loaddll wine "$build/hello-console-arm64.exe" \
    > "$results/arm64.stdout" 2> "$results/arm64.stderr"
arm64_status=$?
WINEPREFIX="$prefix" HODLL64=libarm64ecfex.dll WINEDEBUG=+loaddll \
    wine "$build/hello-console-x64.exe" \
    > "$results/x64.stdout" 2> "$results/x64.stderr"
x64_status=$?
set -e

printf '%s\n' "$arm64_status" > "$results/arm64.exit"
printf '%s\n' "$x64_status" > "$results/x64.exit"

arm64_pass=false
if [ "$arm64_status" -eq 37 ] && cmp -s "$expected" "$results/arm64.stdout"; then
    arm64_pass=true
fi

x64_fex_selected=false
if grep -Fq 'libarm64ecfex.dll' "$results/x64.stderr"; then
    x64_fex_selected=true
fi
x64_pass=false
if [ "$x64_status" -eq 37 ] && cmp -s "$expected" "$results/x64.stdout" && "$x64_fex_selected"; then
    x64_pass=true
fi

printf 'ARM64 native PE: %s (Wine exit %s)\n' "$arm64_pass" "$arm64_status"
printf 'x86-64 PE through FEX: %s (Wine exit %s; FEX selected %s)\n' \
    "$x64_pass" "$x64_status" "$x64_fex_selected"

if [ "$arm64_pass" != true ] || [ "$x64_pass" != true ]; then
    exit 1
fi
