# Local experiments — 2026-10-10

## Actually performed: four native capability variants

Host: MacBook Air (MacBookAir10,1), Apple M1, 8 cores, 8 GB RAM. macOS27.0 build26A428; Xcode27.0 build27A266a; Apple clang21.0.0 (clang-2100.3.34.2). SIP enabled. No valid signing identity or provisioning profile was available. Host details: [host-toolchain.log](host-toolchain.log). Device serial, UUID and UDID are excluded.

The [JSON capability harness](capability-probe.c) was compiled from the same source in two Mach-O layouts: normal linker layout and `-x86_64_layout_emulation` with `__PAGEZERO` set to `0x170000000`. Xcode's linker generated an **ad-hoc, linker-signed** signature for each binary. Each binary was also copied and re-signed with `codesign --sign -` (explicit ad-hoc signing). Thus there is no truly unsigned comparison here. For each layout, the original and re-signed copies share the same executable contents outside the code signature; comparing layouts necessarily uses separately linked binaries. This four-variant unprovisioned baseline is considered sufficiently characterized; do not expand it without a new authorization or a concrete diagnostic hypothesis.

| Layout | Linker-generated ad-hoc signature | Explicit `codesign --sign -` |
|---|---|---|
| Normal | [JSON](results/plain-linker-signed.result.jsonl), [load commands](results/plain-linker-signed.load-commands.txt), [signature](results/plain-linker-signed.signature.txt) | [JSON](results/plain-codesign-adhoc.result.jsonl), [load commands](results/plain-codesign-adhoc.load-commands.txt), [signature](results/plain-codesign-adhoc.signature.txt) |
| Large `__PAGEZERO` | [JSON](results/layout-linker-signed.result.jsonl), [load commands](results/layout-linker-signed.load-commands.txt), [signature](results/layout-linker-signed.signature.txt) | [JSON](results/layout-codesign-adhoc.result.jsonl), [load commands](results/layout-codesign-adhoc.load-commands.txt), [signature](results/layout-codesign-adhoc.signature.txt) |

All four processes reported ARM64, host page size16384, `cross_arch_x86_64=true`, custom x18 mode initially disabled, and `posix_spawnattr_set_4k_page_size_np` success. All four 4 KB child attempts returned88; no child process ran. The results do not identify whether layout, signing, entitlement, provisioning or their interaction caused the error. A harness exit code of0 means it completed and wrote JSON; the process launch outcome is `probe.spawn_4k_rc` inside that JSON.

The linker-generated signature reports a 4096-byte CodeDirectory hash page size; the explicit `codesign --sign -` signature reports16384 bytes. It changes more than a binary's label from “unsigned” to “signed,” so this comparison does not isolate signature presence alone. The larger `__PAGEZERO` is confirmed in `otool -l`; Xcode accepts and runs that parent executable at the host's16 KB page size. The four probe executables are ARM64 Mach-O. `sysctl.proc_translated` was unavailable (`rc=-1`), not a successful observation of zero. See per-variant SHA256, `file`, `codesign --verify`, stderr, and Unified Log capture artifacts beside each linked JSON file.

Per-variant process-name Unified Log calls were blocked inside the command sandbox and carry an explicit `unavailable` status. I then queried the same four process names outside the sandbox; macOS returned an empty result array in [unified-log-followup.json](results/unified-log-followup.json). No matching diagnostic entries or crash log were available because no child was created. This is **UNKNOWN** evidence about the underlying launch failure. A future capture now records the exact launch time window and performs a second, narrowly time-bounded query for `amfid`, `taskgated`, `launchd`, code-signing subsystem events, and messages mentioning `posix_spawn`, `EBADMACHO`, malformed Mach-O, or cross-architecture execution. Since a failed spawn can happen before the child exists, filtering only by the target process name is insufficient. An empty result from either query remains **UNKNOWN**, never proof that authorization was granted or denied. The new query was not run against the four baseline variants.

