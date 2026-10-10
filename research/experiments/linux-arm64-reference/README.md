# ARM64 Linux Hangover reference experiment

This experiment validates pieces shared with the proposed macOS runtime while Apple authorization is unresolved. It is a Linux reference run, not a WinFerry macOS runtime or product backend. It does not test Darwin Wine, macOS entitlements, GUI integration, graphics, or distribution.

## Result (2026-10-10)

| Test | Result |
|---|---|
| ARM64 Windows console PE through Hangover Wine | **PASS** — printed `WinFerry Windows console smoke` and returned exit code 37. |
| x86-64 Windows console PE through ARM64EC/FEX | **PASS, narrow** — five subsequent runs across five fresh Wine prefixes selected `libarm64ecfex.dll`, printed the expected line, and returned exit code 37. One earlier Wine prefix produced two FEX forced-assert failures; that failure did not reproduce in the five clean-prefix runs. |

The ARM64 pass verifies the Linux guest, Wine ARM64 path, and a small Win32 console API use. The five x86-64 passes verify that this tiny PE can execute through Hangover's ARM64EC/FEX path. They do not establish general x64 compatibility or stability. In the earlier prefix, the original x64 test and a later rebuild both raised `0xc000001d` at `FEXCore::Assert::ForcedAssertEv` before printing output; the cause is unknown. The FEX config directory was empty after the tests, and a later x64-first run with isolated `HOME`, XDG, and FEX app-data/config/cache paths also passed. Preserve the assertion logs as a real unresolved edge case. A Hangover user reported the same exception class with release 10.14 in [issue #211](https://github.com/AndreRH/hangover/issues/211); that report is corroborating context, not proof of a shared root cause.

## Host and guest

- Host: Apple Silicon MacBook Air, macOS 27.0 build 26A428, Darwin arm64. The host model-name `sysctl` query was blocked by the execution sandbox; the Darwin kernel identifies `T8103` and the host is an M1 MacBook Air in the task environment.
- Linux VM: Colima 0.7.6, Virtualization.framework (`vz`) backend, 2 vCPUs, 3 GiB configured memory, 24 GiB configured disk. The existing default Colima profile and Docker Desktop were not changed.
- Guest/container: Ubuntu 24.04.5 LTS ARM64, Linux `6.8.0-47-generic`, `uname -m=aarch64`, `getconf PAGESIZE=4096`, 2 visible CPUs, about 2.8 GiB total memory and 23 GiB container overlay at test time.
- The Windows applications ran in an ARM64 Linux container in an ARM64 VM. No x86 Linux guest or Rosetta-on-Linux path was selected. This establishes the architecture of this test path; it says nothing about Rosetta participation in unrelated host applications.
- The test ran in a disposable container as root. Only the source-built, tiny test programs were executed. This container configuration is for a controlled reference experiment and is not an isolation claim for arbitrary Windows programs.

## Pinned runtime inputs

- Hangover release: `hangover-11.16`, released 2026-08-30.
- Asset: `hangover_11.16_ubuntu2404_noble_arm64.tar`, SHA-256 `94611dad2b23978d35825a018c81b3947caaec174aa04c052849d37bc6a39e72`.
- Installed packages: `hangover-wine 11.16~noble`, `hangover-libarm64ecfex 11.16`, `hangover-wowbox64 11.16`; `wine --version` reported `wine-11.16 (Hangover)`.
- Package SHA-256:
  - Wine: `f425b2063b069947efcc553215de650fc0217cff19f52274f36f225c048ca5b8`
  - FEX ARM64EC PE module: `a4a197b04f63fd340bfdfe53049be6abd196e23b4c1c528cc80536b363e19ad0`
  - wowbox64: `ceeb3ec77eee073a2c867725d1153bc8c697bcacefb896149c9a7a45c798635a`
