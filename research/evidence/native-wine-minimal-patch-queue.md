# Minimal Darwin patch queue for the native Wine proof

Assessment date: 2026-10-10. This document tracks a source-level porting plan and its first build-only patch slice. It compares Wine mirror commit `a15ee2ccf20e2fc9f470badd916855801933d31f` (the build-only baseline) with public experimental fork `gzimbric/wine-arm64-macos` commit `21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6`, based on Wine commit `2550c238151a00e43908561f32b6e131603ec6f7`.

## 2026-10-10 build-only implementation update

A bounded first slice is implemented as [`0001-loader-request-4k-process-pages.patch`](../experiments/native-wine-build/patches/darwin-build-only/0001-loader-request-4k-process-pages.patch) plus [`0002-darwin-arm64-low-address-layout.patch`](../experiments/native-wine-build/patches/darwin-build-only/0002-darwin-arm64-low-address-layout.patch). The structural contract test passes. A fresh build applied both patches to a disposable copy of the pinned source, configured the low-address layout through Wine's build system, and verified the emitted loader flags before linking. The prior generated-Makefile override is removed. The linked artifact remains unlaunched; see the updated [build record](../experiments/native-wine-build/darwin-loader-build.md) and [machine-readable result](../experiments/native-wine-build/darwin-loader-build.json).

This did not launch the loader or request a 4 KB process, and it did not exercise authorization. The platform-only capability harness remains independent. Windows x18 transitions, signal/exception handling, and FEX are still unimplemented and deferred.

## Gate 0A native ARM64 Wine builtin

The minimum credible experiment is a provisioned Wine app bundle that launches an ARM64 Wine builtin. It does not need FEX, x86-64 Windows code, DXMT, DXVK, a new synchronization backend, or game-specific fixes. The baseline compiles native host binaries and ARM64X PE modules but does not contain the reported new Darwin execution path; see [the pinned source audit](native-wine-upstream-a15ee2-audit.md) and [first build record](../experiments/native-wine-build/README.md).

| Queue item | Required behavior | Evidence and limit | Gate |
| --- | --- | --- | --- |
| 1. Loader and process layout | Build the loader with current low-address layout flags; request the 4 KB process before Wine maps guest images; bound re-exec to one attempt; verify the process reports 4096-byte pages. Keep a diagnostic path that reports the actual failure. | The public fork's `loader/main.c:203–232` re-execs using `POSIX_SPAWN_SETEXEC` and `posix_spawnattr_set_4k_page_size_np`, with a PID guard against a retry loop. Its documented low-address linker command is manual: the fork diff does not update `configure.ac` or the loader makefile. The pinned upstream has an older 4 KB `PAGEZERO` flag but lacks the spawn API and newer layout flag. | Required for the reported current-SDK route; linker configuration and authorization are still external prerequisites. |
| 2. Windows x18 ABI boundary | Save the Windows TEB value separately; enter custom-x18 mode before running Windows ARM64/ARM64EC code; leave before calling Darwin APIs; restore state after each transition. Route all crossings through a small audited veneer. | The public fork's `signal_arm64.c` has C helpers plus assembly veneers preserving GPR/SIMD state around mode changes, and signal-context paths set x18 from the Wine TEB. A source implementation is not proof that every callback/exception path is correct. | Required before claiming a Win32 builtin execution. |
| 3. Signal and exception crossings | Make signal entry inspect ABI mode, safely enter the Darwin mode for OS operations, preserve the Windows context and TEB, then resume with the original mode. Cover synchronous faults and asynchronous delivery. | The public fork wraps ARM64 signal handlers in `signal_arm64.c` to toggle custom-x18 mode. The branch report itself lists exceptions, APCs, callbacks, and thread suspension as remaining audit work. | Required to establish correctness; first smoke can be narrow, but cannot be promoted to reliable runtime without the tests. |
| 4. Bundle signing and authorization | Put the loader in the required app-like bundle, use an Apple-issued profile/entitlement for the experiment, sign every executable consistently, and record profile identity without checking credentials into source control. | Apple documents that restricted macOS entitlements require profile authorization; public evidence does not answer whether an independent open-source project can obtain this exact capability or distribute it through Developer ID. See [Gate 0A/0B authorization questions](apple-authorization-process.md). | Required to attempt the child launch on the stock host. |

