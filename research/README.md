# WinFerry runtime feasibility research

**Decision: CONDITIONAL GO for a bounded native Wine/FEX prototype; no full-product commitment yet.** Assessment cutoff: **October10,2026**. The best foundation is native ARM64 Wine with its ARM64EC PE architecture and FEX's Windows PE frontend, then qualified DXMT. Independent stock-Mac distribution authorization and runtime memory/ABI correctness are named gates. [Final assessment](07-feasibility.md), [architecture decision](08-architecture-decision.md), [roadmap](09-roadmap.md).

## Reading order

1. [Native ARM64 Wine and Apple's2026 platform changes](02-native-arm64-wine.md)
2. [FEX/Hangover source and Darwin porting assessment](03-fex-hangover.md)
3. [Comparative landscape](01-landscape.md)
4. [Graphics](04-graphics.md), [alternatives](05-alternatives.md), [licensing/security](06-licensing-security.md)
5. [Feasibility](07-feasibility.md), [ADR](08-architecture-decision.md), [roadmap/innovation](09-roadmap.md)

## Evidence vocabulary

- **VERIFIED:** directly inspected source, official documentation or local experiment supports the precise claim. Source verification does not imply a build passed or an application worked.
- **REPORTED:** credible primary developer/vendor execution observation, not independently reproduced here.
- **INFERRED:** engineering conclusion from linked evidence; includes proposed architecture and acceptance criteria.
- **UNKNOWN:** evidence insufficient, inaccessible or contradictory. Untested procedures/results explicitly say **UNTESTED**.

Local work includes native platform capability probes, two clean builds of pinned native Wine components, and the build-only Darwin ARM64 loader/layout patch: [capability experiment](experiments/README.md), [build record](experiments/native-wine-build/README.md), [build comparison](experiments/native-wine-build/build-comparison.md), and [loader/layout result](experiments/native-wine-build/darwin-loader-build.md). A separate ARM64 Linux Hangover run passed tiny ARM64 and x86-64 Windows console tests; five later x64 trials passed in five fresh Wine prefixes after two assertions in one earlier prefix. See the [reproducible experiment](experiments/linux-arm64-reference/README.md). **No native macOS Wine process or graphics application has been executed.** The M1/macOS 27 SDK exposes the required API declarations; four unprovisioned signature/layout variants failed to launch a 4 KB child with error 88. Gate 0A (authorized development execution) and Gate 0B (stock-Mac redistribution) remain untested. Apple's general provisioning process is documented, but availability of this exact capability to an independent publisher remains unknown; see [authorization evidence](evidence/apple-authorization-process.md). The source-level forward-port assessment is [here](evidence/native-wine-minimal-patch-queue.md). No performance claims are measured.

Public source snapshots/metadata/hashes and local SDK references are in [evidence index](evidence/README.md). [References](references.md) preserves links; chapter citations carry source line/revision details. Some web pages are mutable, private integration is unavailable, and Wine GitLab blocked direct MR inspection. These limitations are stated rather than silently filled in. Source inspection and research were parallelized; no upstream patches, messages, credential changes or security changes were made.

The2026 CrossOver preview and public developer reports substantiate the architecture as a real reported execution path. They do **not** settle whether an unrelated ordinary recipient can install an independently built runtime without enrollment. Maintainer paid signing costs and recipient enrollment are separate questions. D3DMetal is outside the mandatory open-source path, and an integrated Windows VM is deferred.