- Installed `/usr/lib/wine/aarch64-windows/libarm64ecfex.dll` SHA-256: `45522fdea5edaf58066d0f265c0b42a4eac361393718625caf4a3639bf9246bf`.
- Primary package source: [Hangover 11.16 release](https://github.com/AndreRH/hangover/releases/tag/hangover-11.16). Hangover documents `HODLL64=libarm64ecfex.dll` as the x86-64 ARM64EC/FEX module selector and `wine program.exe` as the run path in its [README](https://github.com/AndreRH/hangover/blob/56e385b7ff490edd281b288f420677093563560b/README.md).

## Test program and build

`hello-console.c` is WinFerry-authored MIT-licensed source. It calls `GetStdHandle(STD_OUTPUT_HANDLE)` and `WriteFile`, verifies the complete line was written, then returns 37. The source is shared by both PE builds so the test behavior is identical.

- Toolchain: `llvm-mingw-20261006-ucrt-macos-universal`; Clang 23.1.3, LLVM project revision `0d261d1ca552c95a8f007e061c787ac7132fbcbc`.
- The toolchain's Clang executable is a universal Mach-O with x86-64 and ARM64 slices; the host is ARM64. The Windows PE binaries were executed in the ARM64 Linux guest, not by a macOS x86-64 process.
- Command: `LLVM_MINGW=/path/to/llvm-mingw-20261006-ucrt-macos-universal ./build-tests.sh`.
- x86-64 PE machine: `IMAGE_FILE_MACHINE_AMD64 (0x8664)`, SHA-256 `3c240da41dad0ddbb009cbf54c0d9750ebee0af60dfd8e9ee5534c89f0a729d1`.
- ARM64 PE machine: `IMAGE_FILE_MACHINE_ARM64 (0xAA64)`, SHA-256 `0962d15a2aef00f4cf1f7fedcc870a8257fc5a425cac7bf3311c7eb3e0c80810`.
- Source SHA-256: `f23f6dcf0f22d9a23d51cfe5e3a3fb025e0ff7cf1182be450a8329da40070621`.

The exact source, command results, package identities, guest details, stdout, exit status, PE headers, disassembly and complete Wine logs are in `results/`; [manifest.json](results/manifest.json) provides the machine-readable summary, [environment.txt](results/environment.txt) records the host/guest report, and [run-provenance.txt](results/run-provenance.txt) lists the prefix and environment for each pass and failure. Two paired fresh-prefix runs are in [`paired-pass/`](results/paired-pass/) and [`paired-pass-2/`](results/paired-pass-2/); three independent x64-first success logs and both prior failure captures are retained in neighboring directories. Run records are not pass/fail CI gates by harness exit status alone; the Windows program's expected output and return code, PE machine, and FEX selection trace all matter.

## Earlier x86-64 assertion and later passes

The first prefix's saved Wine trace loaded the PE as `native`, then loaded the built-in `libarm64ecfex.dll` at `0x6ffffa920000`. The unhandled-exception PC was `0x6ffffaa85bb8`, RVA `0x165bb8` from that DLL base. Disassembly of the matching ARM64EC PE identifies `FEXCore::Assert::ForcedAssertEv`; the instruction at image virtual address `0x180165bb8` is `hlt #0x1`. This is a deliberate FEX assertion, not evidence of an unsupported host CPU instruction. The assertion happened twice in the same Wine prefix, then was not observed in five later runs using five new Wine prefixes. The causal state change is UNKNOWN.

The five passing trials used the published 11.16 Ubuntu 24.04 ARM64 packages and the same tested AMD64 PE. Two paired runs initialized a fresh prefix with the ARM64 control first; two additional fresh prefixes ran x64 first; one fresh x64-first run also used separate `HOME`, XDG, and FEX app-data/config/cache directories. The [run script](run-tests.sh) captures the PE output, Wine exit codes, and FEX module-selection trace. This is a narrow runtime proof, not a Hangover conformance suite, and it does not establish that the Linux result transfers to Darwin.

## Reproduction

1. Use an ARM64 Ubuntu 24.04 guest with a 4 KB page size; record guest CPU features and resource limits.
2. Install the Hangover 11.16 Ubuntu 24.04 ARM64 release package set and verify the package hashes above.
3. Build both binaries from `hello-console.c` with the pinned llvm-mingw toolchain and verify their PE machine types and hashes.
4. Run `WINEPREFIX=/path/to/new/prefix ./run-tests.sh /path/to/build /path/to/results`. The script runs ARM64 first, records each invocation separately, and exits nonzero if either PE misses its expected output, exit code, or FEX-selection criteria.
5. To test the x64-first path independently, set a new `WINEPREFIX` and run `HODLL64=libarm64ecfex.dll WINEDEBUG=+loaddll wine hello-console-x64.exe` with stdout and stderr redirected to separate files. For an isolated FEX config test, also use new `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `FEX_APP_DATA_LOCATION`, `FEX_APP_CONFIG_LOCATION`, and `FEX_APP_CACHE_LOCATION` directories.

The saved stdout, stderr, and exit-status records accompany this report. Package setup and guest changes were confined to the disposable Colima VM/container; TLS and package signature verification remained enabled. The container used the host's CA trust bundle only to bootstrap its CA store and package lists over HTTPS.
