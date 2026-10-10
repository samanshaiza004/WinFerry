# Landscape source register and acquisition limits

Inspected through web tools **2026-10-10**. Source-line references below refer to raw text line numbers in retrieved primary sources; GitHub page lines include web navigation and are identified separately. `main`/`master` and documentation URLs are mutable observations, not archival source revisions. Exact dependency SHAs must be captured before a build; no SHAs were invented where acquisition failed.

| Source | Revision/date and pertinent location | Evidence classification |
|---|---|---|
| [CodeWeavers blog index](https://www.codeweavers.com/blog) | July31 2026 native ARM64 Preview announcement; article URI is [here](https://www.codeweavers.com/blog/mjohnson/2026/7/31/crossover-preview-the-right-to-bear-arm64-on-mac) | VERIFIED announcement; full article fetch 403; no runtime reproduced |
| [Wine-devel Brendan Shanks](https://list.winehq.org/hyperkitty/list/wine-devel%40list.winehq.org/thread/CKG5CEN2BE5VRXZ7O7NX4YUSBH3247WH/?sort=date) | Aug7 2026; ARM64 Wine plus FEX i386/x86_64 ARM64EC description | REPORTED implementation result, maintainer evidence |
| [CrossOver source](https://www.codeweavers.com/crossover/source) | Listing observed 26.3.0; exact Preview source not acquired in this subtask | VERIFIED stable FOSS publication; UNKNOWN exact Preview completeness |
| [CrossOver EULA](https://www.codeweavers.com/crossover/eula) | Current Appendix A and FOSS section | VERIFIED separate product/component licensing |
| [Wine LICENSE](https://raw.githubusercontent.com/wine-mirror/wine/master/LICENSE) | master observed; lines1–6; [COPYING.LIB](https://raw.githubusercontent.com/wine-mirror/wine/master/COPYING.LIB) sections2,4–6 | VERIFIED LGPL grant/text |
| [Hangover README](https://raw.githubusercontent.com/AndreRH/hangover/master/README.md) | master observed; lines8–35 execution/host/emulators, 53–74 emulator DLL selection, 87–93 DXVK | VERIFIED code-facing public integration instructions; not reproduced |
| [Hangover release](https://github.com/AndreRH/hangover/releases/tag/hangover-11.16) | hangover-11.16, displayed short SHA56e385b, Aug30; FEX2608/Box640.4.4/vararg thunks | VERIFIED published release metadata; not tested |
| [Box64 README](https://raw.githubusercontent.com/ptitSeb/box64/main/README.md) | main observed; lines12–15 Linux/native-library/dynarec and paper, 49–61 Box32/cache, 86–91 Wine | VERIFIED documented architecture, not benchmarks reproduced |
| [Box64 release](https://github.com/ptitSeb/box64/releases/tag/v0.4.4) | v0.4.4, displayed short SHA2f130fa, Aug2 | VERIFIED release metadata |
| [FEX LICENSE](https://raw.githubusercontent.com/FEX-Emu/FEX/main/LICENSE) | main observed; lines0–18 MIT | VERIFIED license |
| [FEX contribution policy](https://raw.githubusercontent.com/FEX-Emu/FEX/main/CONTRIBUTING.md) | main observed; single line | VERIFIED no AI code policy |
| [Proton README](https://raw.githubusercontent.com/ValveSoftware/Proton/proton_11.0/README.md) | proton_11.0 observed; lines3–5 Linux target,166–170 ARM64 build,204–208 licensing,256–308 reversible config | VERIFIED documented source/build capability, not Darwin runtime |
| [Proton tree](https://github.com/ValveSoftware/Proton) | proton_11.0 observed; displayed FEX submodule1cc4b93 and Winee60892c | Short submodule IDs only; not full parent revision capture |
| [UTM README](https://github.com/utmapp/UTM) | main observed; page lines262–276 backend/acceleration,299–309 license warnings | VERIFIED architecture/license |
| [UTM5.0.5](https://github.com/utmapp/UTM/releases/tag/v5.0.5) | beta, short SHAb6f7475, Sep2; Neptune/experimental 3D and optional D3DMetal | REPORTED new graphics capability |
| [UTM5.0.6](https://github.com/utmapp/UTM/releases/tag/v5.0.6) | beta, full SHA968fef31ee3299224feaf4de1e40e1e5f46369c1 ([commit](https://github.com/utmapp/UTM/commit/968fef31ee3299224feaf4de1e40e1e5f46369c1)), Sep24 2026; experimental Windows 3D driver update still unreleased notice | VERIFIED notice; compatibility REPORTED |
| [UTM Windows guide](https://docs.getutm.app/guides/windows/) | observed current; page lines113 license,134 architecture,144 TPM,154–155 x86 multicore correctness | VERIFIED instructions/warnings; no VM experiment |
| [UTM guest tools](https://docs.getutm.app/guest-support/windows/) | page lines93–102 architectures/install;125–129 WebDAV | VERIFIED guest integration documentation |
| [Microsoft ARM FAQ](https://learn.microsoft.com/en-us/windows/arm/faq) | observed current, driver architecture section | VERIFIED emulation excludes drivers |
| [Microsoft emulation](https://learn.microsoft.com/en-ca/windows/arm/apps-on-arm-x86-emulation) | last updated2025-11-07; Prism/user-mode/ARM64X/cache | VERIFIED documentation; no comparative speed measurements |
| [Microsoft Mac options](https://support.microsoft.com/en-us/windows/experience/platform-variants/options-for-using-windows-11-with-mac-computers-with-apple-m1-m2-and-m3-chips) | current official page retains Parallels18/19/20 examples | VERIFIED documented authorization and instance licensing; do not imply complete current-version compatibility chart |
| [Parallels product](https://www.parallels.com/products/desktop/) | page lines193–227 seamless windows/D3D11; licensing commercial | REPORTED product features, not local validation |
| [Whisky README](https://raw.githubusercontent.com/Whisky-App/Whisky/main/README.md) | main observed; lines8–10 maintenance,26 architecture/history,31–34 requirements,47–56 dependencies | VERIFIED maintenance and configuration |
| [Whisky archive](https://github.com/Whisky-App/Whisky) | banner May11 2025 archive | VERIFIED archived repository; forks not evaluated |
| [Porting Kit](https://www.portingkit.com/about), [terms](https://www.portingkit.com/terms) | fetched only navigation/Angular-style placeholder page | UNKNOWN current complete license/implementation; not treated as FOSS source proof |
| [osxEQL STATUS](https://raw.githubusercontent.com/sowoky/osxEQL/main/docs/STATUS.md) | main observed; heading July12, later section August; lines35–57 Intel Wine build,74–84 dlopen closure correction | REPORTED render/packaging; VERIFIED instructions show x86 architecture; not native proof |
| [Porthole](https://github.com/Bockit/porthole) | main observed; README explicitly x86_64/Rosetta | VERIFIED stated architecture only |
| [Blink](https://github.com/jart/blink) | master observed; page lines214–229 POSIX/macOS hosts; ISC license | VERIFIED documented supported scope; Windows integration not reproduced |
| [Apple Developer ID](https://developer.apple.com/developer-id/) | page lines139 Account Holder requirement,144 hardened runtime,153–161 notarization | VERIFIED publisher distribution distinction |
| [Apple accounts](https://developer.apple.com/help/account/basics/about-your-developer-account) | page lines238–257 free versus membership | VERIFIED account distinction; cross-architecture authorization remains separate |
| [Apple JIT](https://developer.apple.com/documentation/apple-silicon/porting-just-in-time-compilers-to-apple-silicon) | current observed; MAP_JIT/hardened-runtime and write protection | VERIFIED generic JIT requirements |
| [Apple GPTK](https://developer.apple.com/games/game-porting-toolkit) | GPTK4 current page observed | VERIFIED tooling description; full framework license not acquired |
| [Wine security statement](https://www.winehq.org/pipermail/wine-devel/2002-October/009804.html) | historical Oct2002 developer discussion | VERIFIED longstanding sandbox distinction; not a present comprehensive vulnerability audit |
| [DXMT license](https://raw.githubusercontent.com/3Shain/dxmt/main/LICENSE) and [policy](https://raw.githubusercontent.com/3Shain/dxmt/main/CONTRIBUTING.md) | current main observed; license lines2–5 LGPL2.1+; policy lines20–24 AI restriction/research permission | VERIFIED licensing and contribution policy |

Graphics license links for DXVK, MoltenVK and VKD3D-Proton, plus REA/Ghidra, appear directly in [06](../06-licensing-security.md); each raw license was inspected. This register does not assert immutable branch provenance for them.

## Acquisition failures

A read-only Python attempt to retrieve GitHub API repository/commit metadata failed with DNS resolution errors in the restricted shell. `landscape-revisions.json` preserves those errors, not successful revision metadata. Research then used readable primary web sources, raw source text and release tags. No source checkout, license archive download, VM launch or benchmark was performed by this subtask. Porting Kit rendered content was unavailable; the specific CodeWeavers blog article was403; Microsoft `/apps-on-arm` was404 and corrected to `/faq` plus `/apps-on-arm-x86-emulation`; GNU online LGPL URL timed out, so Wine's bundled exact text was used.

Additional Porting Kit discovery: [publisher release repository](https://github.com/vitor251093/porting-kit-releases) contains only a README in its source tree; [development releases](https://github.com/vitor251093/porting-kit-releases-dev/releases/) show binary distribution. This reinforces UNKNOWN complete source/license; it does not prove no source exists elsewhere. No release date without a displayed year was used to infer current-cutoff status.

[Apple Rosetta policy](https://developer.apple.com/news/?id=w5ngl9k2), Sep1 2026, page lines140–143: macOS26.4+ notices; macOS27 last general support; older-game exception. VERIFIED public policy, not inferred support for arbitrary Wine runtimes.
