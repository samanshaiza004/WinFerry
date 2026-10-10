# Roadmap and real innovation

Date: 2026-10-10. Everything below is **PROPOSED / INFERRED**, not delivered runtime capability. Engineering priorities derive from the source evidence in [02](02-native-arm64-wine.md), [03](03-fex-hangover.md), [04](04-graphics.md) and alternatives in [05](05-alternatives.md). Acceptance counts are prospective criteria, not measured results or effort estimates.

## Five highest-priority tasks

1. Establish an independently obtainable and distributable Apple cross-architecture authorization, including expiry/renewal and unrelated recipient installation.
2. Publish a pinned clean build of native Wine that runs ARM64 builtins and survives all Darwin/Windows ABI boundaries.
3. Implement/reproduce the narrow FEX PE UnixLib Darwin integration with correct per-thread configuration and observable execution provenance.
4. Qualify JIT/code protection, SMC, atomics, threads, callbacks and mixed exceptions against reference behavior.
5. Establish a desktop workflow corpus and a deterministic, reversible compatibility manifest/recipe subsystem.

These are dependencies: product UI and accelerated graphics cannot unblock missing execution authority or correctness.

## Milestones and gates

| Milestone | Deliverable | Measurable acceptance | Stop or revise condition |
|---|---|---|---|
| 0: Authorization | Capability harness, exact signing/entitlement/profile policy, redistribution conditions | Actual4 KB process, legal low fixed mapping, x18 mode and TSO probe in permitted environment; release artifact runs on an unrelated stock Mac whose user has no developer enrollment; SIP/AMFI retained; profile renewal and update tested | Independent publisher cannot obtain distribution capability; don't substitute SIP bypass |
| 1: Native Wine A | Public pinned source/toolchain/build manifest, minimal patch queue, isolated signed bundle | Clean checkout builds twice; ARM64 cmd/notepad and API smoke work on M1 and a newer Apple Silicon model; actual process/native module architecture captured; no Intel helper fallback;100 fresh-prefix smoke runs pass | Missing source/integration; fragile old-SDK workaround is sole viable path; repeated ABI faults |
| 2: FEX B | PE emulator DLL and native adapter builds, registration manifest, guest smoke source and trace | Self-built x64 PE runs and exits0 on both machines; trace identifies FEX code and native API transitions;100 repeated runs, child process,8-thread TLS/atomic fixture pass; Linux rootfs/standalone FEX not required | Port requires broad Linux frontend transplantation or unavailable external patches |
| 3: Correctness and C | Reproducible fault/unwind/JIT corpus and Win32 GUI fixture |4 KB protect/guard/fixed mappings, callback/SEH/longjmp, thread suspension and creation, cross-thread JIT publish, VirtualProtect/SMC, sync and async I/O-to-code invalidation tests pass; UI input/resize/DPI/clipboard/file dialogs verified; no security-mode relaxation | Unresolved data races/deadlocks or only screenshot-level success. Do not infer correctness from100 runs alone |
| 4: Desktop technical preview | Ten source-available or lawfully testable desktop workflows, versioned recipes, diagnostics | At least8/10 nominated workflows install/launch/open-save/close correctly on both models; failures recorded publicly; MSI tested only where included; clean install/uninstall and rollback leave host test files unchanged; releases include source/license manifest | Insufficient practical coverage; narrow supported list instead of promising broader compatibility |
| 5: Optional DXMT | Exact Wine/macdrv/DXMT tuple, x64 D3D11 fixture | Native PE/unixlib architecture verified; pixel/readback/query/present/resize/teardown tests; cold/warm caches recorded; no proprietary graphics dependency | Feature gaps prevent nominated app workflows; keep desktop-only release |
| 6: External VM fallback study | Same corpus in existing user-owned UTM Windows ARM or proposed Linux VM | Publish incremental pass count, additional RAM/disk/start time, integration limitations and license/setup burden; add handoff only if actual user workflows benefit | Two-backend support burden exceeds demonstrated added value |

Milestones0–3 are the full-project investment gate. Milestone4's8/10 criterion applies to a **predeclared** small corpus, not cherry-picked applications after tests. The program must separately publish exclusions. No milestone claims universal support.

Milestone0 can begin with a platform-only harness; no Wine build is necessary to expose a capability denial. Software TSO fallback can be evaluated where legally available, but cannot replace missing page/layout authority. Use the local [probe record](experiments/README.md) as a starting diagnostic, not proof that this milestone is already complete.

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