The remaining implementation should be a small forward-port of the needed behaviors, not a cherry-pick of the whole experimental branch. Its Wine base is older than the pinned build source, and a mechanical cherry-pick or clean rebase has not been tested. Keep each behavior in an isolated patch and record the upstream file/commit it changes. The initial build-only recipe exposed that Wine expands loader link flags into the generated Makefile, so a make-time override is ineffective. The new build-system patch wires the experimental layout into the Darwin ARM64 configure branch; it remains build-only and does not establish that the layout or loader works at runtime.

## Defer until native Wine builtin passes

- **FEX Darwin UnixLib and ARM64EC transitions:** the fork's build notes identify external FEX changes and per-emulation-thread hardware TSO setup. They are necessary for the separate x86-64 execution gate, not for proving native ARM64 Wine startup. In particular, the reported non-inheritance of x86 TSO is a FEX thread-creation concern; it must not be papered over by Wine's host process.
- **`MAP_JIT` for translated code:** the fork's opt-in `virtual.c` path backs generated ARM64EC code. This is relevant when FEX is active; it is not evidence of a production-safe executable-code cache and should not be pulled into the native builtin proof without a demonstrated need.
- **New in-process synchronization:** keep Wine's existing wineserver path for the first run. The separate backend changes server protocol and adds compatibility risk without resolving launch authorization or ABI crossings.
- **DXMT, Vulkan, D3DMetal, Steam, Dock behavior, FAudio, and game workarounds:** graphics and app integration are separate milestones. None helps diagnose whether a provisioned native ARM64 Wine process can start a builtin.

## Minimal x86-64/FEX extension after Gate 0A

Only after a native Wine builtin succeeds, add the FEX ARM64EC execution path in a separate patch set. The required proof then includes: FEX guest instruction execution, its Darwin host-services adapter, per-thread TSO setup on every emulation thread, x64-to-ARM64EC transition and unwind tests, and JIT memory permission/invalidation tests. A `.text` section or ARM64X machine type cannot substitute for any of these runtime checks.

## Acceptance and stop conditions

1. Keep SIP enabled. Do not diagnose entitlement errors by disabling system protections.
2. The child must be launched with the 4 KB attribute, report 4096-byte pages, and return its own result; the harness process exit code alone is insufficient.
3. Confirm the process architecture and signing/profile state from the launched process. Record that no x86-64 Wine helper or Rosetta process participated.
4. Execute one Wine builtin, then repeat thread creation, callback, signal/fault, and exception cases before broadening to x86-64 code.
5. If Apple does not make an authorized development profile available, stop the Darwin runtime attempt at Gate 0A and evaluate the separately documented Linux VM route. Do not spend effort porting FEX into an unauthorized host process.

## Sources

- [Pinned public Wine baseline](https://github.com/wine-mirror/wine/tree/a15ee2ccf20e2fc9f470badd916855801933d31f); local archive SHA-256 `f87b071f5f19f4cc5b6a51d3000ae03ee791325d5873ba221da191fd5b933a41`.
- [Experimental Wine fork at exact revision](https://github.com/gzimbric/wine-arm64-macos/tree/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6); base `2550c238151a00e43908561f32b6e131603ec6f7`.
- [Fork comparison: 21 commits, 44 changed files](https://github.com/gzimbric/wine-arm64-macos/compare/2550c238151a00e43908561f32b6e131603ec6f7...21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6).
- Exact source locations: [bounded 4 KB loader re-exec](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/loader/main.c#L203), [x18 helpers and signal context](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/dlls/ntdll/unix/signal_arm64.c#L64), [signal-handler wrappers](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/dlls/ntdll/unix/signal_arm64.c#L1738), [opt-in ARM64EC `MAP_JIT` view](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/dlls/ntdll/unix/virtual.c#L2258), and [manual loader link flags](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/docs/macos-arm64/BUILD.md#L32).
- [Fork's build and integration notes](native-wine-fork-build.md), [reported status](native-wine-fork-status.md), and [pinned upstream audit](native-wine-upstream-a15ee2-audit.md).
- [Apple provisioning-profile signing model, TN3125](https://developer.apple.com/documentation/technotes/tn3125-inside-code-signing-provisioning-profiles).
- [Wine-devel discussion of the native process requirements and entitlement access](https://list.winehq.org/hyperkitty/list/wine-devel@list.winehq.org/thread/CKG5CEN2BE5VRXZ7O7NX4YUSBH3247WH/).

**Finding:** a narrow first native ARM64 builtin experiment remains justified after Gate 0A is authorized. The loader/re-exec and layout build slice is now locally demonstrated, but execution, authorization, and the remaining ABI/signal patches are not. The best publicly documented end-to-end execution report is materially broader, but it depends on external FEX/DXMT work and does not supply a clean, independently reproducible package.
