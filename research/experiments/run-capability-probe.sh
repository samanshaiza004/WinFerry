#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
output_dir=${CAPABILITY_PROBE_OUTPUT_DIR:-"$script_dir/results"}
mkdir -p "$output_dir"

build_probe() {
    name=$1
    shift
    xcrun clang -arch arm64 -Wall -Wextra -mmacosx-version-min=26.6 \
        "$script_dir/capability-probe.c" "$@" -o "$output_dir/$name"
}

build_probe capability-probe-plain
build_probe capability-probe-layout \
    -Wl,-x86_64_layout_emulation,-no_fixup_chains,-no_huge,\
-image_base,0x170000000,-pagezero_size,0x170000000

cp "$output_dir/capability-probe-plain" "$output_dir/capability-probe-plain-codesign-adhoc"
cp "$output_dir/capability-probe-layout" "$output_dir/capability-probe-layout-codesign-adhoc"
codesign --force --sign - --timestamp=none "$output_dir/capability-probe-plain-codesign-adhoc"
codesign --force --sign - --timestamp=none "$output_dir/capability-probe-layout-codesign-adhoc"

"$script_dir/capture-capability-variant.sh" plain-linker-signed \
    "$output_dir/capability-probe-plain"
"$script_dir/capture-capability-variant.sh" plain-codesign-adhoc \
    "$output_dir/capability-probe-plain-codesign-adhoc"
"$script_dir/capture-capability-variant.sh" layout-linker-signed \
    "$output_dir/capability-probe-layout"
"$script_dir/capture-capability-variant.sh" layout-codesign-adhoc \
    "$output_dir/capability-probe-layout-codesign-adhoc"

python3 "$script_dir/index-capability-results.py" "$output_dir"
