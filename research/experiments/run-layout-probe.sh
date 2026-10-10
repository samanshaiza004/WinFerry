#!/bin/sh
set -eu
cd "$(dirname "$0")"
xcrun clang -arch arm64 -mmacosx-version-min=26.6 capability-probe.c \
  -Wl,-x86_64_layout_emulation,-no_fixup_chains,-no_huge,-image_base,0x170000000,-pagezero_size,0x170000000 \
  -o capability-probe-layout
file capability-probe-layout
./capability-probe-layout
