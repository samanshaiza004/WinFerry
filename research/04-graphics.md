# Graphics architecture assessment

Research cutoff: **2026-10-10**. Source snapshots below are pinned to the newest public commit returned by GitHub's commit API at or before the cutoff. **VERIFIED** means the cited source/build definition exists; it does not mean this investigation reproduced the build or application. No GPU performance measurements or runtime graphics experiments were performed.

## Decision

**INFERRED — Choose Wine's existing desktop drawing/windowing first, then DXMT for explicitly tested D3D10/11 applications. Postpone generalized DXVK/MoltenVK and D3D12 support.** A Direct3D translator cannot solve Wine's USER/GDI, COM, installer, font, clipboard, or application-runtime compatibility. In particular, the proposed CPU proof needs no accelerated Direct3D; make the native Wine windowing and x86-64 execution path work before adding another ABI-sensitive subsystem. DXMT is unusually relevant because current source contains both an ARM64EC Windows cross-build and a native ARM64 Darwin companion build. The Vulkan alternatives have concrete feature mismatches, not merely an extra layer of overhead. See the evidence below.

## Revisions and evidence

| Component | Inspected revision | Commit date UTC | Primary evidence |
|---|---|---|---|
| DXMT | `e94c312f5c054263acf261cfa109edf13e757587` | 2026-10-06 13:26:23 | [repository at revision](https://github.com/3Shain/dxmt/tree/e94c312f5c054263acf261cfa109edf13e757587) |
| DXVK | `71ec7b5be6c517db39bcca4d38f38a63f6ddbc56` | 2026-10-10 14:51:52 | [repository at revision](https://github.com/doitsujin/dxvk/tree/71ec7b5be6c517db39bcca4d38f38a63f6ddbc56) |
| MoltenVK | `67b2682699d7903606b97a0392061d85d27d49e6` | 2026-10-08 08:37:16 | [repository at revision](https://github.com/KhronosGroup/MoltenVK/tree/67b2682699d7903606b97a0392061d85d27d49e6) |
| vkd3d-proton | `2230755878b01993b4b82d0ac0c0624f3ab4d333` | 2026-10-06 10:40:08 | [repository at revision](https://github.com/HansKristian-Work/vkd3d-proton/tree/2230755878b01993b4b82d0ac0c0624f3ab4d333) |
| UTM d3dmetal-native | `d374b21668f94b7b7b059f152794fdb93e944b84` | 2026-10-07 06:38:03 | [README at revision](https://github.com/utmapp/d3dmetal-native/blob/d374b21668f94b7b7b059f152794fdb93e944b84/README.md) |

The local `evidence/graphics-*-revision.json` files preserve full commit metadata; `graphics-sha256.tsv` fingerprints fetched source files. These are source-inspection evidence, not build logs. October activity is directly verified by the pinned commits. No claim is made that each project's latest CI job passed.

## Comparison

| Path | Verified implementation | Rosetta-free relevance | Initial-release decision |
|---|---|---|---|
| D3D10/11 → DXMT → Metal | D3D10/11 implementation, Windows PE and Darwin unixlib, ARM64EC CI definitions | Strongest candidate; match ARM64EC PE, ARM64 unixlib, ARM64 Wine, and translator transition ABI | Include only after native CPU/windowing proof and per-app graphics tests |
| D3D8/9/10/11 → DXVK → Vulkan → MoltenVK → Metal | DXVK Windows DLLs and MoltenVK Darwin implementation exist | CPU architecture alone is insufficient; current Vulkan required-feature profile conflicts with MoltenVK | Later, only a version-pinned supported fork/profile with feature evidence |
| D3D12 → vkd3d-proton → Vulkan → MoltenVK → Metal | D3D12-over-Vulkan implementation exists and Linux aarch64 build instructions exist | Not evidence of Darwin/ARM64EC end-to-end support; explicit required-feature rejection exists | Postpone |
| D3D → Apple's D3DMetal | Proprietary evaluation environment exists; third-party Darwin wrapper reports x86_64 framework | Available wrapper explicitly uses Rosetta on Apple Silicon | Optional separately licensed research baseline; no required dependency |

## DXMT: strongest open-source Metal path

**VERIFIED — Build architecture.** At the pinned revision, `.github/workflows/ci.yml` defines ARM64EC cross-build jobs (lines 519–608) using Wine `wine-11.2`, llvm-mingw `20260908`, and native ARM64 LLVM; lines 611–641 separately build ARM64 Mach-O libraries. `build-arm64ec.txt` declares a Windows aarch64 target and ARM64X flags. `meson.build` lines 173–205 distinguish Windows `aarch64-windows` artifacts from Darwin native compilation with `-arch arm64`. Thus ARM64EC PE presence and ARM64 Darwin presence are separately evidenced. These configurations do **not** prove that an arbitrary x86-64 game uses FEX rather than Rosetta. [CI](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/.github/workflows/ci.yml#L519), [cross-file](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/build-arm64ec.txt), [Meson](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/meson.build#L173).

**VERIFIED — Wine coupling.** The Darwin `winemetal.so` links against `winemac.so` and `ntdll.so`, with Metal, MetalFX, Cocoa, QuartzCore, and SQLite. Source creates the Metal presentation view through Wine mac-driver internals, resolves `macdrv_functions` or individual symbols, and accesses `macdrv_win_data.client_cocoa_view`. This is a real compatibility seam that must be preserved against the chosen Wine revision; it is not a completely independent D3D library. [unixlib build](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/winemetal/unix/meson.build#L6), [bridge lines 1656–1741](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/winemetal/unix/winemetal_unix.c#L1656).

**VERIFIED — Shader/cache and synchronization machinery already exists.** DXMT builds against LLVM 15 and Apple's Metal toolchain. Its internal shader cache uses a Metal-version-specific database and versioned cache schema; native cache code uses SQLite. The native command bridge implements Metal buffer allocation/storage mode, resource-usage declarations, command-buffer commits, and compute/render/blit fence waits and updates. Reuse these mechanisms, rather than designing a new shader cache or assuming unified memory eliminates resource barriers. [build prerequisites](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/docs/DEVELOPMENT.md#L3), [shader cache](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/dxmt/dxmt_shader_cache.cpp#L21), [cache storage](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/winemetal/unix/cache.c#L46), [Metal bridge](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/winemetal/unix/winemetal_unix.c#L756).

**VERIFIED / UNKNOWN — API completeness.** The project advertises D3D10/11; the inspected D3D11 device source still has `E_NOTIMPL` returns and an explicit unimplemented-query path. Current source also contains D3D12, but `enable_d3d12` defaults to false and the ARM64EC CI jobs do not enable it. Experimental source presence must not become a product promise. Device-specific feature coverage and performance require a test matrix; no universal D3D11 or D3D12 claim is justified here. [README](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/README.md), [device query handling](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/src/d3d11/d3d11_device.cpp#L979), [default options](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/meson.options).

**INFERRED — Integration requirements.** Pin Wine, DXMT, native LLVM, PE toolchain, translator, and mac-driver ABI together. Test both x86-64 guest → ARM64EC D3D DLL → ARM64 unixlib calls and callbacks. Keep DLL overrides prefix-local and reversible. Measure first launch/cold shader cache separately from warm launch. API-layer count is not a performance measurement.

## DXVK + MoltenVK: an actual capability mismatch

**VERIFIED — Newer MoltenVK is a Vulkan 1.4 subset, not the old Vulkan 1.2-only implementation.** Its README explicitly distinguishes direct mappings, emulation, and unsupported capability. It supports public Metal APIs by default; optional private-Metal builds exist and can disqualify App Store submission. Never infer compatibility solely from the reported Vulkan version. [README lines 375–409](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/README.md#L375), [private API option](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/README.md#L302).

**VERIFIED — Current DXVK's profile requires robustness2 `nullDescriptor` and `robustBufferAccess2`; current MoltenVK reports both false.** MoltenVK advertises the robustness2 extension, but its feature fields remain false at `MVKDevice.mm` lines 635–638. This is a particularly important counterexample to extension-name checking. DXVK's required profile also includes maintenance5/6 and depth-clip functionality. A stock combination cannot be assumed viable; a downstream patch must provide correct semantics, not simply bypass checks. [DXVK profile lines 77–115](https://github.com/doitsujin/dxvk/blob/71ec7b5be6c517db39bcca4d38f38a63f6ddbc56/VP_DXVK_requirements.json#L77), [MoltenVK capability code](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/MoltenVK/MoltenVK/GPUObjects/MVKDevice.mm#L635).

**VERIFIED — Caching crosses two translators.** DXVK has shader-cache controls and optionally uses Vulkan graphics-pipeline libraries. MoltenVK converts SPIR-V to MSL and documents Vulkan pipeline-cache serialization to avoid repeated conversion. **INFERRED:** preserve separate versioned caches and test invalidation on translator, GPU family, macOS, and shader-compiler changes. Double translation can add CPU work and semantic adaptation, but no overhead percentage can be stated without measurement. [DXVK cache documentation](https://github.com/doitsujin/dxvk/blob/71ec7b5be6c517db39bcca4d38f38a63f6ddbc56/README.md#L96), [MoltenVK runtime guide](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/Docs/MoltenVK_Runtime_UserGuide.md#L611).

**UNKNOWN — ARM64EC/Darwin end-to-end readiness.** The inspected DXVK main build/README does not establish a supported ARM64EC-on-native-macOS stack. Retaining an x86-64 PE translator under FEX may be possible but adds guest CPU work; it does not require loading an x86-64 Mach-O library. Independently verify Wine Vulkan thunk support, ARM64 host MoltenVK, surface presentation, and D3D feature semantics. For D3D9, first test Wine's existing implementation; add a known working DXVK-derived macOS fork only for applications with demonstrated benefit.

## vkd3d-proton + MoltenVK: D3D12 remains outside the initial scope

**VERIFIED — vkd3d-proton aggressively targets modern Vulkan drivers.** Its README requires Vulkan 1.3, extensive update-after-bind descriptor indexing, shaderDrawParameters, robustness2, and push descriptors. Linux aarch64 build instructions demonstrate Linux host builds, not an ARM64EC DLL or macOS integration. [requirements](https://github.com/HansKristian-Work/vkd3d-proton/blob/2230755878b01993b4b82d0ac0c0624f3ab4d333/README.md#L17), [aarch64 recipe](https://github.com/HansKristian-Work/vkd3d-proton/blob/2230755878b01993b4b82d0ac0c0624f3ab4d333/README.md#L116).

**VERIFIED — Device creation explicitly returns `E_INVALIDARG` when `robustBufferAccess2`, `robustImageAccess2`, or `nullDescriptor` is missing.** Against the pinned MoltenVK capability code this is a direct blocker. Earlier claims that MoltenVK has no descriptor indexing are stale: the present code includes runtime descriptor arrays, update-after-bind features, and million-entry limits for several tier-2 resource classes. That progress does not remove the robustness blocker or prove D3D12 game compatibility. [vkd3d rejection lines 2639–2650](https://github.com/HansKristian-Work/vkd3d-proton/blob/2230755878b01993b4b82d0ac0c0624f3ab4d333/libs/vkd3d/device.c#L2639), [MoltenVK descriptor capabilities](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/MoltenVK/MoltenVK/GPUObjects/MVKDevice.mm#L190), [limits](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/MoltenVK/MoltenVK/GPUObjects/MVKDevice.mm#L895).

**REPORTED — Maintainer discussions.** MoltenVK issue 2158 discusses the D3D12 bindless/sparse-resource roadmap. Its older future-tense promises are not implemented-feature evidence; current source above takes precedence. [issue opened 2024-02-10, maintainer response 2024-02-13](https://github.com/KhronosGroup/MoltenVK/issues/2158).

## Apple's D3DMetal and GPTK

**VERIFIED — Apple currently advertises Game Porting Toolkit 4 and an evaluation environment for Windows executables, including Metal 4 support.** This is an evaluation/porting product; the open-source skills/sample companion repository does not make D3DMetal open source. [Apple's product page, accessed 2026-10-10](https://developer.apple.com/games/game-porting-toolkit/).

**REPORTED — UTM's current `d3dmetal-native` README says the framework is x86_64-only and its Apple Silicon process runs under Rosetta 2.** This is evidence for that wrapper/framework path, not a claim that every future Apple framework distribution must be x86_64. The wrapper requires users to obtain Apple's framework and excludes it from the project. We did not download or inspect the current GPTK binary/SLA; its exact redistribution permissions remain **UNKNOWN**. Do not repeat a blanket “all redistribution prohibited” claim from old GPTK versions. Apple says accepted English agreements are binding and current. [wrapper requirements](https://github.com/utmapp/d3dmetal-native/blob/d374b21668f94b7b7b059f152794fdb93e944b84/README.md#L61), [Apple agreements](https://developer.apple.com/support/terms/).

**INFERRED — Keep D3DMetal outside the core dependency graph.** It fails the fully open-source preferred-path requirement regardless of whether a particular SLA permits limited redistribution. A separately installed, explicitly licensed baseline can help diagnose Wine-versus-graphics failures, but no mandatory proprietary component belongs in this runtime.

## Licenses and contribution constraints

| Component | VERIFIED primary license/policy | Practical implication |
|---|---|---|
| DXMT current | LGPL-2.1-or-later; `LICENSE.OLD` says only releases through v0.80 used MIT | Redistribute current source/modifications and license notices correctly; do not advertise current release as MIT |
| DXVK | zlib | Preserve license notice and mark altered source |
| MoltenVK | Apache-2.0; repository requires contributor CLA | Preserve notices/license; inspect dependency NOTICE files; do not treat CLA as source redistribution restriction |
| vkd3d-proton | LGPL-2.1-or-later on inspected device source plus LGPL license text | Corresponding-source and linking obligations apply; audit submodules separately |
| D3DMetal | Proprietary Apple terms, excluded from UTM wrapper | Exact downloaded-package license review required before redistribution; cannot be the FOSS core |

Sources: [DXMT LICENSE](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/LICENSE), [older-license boundary](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/LICENSE.OLD), [DXVK LICENSE](https://github.com/doitsujin/dxvk/blob/71ec7b5be6c517db39bcca4d38f38a63f6ddbc56/LICENSE), [MoltenVK LICENSE](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/LICENSE), [MoltenVK contribution policy](https://github.com/KhronosGroup/MoltenVK/blob/67b2682699d7903606b97a0392061d85d27d49e6/README.md#L445), [vkd3d file header](https://github.com/HansKristian-Work/vkd3d-proton/blob/2230755878b01993b4b82d0ac0c0624f3ab4d333/libs/vkd3d/device.c#L1).

**VERIFIED — DXMT also rejects contributions made or co-authored by AI/LLMs.** It allows AI-assisted research and sharing findings, but says not to create a PR. No upstream changes were submitted during this research. Human-authored upstream work must respect that policy. [CONTRIBUTING.md](https://github.com/3Shain/dxmt/blob/e94c312f5c054263acf261cfa109edf13e757587/CONTRIBUTING.md).

**INFERRED / legal review needed — Distribution practice.** Use separately replaceable runtime libraries and publish precise corresponding sources/build scripts. If statically incorporating LGPL components, provide the materials required to relink the covered library; merely publishing an application repository is not automatically sufficient. Audit LLVM, mingw, shader tooling, and every submodule license in the eventual shipped graph. Running against macOS's Metal framework is distinct from redistributing Apple's D3DMetal or SDK tools. This research is not a legal opinion.

## Smallest graphics validation after CPU proof

1. Build a tiny source-available x86-64 Win32 test that creates a window without D3D. Verify it renders, responds to input, resizes, and exits in the ARM64 Wine/FEX process.
2. Build the pinned DXMT ARM64EC PE DLLs and ARM64 unixlib against the exact Wine build; inspect their binary architectures before execution.
3. Run a source-available D3D11 clear/triangle sample at a deliberately low feature level, then test resize/present, CPU-write buffer upload, texture readback, query completion, and device teardown. Validate pixel results rather than merely a visible launch.
4. Record FEX/ARM64EC transition traces and native process architectures, GPU validation output, cold/warm cache behavior, allocations, and per-frame CPU/GPU timestamps. No numeric performance target is defensible until the same test runs across baseline backends.
5. Add selected ordinary desktop applications requiring D3D11, Direct2D/DirectWrite, or WPF only after identifying their actual API dependencies. Never infer those APIs work merely because a D3D11 triangle renders.

Acceptance: correct results with no x86_64 Darwin process or Rosetta participation, stable repeated resize/present and teardown, deterministic versioned overrides, and a reproducible build. Graphics support is an opt-in tested capability until this passes. These steps are **untested procedures**, not results.
