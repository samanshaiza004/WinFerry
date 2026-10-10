#!/bin/sh
set -eu
cd "$(dirname "$0")"
xcrun clang -arch arm64 -Wall -Wextra -mmacosx-version-min=26.6 capability-probe.c -o capability-probe
file capability-probe
codesign -d --entitlements :- capability-probe 2>&1 || true
./capability-probe
