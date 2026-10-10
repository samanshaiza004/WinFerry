# WinFerry

WinFerry is investigating a free, open-source way to run Windows applications on Apple Silicon Macs without making Rosetta or a Windows installation part of the preferred execution path.

## Status

**Research, capability-probing, and build-only stage. No Windows application has been executed by WinFerry.** A pinned public upstream native Wine component build completed successfully, but it is not runtime evidence. The current feasibility decision is **CONDITIONAL GO**: native ARM64 Wine with Wine's ARM64EC support and FEX is a credible foundation, but the team has not reproduced an end-to-end Windows runtime or established Apple's development and distribution authorization for independent publishers.

A local M1 probe confirmed that macOS exposes the relevant cross-architecture APIs. Its attempt to launch a 4 KB child process returned `EBADMACHO` (error 88). That result does not identify the cause or establish whether a properly provisioned process will work. SIP remained enabled. See the [experiment record](research/experiments/README.md).

## What we are investigating

- Native ARM64 Wine and Apple's cross-architecture execution facilities
- FEX's Windows PE/ARM64EC path and the Darwin integration it needs
- Open graphics translation, especially DXMT, after CPU and windowing support
- Separate development authorization from distribution to ordinary Mac users
- A possible Linux virtual machine contingency if native Darwin authorization blocks distribution

WinFerry is not promising universal Windows compatibility. It has no consumer launcher or graphical interface yet.

## Research

Start with the [feasibility decision](research/07-feasibility.md), [architecture decision](research/08-architecture-decision.md), and [roadmap](research/09-roadmap.md). The [research index](research/README.md) links the comparative analysis, source evidence, licensing review, and experiment procedure.

The next gates are independent: first prove authorized native execution on a development machine; separately establish that an appropriately signed build can run on an unrelated stock Mac without recipient enrollment, machine registration, or weakened system security. The pinned native Wine component build completed in parallel and does not prove runtime execution.

## Contributing

At this stage, useful contributions include reproducible source/build evidence, carefully scoped experiments, and compatibility fixtures. Read the contribution policies for each upstream project before proposing code. In particular, FEX and DXMT restrict AI-generated code contributions; WinFerry research must not be misrepresented as human-authored upstream implementation.
