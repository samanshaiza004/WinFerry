# WinFerry

WinFerry is investigating a free, open-source way to run Windows applications on Apple Silicon Macs without making Rosetta or a Windows installation part of the preferred execution path.

## Status

**Research and experimental runtime stage. WinFerry's native macOS runtime has not executed a Windows application.** Two clean builds of pinned public native Wine sources completed successfully. A bounded Darwin loader patch and low-address layout also built as a native ARM64 Mach-O, but were not launched. The selected outputs have matching formats and code/ABI comparisons, with path and linker-generated debug identity differences documented; this is partial reproducibility, not macOS runtime evidence. A separate ARM64 Linux reference run passed a tiny ARM64 Windows console test and a tiny x86-64 test through Hangover/FEX in five later fresh-prefix trials. One earlier prefix hit the same FEX assertion twice; that anomaly remains unexplained. The full result is in [the Linux experiment](research/experiments/linux-arm64-reference/README.md). The feasibility decision remains **CONDITIONAL GO**: Linux results do not establish native macOS execution or Apple's development and distribution authorization.

A local M1 probe confirmed that macOS exposes the relevant cross-architecture APIs. Its attempt to launch a 4 KB child process returned `EBADMACHO` (error 88). That result does not identify the cause or establish whether a properly provisioned process will work. SIP remained enabled. See the [experiment record](research/experiments/README.md).

## What we are investigating

- Native ARM64 Wine and Apple's cross-architecture execution facilities
- FEX's Windows PE/ARM64EC path and the Darwin integration it needs
- Open graphics translation, especially DXMT, after CPU and windowing support
- Separate development authorization from distribution to ordinary Mac users
- An ARM64 Linux Hangover reference path that can be tested without Apple Developer Program membership

WinFerry is not promising universal Windows compatibility. It has no consumer launcher or graphical interface yet.

## Research

Start with the [feasibility decision](research/07-feasibility.md), [architecture decision](research/08-architecture-decision.md), and [roadmap](research/09-roadmap.md). The [research index](research/README.md) links the comparative analysis, source evidence, licensing review, and experiment procedure.

Work can continue without paid Apple Developer Program membership: Wine build work, the Linux reference path, portable Windows test fixtures, and build-only Darwin changes remain available. Developer ID signing and notarization are later distribution tasks, and membership does not guarantee Apple's separate restricted cross-architecture authorization. The next native-macOS gates remain independent: prove authorized execution on a development machine, then establish that a signed build can run on an unrelated stock Mac without recipient enrollment or weakened system security. The two pinned native Wine component builds passed in parallel, with their differences recorded in the [build comparison](research/experiments/native-wine-build/build-comparison.md). The separate [loader/layout build-only experiment](research/experiments/native-wine-build/darwin-loader-build.md) also passed its link checks. Neither proves native macOS runtime execution.

## Contributing

At this stage, useful contributions include reproducible source/build evidence, carefully scoped experiments, and compatibility fixtures. Read the contribution policies for each upstream project before proposing code. In particular, FEX and DXMT restrict AI-generated code contributions; WinFerry research must not be misrepresented as human-authored upstream implementation.

## License

WinFerry-authored code and research are MIT-licensed. The Wine-derived patches
retain LGPL-2.1-or-later terms. See [`THIRD_PARTY.md`](THIRD_PARTY.md) for the
license boundary and attribution details.
