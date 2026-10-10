# Local experiments — 2026-10-10

## Actually performed: native capability probes

Host: MacBook Air (MacBookAir10,1), Apple M1, 8 cores, 8 GB RAM. macOS27.0 build26A428; Xcode27.0 build27A266a; Apple clang21.0.0 (clang-2100.3.34.2). SIP enabled. No valid signing identity. SDK/toolchain details: [host-toolchain.log](host-toolchain.log). Device serial/UUID/UDID deliberately excluded.

Executed [run-capability-probe.sh](run-capability-probe.sh) and [run-layout-probe.sh](run-layout-probe.sh), with the checked-in [source](capability-probe.c). No provisioning profile or special entitlement was supplied. These are developer probes, not shipped sandboxed/Hardened Runtime applications. No Wine, FEX, Windows install, privileged component, or security change was installed.

Results: [capability-probe.log](capability-probe.log), [layout-probe.log](layout-probe.log). Both binaries are single-slice ARM64 Mach-O; therefore these probe executables cannot run as an x86_64 Rosetta slice. `sysctl.proc_translated` query was unavailable (-1), not a successfully observed zero. The compile target and file inspection establish native probe architecture; do not reinterpret the unavailable query as a Rosetta measurement.

The kernel query returned1. Native page size was16384. Setting the 4 KB spawn attribute returned0, but child launch returned88 (Malformed Mach-o file). Xcode accepted the layout flags and that binary ran normally at16 KB; the 4 KB child still failed. This does **not** isolate the failure cause: the probes lack the fully provisioned Wine bundle. It neither disproves authorized 4 KB execution nor proves that obtaining an entitlement alone fixes it. No child was created; no crash log exists. There is no timing benchmark.

Compiled binaries are disposable local outputs; retained source, commands, logs and SDK hashes are the reproducibility record. `.gitignore` excludes the binaries.

## Wine milestones: NOT performed

A (ARM64 Wine built-in), B (x64 console through FEX), C (GUI) are **UNTESTED**. There is no suitable signing identity/profile and no complete published integrated runtime installed here. Building Wine before resolving the authorization gate would not validate the execution requirement. No Wine/FEX dependency hash is an experiment result; source-inspection revisions are in the research chapters.

## Reproduction procedure once prerequisites exist

This is a staged procedure, not a claimed successful end-to-end build. Missing public integration and entitlement issuance are explicit inputs; a fully reproducible B recipe cannot honestly be supplied until those inputs are available.

1. On a disposable non-admin test account, record host hardware without identifiers, OS build, selected Xcode/SDK, compiler and dependency versions. Preserve SIP/AMFI. Select an authorized Apple-issued cross-architecture profile and matching identity/App ID. Record entitlement names/profile expiry, never publish private keys or device identifiers. First reproduce these probes inside the provisioned bundle: actual4 KB child is the gate.
2. Obtain native Wine source at the upstream SHA in chapter02 or the named experimental fork SHA. Use fork only as a diagnostic baseline. Obtain a pinned llvm-mingw with ARM64EC support (fork notes used20260826), Bison and normal Wine build dependencies. Verify all **host** tools/modules are ARM64. Build out-of-tree with `CC=/usr/bin/clang`, native `-arch arm64`, and `configure --enable-archs=arm64ec,aarch64,i386,x86_64 --without-x --without-cups --without-pulse --without-alsa --without-gstreamer --without-vulkan --prefix=<isolated-install>`, then `make -j2` on this8 GB host. The component command comes from [published fork build notes](../evidence/native-wine-fork-build.md), not a local successful build.
3. Link the loader with the published layout flags in run-layout-probe.sh, construct Wine.app with the matching bundle ID and `LSUIElement`, embed the authorized profile, and sign each native component in the required order using caller-supplied credentials. Establish which JIT/Hardened Runtime exceptions are needed; do not guess that `allow-jit` authorizes cross-architecture mode. First launch ARM64 Wine using an isolated fresh `WINEPREFIX` and built-in ARM64 `cmd /c ver` and notepad. Capture stdout/stderr and crashes. Verify observed process and loaded module architecture; forbid Intel host fallback. **A acceptance:** native windows/API calls, page size and fixed mappings correct, SIP enabled, repeat from clean prefix.
4. For B, obtain FEX PE ARM64EC and WoW64 frontends plus the published Darwin UnixLib shim identified in chapter03. Resolve outstanding dependencies, per-thread TSO initialization, JIT allocation and invalidation against the selected Wine revision. The experimental fork reports `xtajit64.dll` and `xtajit.dll` paired with native UnixLibs via `WINEDLLPATH`; exact registration/export contracts must match the pinned frontend source. Do not copy random DLLs or assume a standalone Linux FEX binary works. Produce a machine-readable manifest of all revisions, patches, builds and installations. Stop if any integration source is missing.
5. Compile the tiny program below using the selected llvm-mingw `x86_64-w64-mingw32-gcc -O0 smoke.c -o smoke-x64.exe`; inspect the resulting PE machine header, imports and hash. Run through the explicitly selected ARM64EC/FEX runtime. Build an ARM64 variant as a control. Then extend with child process, TLS/callback, SEH/unwind, atomics, guard-page, VirtualProtect, and SMC fixtures before general application tests.
6. Instrument FEX entry and code-cache execution; record guest x64 PE identity, ARM64EC builtin identity, ARM64 UnixLib identity and native Wine/wineserver process state. Attach a debugger or collect process samples showing FEX-generated code executes and transitions to native Wine. Record `sysctl.proc_translated` when available, loaded native images and helper architectures. Universal launcher names and Activity Monitor alone are insufficient. **B acceptance:** output correct, exit0, trace proves FEX path, no Intel Mach-O host/helper required, 100 fresh runs and threaded variants pass.
7. C: build a minimal x64 Win32 window/message-loop application, test keyboard, mouse, clipboard, resizing/DPI and window close under winemac.drv. No DirectX needed. Preserve test source, commands, logs and screenshots when actually performed. Only then add DXMT as a separate experiment.

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

This validates separate4 KB guest protection through a write to the second page; a separate exception fixture must also prove first-page writes fault. It does not validate the complete Windows API or translator.
