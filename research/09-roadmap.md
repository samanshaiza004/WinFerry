# Roadmap and real innovation

Date: 2026-10-10. Everything below is **PROPOSED / INFERRED**, not delivered runtime capability. Engineering priorities derive from the source evidence in [02](02-native-arm64-wine.md), [03](03-fex-hangover.md), [04](04-graphics.md) and alternatives in [05](05-alternatives.md). Acceptance counts are prospective criteria, not measured results or effort estimates.

## Five highest-priority tasks

1. Resolve Gate 0A through Apple's documented developer capability/provisioning process. Keep the already characterized unprovisioned baseline closed; do not guess entitlement strings or relax system protections.
2. Build pinned public native ARM64 Wine components in parallel with authorization work. The source/toolchain are now pinned and acquired; the build result is recorded separately from runtime feasibility.
3. Resolve Gate 0B as a separate publisher/distribution question: can an independently signed runtime install on an unrelated stock Mac without recipient enrollment or security changes?
4. Start FEX/ARM64EC runtime integration only after a properly authorized 4 KB process can launch; then prove thread setup and execution provenance before adding application support.
5. Qualify ABI, memory, synchronization and then a small desktop workflow corpus. Graphics, broad compatibility recipes and consumer UI follow a working runtime.

These are dependencies: product UI and accelerated graphics cannot unblock missing execution authority or correctness.

## Milestones and gates

| Gate / milestone | Deliverable | Measurable acceptance | Stop or revise condition |
|---|---|---|---|
| 0A: Development authorization | Tiny native capability harness using Apple's documented APIs | On a development Mac with an Apple-issued entitlement/profile: authorized 4 KB child runs and reports 4096-byte pages; valid low-address layout is mapped; x18 entry/exit behavior and per-thread TSO semantics are recorded; SIP/AMFI remain enabled | Required features fail under the granted profile or require system-protection changes |
| 1: Native Wine build (parallel with 0A/0B) | Pinned public source/toolchain/build manifest and minimal patch queue | Clean checkout builds components twice with native ARM64 host binaries and matching Windows PE targets; hashes and commands match; build-only work makes no claim that Wine runs | Missing build inputs or unmaintainable private changes; record this separately from an authorization denial |
| 0B: Redistribution authorization (parallel with the component build) | Release-signed runtime and independent install procedure | On an unrelated stock Mac: recipient has no developer enrollment or registered UDID, installs and runs the signed environment; SIP/AMFI remain enabled; profile/signature renewal and update path are documented | Independent publisher cannot obtain the needed capability or release installs require recipient enrollment/machine registration |
| 2: Native Wine A runtime | Authorized signed bundle, isolated prefix and API fixture | After 0A, clean build runs ARM64 `cmd`/Notepad and API smoke on M1 and newer Apple Silicon; architecture trace rules out Intel host fallback; 100 fresh-prefix smoke runs pass | Repeated ABI faults, or a legacy SDK workaround is the sole runtime path |
| 3: FEX B | PE emulator DLL and native adapter builds, registration manifest, guest smoke source and trace | Self-built x64 PE runs and exits 0 on both machines; trace identifies FEX code and native API transitions; 100 repeated runs, a child process, and an 8-thread TLS/atomic fixture pass; Linux rootfs/standalone FEX not required | Port requires broad Linux frontend transplantation or unavailable external patches |
| 4: Correctness and C | Reproducible fault/unwind/JIT corpus and Win32 GUI fixture | 4 KB protect/guard/fixed mappings, callback/SEH/longjmp, thread suspension and creation, cross-thread JIT publish, VirtualProtect/SMC, sync and async I/O-to-code invalidation tests pass; UI input/resize/DPI/clipboard/file dialogs verified; no security-mode relaxation | Unresolved data races/deadlocks or only screenshot-level success. Do not infer correctness from 100 runs alone |
| 5: Desktop technical preview | Ten source-available or lawfully testable desktop workflows, versioned recipes, diagnostics | At least 8 of 10 nominated workflows install/launch/open-save/close correctly on both models; failures recorded publicly; MSI tested only where included; clean install/uninstall and rollback leave host test files unchanged; releases include source/license manifest | Insufficient practical coverage; narrow supported list instead of promising broader compatibility |
| 6: Optional DXMT | Exact Wine/macdrv/DXMT tuple, x64 D3D11 fixture | Native PE/unixlib architecture verified; pixel/readback/query/present/resize/teardown tests; cold/warm caches recorded; no proprietary graphics dependency | Feature gaps prevent nominated app workflows; keep desktop-only release |
| 7: External VM fallback study | Same corpus in existing user-owned UTM Windows ARM or proposed Linux VM | Publish incremental pass count, additional RAM/disk/start time, integration limitations and license/setup burden; add handoff only if actual user workflows benefit | Two-backend support burden exceeds demonstrated added value |

Gates 0A and 0B are independent: passing 0A proves that authorized development execution is technically possible, while 0B establishes that ordinary recipients can use a distributed build. Neither implies the other. Native Wine component builds proceed in parallel and do not substitute for running Wine after 0A. The full-product investment gate is completion of 0A and 0B plus milestones 1–4. Milestone 5's 8-of-10 criterion applies to a **predeclared** small corpus, not cherry-picked applications after testing. Publish the exclusions separately. No milestone claims universal support.

