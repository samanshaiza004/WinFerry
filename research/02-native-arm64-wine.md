# Native ARM64 Wine on macOS

Assessment date: 2026-10-10. Findings use the evidence vocabulary in README.md. A source containing code is evidence of implementation, not evidence that the implementation is correct or generally compatible.

## What changed in 2026

**REPORTED:** Brendan Shanks described a macOS 26.5 execution environment usable by native Wine: custom x18, 4 KB processes, low-address layout, and per-thread x86 memory ordering. His August announcement described provisioning requirements; September replies disputed free-account access. Treat the entitlement route as unresolved, not established. [Wine-devel, Aug 7–Sep 9](https://list.winehq.org/hyperkitty/list/wine-devel@list.winehq.org/thread/CKG5CEN2BE5VRXZ7O7NX4YUSBH3247WH/).

**VERIFIED:** The locally installed macOS 27 SDK declares all the relevant APIs. Its annotations are **26.4** for custom x18, **26.0** for the 4 KB spawn attribute, and **26.6** for the capability query. These are declaration availability annotations; they do not establish when the full, entitled combination became deployable. Use 26.5 as the reported minimum of the CrossOver implementation, and validate each supported OS build. [SDK inspection, exact lines and hashes](evidence/native-sdk-inspection.txt); [CrossOver preview](https://www.codeweavers.com/blog/mjohnson/2026/7/31/crossover-preview-the-right-to-bear-arm64-on-mac).

Older categorical claims that native Wine is impossible on macOS are obsolete. Conversely, new APIs alone do not make stock upstream Wine a finished runtime. **INFERRED** from the source audit below.

## ABI: three separate boundaries

1. Windows x64 application → FEX-generated ARM64 instructions.
2. Translated x64 → ARM64EC Wine PE implementation through architecture-aware call checks/thunks.
3. Windows ABI → Darwin ARM64 Unix libraries and Cocoa/Metal through Wine's Unix interface.

**VERIFIED:** ARM64EC is distinct from ordinary Windows ARM64; it preserves x64 software conventions, maps register state, and requires signature-specific entry/exit thunks. It is not a generic mechanism for loading arbitrary ARM64 DLLs into x64 processes. Mixed unwinding needs EC-aware metadata, including full SIMD state restoration. Guest JIT code defaults to x64 unless explicitly registered as EC. [Microsoft ARM64EC ABI](https://learn.microsoft.com/en-us/windows/arm/arm64ec-abi), [interoperability](https://learn.microsoft.com/en-us/windows/arm/arm64ec).

**VERIFIED:** Apple's SDK reserves x18 normally. Custom mode must be entered before foreign ABI execution and left before **any** macOS library/framework call, including POSIX calls in a signal handler. Toggling to the already-current mode aborts. Leaving destroys the custom x18 value; Wine must preserve/restore its TEB separately. A signal handler must inspect mode, temporarily leave if needed, and return with the correct TEB. [SDK arm64.h:45–141](evidence/native-sdk-inspection.txt).

**INFERRED:** Correctness requires assembly veneers and a boundary audit, not merely one toggle in main(). Test syscall dispatch, callbacks, APC delivery, thread suspension, SEH, C++ exceptions, longjmp, nested callbacks, and faults inside generated code. Unwinding has to preserve both the Windows context and Darwin ABI state. A fault handler cannot casually call logging or pthread routines while custom mode is active. The official SDK contract makes these requirements unavoidable.

**REPORTED:** A July independent Wine experiment booted a prefix and builtin applications with the macOS driver using layout/protection changes and old-SDK x18 behavior. This was a local series, not a published general x64 runtime. [July discussion](https://list.winehq.org/hyperkitty/list/wine-devel@list.winehq.org/thread/2WWSHLWFTPASROXDF6HRP3VZUKYJAWNF/).

## Compatibility and implementation matrix

| Area | Evidence / OS requirement | Entitlement/security | Required engineering | Status / workaround limits |
|---|---|---|---|---|
| Windows x18 TEB | SDK custom mode annotated 26.4; usable stack reported 26.5 | July report names `com.apple.security.custom-x18-abi-toggle`; August reports broader restricted cross-architecture capability | Save TEB, toggle at all Unix boundaries, restore after signals and callbacks | API **VERIFIED**, complete integration **UNKNOWN**. Old SDK targeting 11/12 is a reported compatibility workaround, not a durable release strategy |
| Windows 4 KB protection granularity | `posix_spawnattr_set_4k_page_size_np`, SDK spawn.h:165 annotated26.0; combination reported26.5 | Restricted capability reported; ad-hoc signing alone not established | Launch/re-exec before loading Wine modules; bound retries; verify actual page size | API **VERIFIED**. Native probe remained16 KB and 4 KB child spawn failed; cannot infer all signed configurations |
| PAGEZERO / low4 GB | Linker/kernel changes reported26.4; local Xcode27 accepts flag | Cross-architecture authorization reported | `-x86_64_layout_emulation`; reserve/remap low area, avoid dyld collisions; Wine fixed mappings | Flag acceptance **VERIFIED**, provisioned remapping **UNTESTED**. Relocating shared data does not establish binary compatibility with fixed-address x64 consumers |
| Shared data/fixed addresses | Windows shared-data address reported0x7ffe0000 | Same process layout permissions | Map KUSER_SHARED_DATA and TEBs at valid guest addresses; distinguish host and guest reservations | **REPORTED/INFERRED**; changing Wine-owned constants cannot change third-party hardcoded accesses |
| Native JIT/W^X | Apple ARM64 JIT model; MAP_JIT path present in experimental fork | Ordinary `allow-jit` differs from restricted cross-architecture capability | Controlled code-cache allocation; per-thread write protection; instruction-cache flush; race-safe publish/invalidation | Code **VERIFIED**; production correctness **UNKNOWN**. Permission broadening is not a correctness proof |
| Guest VirtualProtect / SMC | Guest pages can contain translated x86 bytes, distinct from host executable ARM64 cache | Guest RWX need not imply every guest page is native executable | Track writes, invalidate translations, concurrent execution/write tests, guard/DEP/COW semantics | **INFERRED**; 4 KB OS mode solves granularity, not translation invalidation |
| x86 TSO | SDK mach_traps.h:305 declares `thread_set_x86_64_compat(uint32_t)`; rollout reported26.5 | Restricted capability reported | Enable on every emulation thread, child thread path and re-entry; validate software barrier fallback | Declaration **VERIFIED**, inheritance limitation **REPORTED**. Hardware TSO does not repair guest atomics, signals or cache invalidation automatically |
| Standard Wine synchronization | Wineserver baseline; experimental Darwin in-process backend in fork | No reason to equate this with hardware TSO | Keep server fallback; test wait-all/any, abandoned mutexes, events, process death | Fork code **VERIFIED**, broad conformance **UNKNOWN**. Postpone new fast sync until baseline passes |
| Distribution | Provisioned loader described by maintainer; fork requires caller-supplied profile/identity | Restricted capability, App ID and signing identity; recipient UDID described for development provisioning | Establish release signing/profile policy, expiry and update handling, fresh unrelated stock Mac install | **UNKNOWN** for general OSS distribution; no SIP workaround accepted |
| Gatekeeper / notarization | Standard macOS distribution mechanisms | Hardened Runtime/JIT exceptions and notarization are distinct from capability grant | Sign native nested code correctly, staple ticket where applicable, test downloaded bundle | Ordinary documented route; combination with restricted loader **UNKNOWN** |

Sources for the report-only OS and entitlement rows are the two Wine-devel discussions above. Local annotations and observations are preserved separately so deployment claims cannot silently become verified facts.

## Public source inspection and upstream status

Pinned upstream mirror: **a15ee2ccf20e2fc9f470badd916855801933d31f**, committed 2026-10-09T16:31:55Z. Inspected `loader/main.c`, `dlls/ntdll/unix/signal_arm64.c`, and `virtual.c`. The inspected loader and signal file do **not** contain the new custom-x18 or 4 KB spawn calls. This is a bounded negative finding, not proof that every relevant MR is unmerged. [Upstream loader](https://github.com/wine-mirror/wine/blob/a15ee2ccf20e2fc9f470badd916855801933d31f/loader/main.c), [signal code](https://github.com/wine-mirror/wine/blob/a15ee2ccf20e2fc9f470badd916855801933d31f/dlls/ntdll/unix/signal_arm64.c), [metadata](evidence/native-wine-upstream-metadata.json).

**VERIFIED:** Experimental `gzimbric/wine-arm64-macos` snapshot **21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6** (Oct9) contains custom-x18 helper/assembly changes (`signal_arm64.c:62–69`, signal wrappers around1740–1800), bounded 4 KB re-exec (`loader/main.c:203–232`), and MAP_JIT allocation (`virtual.c:2268`, opt-in3738). Its Wine base is2550c238151a00e43908561f32b6e131603ec6f7. This is the newest substantive public fork located in this investigation, not a claim that no newer work exists. [Fork source](https://github.com/gzimbric/wine-arm64-macos/tree/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6), [build notes](evidence/native-wine-fork-build.md), [status](evidence/native-wine-fork-status.md).

**REPORTED:** Its author exercised Windows ARM64 and x64/i386 through external FEX/DXMT on one development machine. **VERIFIED:** The same notes explicitly omit external integration patches, production JIT handling and clean-machine reproduction. Do not adopt all sixteen changes wholesale: several are application workarounds or experimental synchronization rather than prerequisites. Prefer upstream loader/ABI work, then a narrow reviewed patch queue.

MR11638 is a different Apple Silicon proposal using relocated shared data and old-SDK x18 behavior; MR11668 concerns CPU identification. Mailing-list mirrors show discussion/approval events, but approval is not synonymous with complete native support. Wine GitLab's anti-bot access denied direct MR inspection, so merged state of the complete platform series remains **UNKNOWN**. [MR11638](https://gitlab.winehq.org/wine/wine/-/merge_requests/11638), [August mirror](https://list.winehq.org/hyperkitty/list/wine-gitlab@list.winehq.org/latest?count=25&page=35).

## Answer to the stock-Mac installation question

**UNKNOWN, and a release blocker.** Free-account entitlement availability is contested in primary correspondence. Development provisioning of registered Macs does not demonstrate a redistributable app usable by unrelated users. Users need not necessarily enroll in a developer program if the publisher can lawfully distribute a properly entitled binary; that route still needs confirmation and an independent installation test. A free product may have publisher signing costs without charging users. The stricter goal of *no paid developer enrollment by anyone* is not established.

Minimum evidence: an authorized publisher creates a release-signed loader, documents exactly which capabilities/profile it needs, and an unrelated user with no developer account downloads and runs it on a stock Mac with SIP/AMFI enabled. Repeat after profile renewal and runtime update. Obtain Apple's public or written capability/distribution conditions. Do not ship around this uncertainty by disabling security protections.