The harness exits zero after it records a failed child launch, so process status alone is not a CI success condition. [require-authorized-4k.py](require-authorized-4k.py) requires the spawn attribute call and spawn to return zero, a parent-reported child exit of zero without a signal, and a child JSON record that reports ARM64 and a 4096-byte page. It rejects the stored baseline (`spawn_4k_rc=88`) and accepts a synthetic success record; neither check repeats the platform experiment. The indexer pairs JSON records by `mode`, because a successful child prints before the waiting parent and therefore appears first in JSONL.

No developer profile, restricted entitlement, Developer ID signing identity or notarized build was tested. **Gate0A remains untested** because the required development authorization was unavailable here. **Gate0B remains untested** because there was no releasable provisioned bundle or unrelated recipient machine. This four-way comparison isolates linker layout and ad-hoc signing method only; provisioning/entitlement must be tested under an authorized account in a separate run.

## Native Wine build investigation: performed, build-only

The upstream Wine source is pinned to commit [`a15ee2ccf20e2fc9f470badd916855801933d31f`](https://github.com/wine-mirror/wine/commit/a15ee2ccf20e2fc9f470badd916855801933d31f), and the Windows cross-toolchain is the official `llvm-mingw 20261006` release (LLVM 23.1.3). The full configured component build completed successfully. It produced ARM64 Mach-O host tools and ARM64X PE `ntdll.dll`/`kernel32.dll` outputs; hashes, configure/build logs, and exact inputs are recorded in [native-wine-build](native-wine-build/README.md). The build does not test Apple authorization, execute Wine, or add the native 4 KB/process-layout work reported by CrossOver. No Windows executable was run, and the build has not yet been repeated from a second clean directory for byte-for-byte reproducibility.

## Wine runtime milestones: NOT performed

Native Wine A (ARM64 built-in), FEX B (x64 console), and GUI C are **UNTESTED**. No FEX runtime or Windows installer was installed. The component build result is not a runtime test and cannot resolve an authorization denial or stand in for a successful launch.

## Reproduction

Run `./research/experiments/run-capability-probe.sh` only when a new platform experiment is warranted. It builds both layouts, preserves linker-generated ad-hoc signatures, makes explicit ad-hoc-signature copies, and calls `capture-capability-variant.sh` to save JSON results, load commands, hashes, signature details, verification results, stderr, and timestamp-bounded Unified Log queries. `index-capability-results.py` creates a machine-readable manifest of layout, signature and process outcomes. The run does not alter system settings or sign with a developer identity. Set `CAPABILITY_PROBE_OUTPUT_DIR` to choose a separate output directory. CI should use `require-authorized-4k.py` on a `.result.jsonl`; do not gate on the harness exit status.

For authorized work, call `capture-capability-variant.sh LABEL /path/to/already-built/and/signed/executable` for every entitlement/provisioning/layout variant. With an authorized profile, add `--test-x18-transitions` to record entry/exit API state and `--test-tso` to record `thread_set_x86_64_compat` return codes on the current and a newly created thread. These probes test the API transitions, not x18 register preservation or memory-order correctness; those need separate ABI and litmus tests. The capture script only inspects and runs its input; it does not sign it, add entitlements or modify provisioning profiles. Preserve the signed input hash and profile/entitlement metadata separately, omitting private keys and device identifiers. Capture the same source fixture in each condition. A successful `codesign --verify` alone does not prove that a restricted entitlement is granted by the target OS.

## Wine execution procedure after Gate0A

1. On a disposable non-admin test account, record host hardware without identifiers, OS build, selected Xcode/SDK, compiler and dependency versions. Preserve SIP/AMFI. Use the authorized Apple-issued profile and matching identity/App ID. Record entitlement names and profile expiry, never publish keys or UDIDs. First prove an actual4 KB child before installing Wine.
2. Obtain native Wine source at the upstream SHA in chapter02 or the named experimental fork SHA. Use the fork as a diagnostic baseline. Obtain a pinned llvm-mingw with ARM64EC support (fork notes used20260826), Bison and normal Wine build dependencies. Verify all **host** tools/modules are ARM64. Build out-of-tree with `CC=/usr/bin/clang`, native `-arch arm64`, and `configure --enable-archs=arm64ec,aarch64,i386,x86_64 --without-x --without-cups --without-pulse --without-alsa --without-gstreamer --without-vulkan --prefix=<isolated-install>`, then `make -j2` on this8 GB host. This command is copied from [published fork build notes](../evidence/native-wine-fork-build.md); it has not been built locally.
3. Link the loader with the published layout flags in `run-capability-probe.sh`, construct Wine.app with the matching bundle ID and `LSUIElement`, embed the authorized profile, and sign each native component in the required order using caller-supplied credentials. Establish which JIT/Hardened Runtime exceptions are needed. Launch ARM64 Wine on an isolated fresh `WINEPREFIX` and built-in ARM64 `cmd /c ver` and Notepad. Capture stdout/stderr and crashes. Verify process and loaded module architectures. **A acceptance:** native windows/API calls, page size and fixed mappings correct, SIP enabled, repeat from a clean prefix.
4. For B, obtain FEX PE ARM64EC and WoW64 frontends plus the Darwin UnixLib shim identified in chapter03. Resolve dependencies, per-thread TSO initialization, JIT allocation and invalidation. The experimental fork reports `xtajit64.dll` and `xtajit.dll` paired with native UnixLibs via `WINEDLLPATH`; exact registration/export contracts must match the pinned frontend. Do not assume a standalone Linux FEX binary works. Produce a machine-readable manifest of revisions, patches, builds and installations; stop if integration source is missing.
5. Compile the tiny program below using `x86_64-w64-mingw32-gcc -O0 smoke.c -o smoke-x64.exe`; inspect its PE machine header, imports and hash. Run through the explicitly selected ARM64EC/FEX runtime. Build an ARM64 variant as a control. Extend with child process, TLS/callback, SEH/unwind, atomics, guard-page, VirtualProtect and SMC fixtures before general application tests.
6. Instrument FEX entry and code-cache execution; record guest x64 PE, ARM64EC builtin, ARM64 UnixLib and native Wine/wineserver process state. Attach a debugger or collect process samples showing FEX-generated code and transitions to native Wine. Record `sysctl.proc_translated` when available, loaded images and helper architectures. **B acceptance:** correct output, exit0, trace proves FEX path, no Intel Mach-O host/helper, 100 fresh runs and threaded variants pass.
7. For C, build an x64 Win32 window/message-loop app and test keyboard, mouse, clipboard, resize/DPI and close under winemac.drv. No DirectX is required. Preserve source, commands, logs and screenshots when run; add DXMT as a separate later experiment.

Tiny test source (proposed, **not built or executed** here):

```c
#include <windows.h>
#include <stdio.h>
int main(void) {
    SYSTEM_INFO s; GetSystemInfo(&s);
    DWORD tls=TlsAlloc();
    if (tls==TLS_OUT_OF_INDEXES || !TlsSetValue(tls,(void*)0x1234) ||
        TlsGetValue(tls)!=(void*)0x1234) return 1;
    void *p=VirtualAlloc(NULL,8192,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
    DWORD old;
    if (!p || s.dwPageSize!=4096 ||
        !VirtualProtect(p,4096,PAGE_READONLY,&old)) return 2;
    ((volatile char*)p)[4096]=42;
    printf("pid=%lu pages=%lu tls=ok second_page=%d\n",
           (unsigned long)GetCurrentProcessId(),(unsigned long)s.dwPageSize,
           ((volatile char*)p)[4096]);
    VirtualFree(p,0,MEM_RELEASE); TlsFree(tls); return 0;
}
```

This checks separate4 KB guest protection by writing the second page; a separate exception fixture must prove a write to the first page faults. It does not establish the complete Windows API or translator.