Gate 0A can begin with a platform-only harness; no Wine build is necessary to expose a capability denial. The harness should compare identical source compiled with ordinary and low-address linker layouts, capture linker/code-signature and entitlement state, and record the child-process result plus relevant diagnostics. Keep each variable explicit; do not label error 88 as an entitlement denial without corroborating evidence. Software TSO fallback can be evaluated where legally available, but cannot replace missing page/layout authority. Use the local [probe record](experiments/README.md) as a starting diagnostic, not proof that either gate is complete.

## Test and benchmark discipline

**Proposed measurements:** compare identical application versions/workflows and data under native stack, an existing free Wine/Rosetta baseline where available, and UTM only where appropriate. Record hardware, OS, patches, graphics mode, RAM pressure, cache state and confidence intervals over repeated runs. Separate cold installation, launch-to-interactive, warm launch, CPU task, UI input latency, peak resident footprint/guest RAM, battery/energy and GPU workload. Record failures as failures, not zero-time successes. Choose tolerable regression thresholds for the predeclared corpus before testing; no current speed target or claimed advantage is justified by this investigation.

Correctness fixtures should compare API results and fault/exception behavior against a licensed Windows reference, not mirror the implementation. Reuse upstream Wine/FEX tests. Workload testing covers multilingual text/fonts, input methods, clipboard formats, DPI, accessibility, shell dialogs, registry/COM, file locks and child installers. Kernel drivers and anti-cheat require a different compatibility boundary and are outside this preview.

## Ranked contributions

These qualitative rankings are engineering judgments, not scored research results. Existing bottles/recipes, test suites and catalogs in [landscape](01-landscape.md) mean most product ideas have precedent. The original contribution is their reproducible integration and open evidence, not claiming to invent them.

| Rank | Contribution | User value | Novelty | Difficulty / dependency |
|---|---|---|---|---|
| 1 | Signed, reproducible native Wine/FEX integration manifest and capability diagnostics | Essential: makes installation possible and failures understandable | Runtime/platform integration is substantive; underlying translator/API design already exists | High; Apple authorization plus Wine/FEX correctness |
| 2 | Versioned compatibility evidence and replayable desktop regression fixtures | High: prevents silent upgrades from breaking working apps | Moderate integration contribution; testing/catalogs already exist | Medium; needs working runtime but fixtures/manifests can be built first |
| 3 | Reversible per-app environments and declarative recipes | High: predictable installation and rollback | Low conceptual novelty; good cross-project standardization opportunity | Medium; content-addressed versions, changes journal, migration tests |
| 4 | Actionable failure diagnostics with provenance | High: distinguish missing DLL, entitlement, architecture, API and graphics failures | Moderate reusable classifier/evidence schema | Medium; deterministic log/error mapping, privacy filtering; never confidently classify an unknown crash |
| 5 | Bounded executable/dependency preflight and deterministic backend selector | High: early unsupported-driver/architecture warnings and fewer manual choices | Low/moderate; parsers and recipes exist | Medium; static imports are incomplete for delay-load/downloaded/packed code; requires dynamic evidence |
| 6 | macOS desktop integration | High for ordinary users: coherent icons, windows, document access and lifecycle | Low conceptual novelty; Wine/CrossOver already integrate | Medium/high; working macdrv baseline, accessibility/DPI/IME and safe file grants |
| 7 | Narrow public Darwin FEX host-service seam and conformance tests | Foundational ecosystem value | Meaningful port engineering, not a new translator | High correctness; human-authored upstream work under FEX policy |
| 8 | Explicit VM handoff with evidence-based reason | Medium for unsupported apps | Low: existing VM tools | Medium/high; needs user-owned guest and state contract; postpone |
| 9 | New fast synchronization or D3D12 implementation | Potential selective benefit | Runtime engineering, but already active upstream | Very high; defer until profiling identifies actual blockers |

## Small reusable subsystem worth building

A **runtime manifest and evidence format** can serve Wine packaging, Hangover, UTM handoff and testing without owning a new emulator. A record should identify executable hash/version and PE architecture; imported/delay-loaded dependencies; tested runtime tuple; host OS/hardware capability; permissions; installation steps with checksums; before/after environment changes; workflow test source/results; diagnostic artifacts with redaction; and provenance/status/date. License recipe data explicitly and exclude proprietary redistributables/secrets.

A selector reads this record and host capabilities, verifies the recipe inputs, chooses one qualified path and explains the evidence. On an unknown binary it cannot prove compatibility from imports alone. It can detect PE architecture, reject required kernel drivers where identified, use a conservative default, and collect permissioned test evidence. If a downloaded plugin changes the dependency graph, invalidate the previous conclusion. This deterministic limitation is a reason to be honest, not a reason to add an AI dependency.

Recipes should describe changes declaratively and journal each mutation. Install into a disposable prefix; commit only when checks pass. Rollback must restore prefix state and report external side effects it cannot undo. Native/VM backends never share a mutable registry or prefix; only explicit app-specific document/state transfer is permitted.

## Sustainability boundary

Keep upstream Wine and FEX releases as the base. Track patch count and affected modules each release, assign human maintainers to the Darwin seam, and require build/conformance results before upgrades. FEX and DXMT forbid AI-authored upstream code; this report is research, not an authorization to submit generated port patches. [Contribution constraints](06-licensing-security.md).

The first substantial expenditure should buy proof of authorization and reproducibility. Interface work can follow that proof. If those gates fail, publish the evidence, test corpus and manifest subsystem; do not conceal a Rosetta fallback inside a product advertised as Rosetta-free.
