# Experimental native Wine for Apple Silicon

This experimental development branch contains Wine itself and experimental Darwin ARM64 changes. It does not contain the Aster launcher, FEX, DXMT, games, Steam installations, Wine prefixes, Apple SDKs, signing identities, or provisioning profiles.

Base: Wine commit `2550c238151a00e43908561f32b6e131603ec6f7` (11.17 development tree). The original Wine README and LGPL license remain authoritative for the Wine project. This branch is an independent experiment, not an official Wine or CodeWeavers release.

## What works on the development machine

Tested on an Apple M5 Max with macOS 27 beta and Xcode 27 beta:

- Native ARM64 Wine host processes and ARM64 Windows smoke tests.
- x86-64 guest smoke, child processes, eight-thread integer stress and self-modifying code, using external FEX ARM64EC integration.
- 32-bit Windows smoke and window/message tests with external FEX WoW64 integration.
- D3D11 compute, GPU readback and visible presentation using external ARM64EC DXMT.
- Cities: Skylines II loaded a saved city, with working controls, pause menu, Traffic and RoadBuilder mods. The Metal FPS/GPU-time HUD was visible.
- October 2026: Cities: Skylines II, Schedule I and Surviving Mars: Relaunched launch from the Steam client through an external compatibility-tool integration (not in this repository), with the Steam API working through an external native client bridge. The in-process synchronization backend was active in Cities: Skylines II (all sampled waits in the in-process path, none in the server wait). explorer.exe and helper processes no longer add Dock icons.

These are observations on one development machine, not a broad compatibility guarantee. The complete Wine + FEX + DXMT setup has not been reproduced from a clean checkout by another developer. This repository does not claim a speedup: a preliminary matched-save comparison was about 57.5 FPS / 14.5 ms GPU on the native experimental stack versus 75.3 FPS / 11.2 ms GPU on the original Rosetta/GPTK stack. Camera equivalence was confirmed by the tester, but runs were sequential and not a controlled repeated benchmark.

## Changes in this branch

1. Darwin ARM64 loader bootstrap for the restricted 4 KB / low-address compatibility environment.
2. Opt-in diagnostic write/execute memory fault handling.
3. Experimental custom-x18 handling around native/Windows transitions and signals.
4. Narrow Wine macdrv Metal surface creation/release interface for an external DXMT adapter.
5. Opt-in skipping of occupied host mappings during address-space searches.
6. Opt-in Steam CEF single-process command-line workaround.
7. Diagnostic executable-heap commit handling.
8. Opt-in MAP_JIT backing for committed ARM64EC code, exempt from the diagnostic W^X path.
9. Opt-in resolution of the Steam client DLL to a builtin `lsteamclient`.
10. FAudio: keep the sample timeline current when resampling is bypassed at unity rate (fixes a hang on a later rate change).
11. ARM64 user-mode callbacks whose arguments would overflow the thread stack are rejected instead of corrupting it.
12. winemac: apply the executable's icon when it loads after the process became a foreground app.
13. winemac: keep a window's Metal view alive until its last swap chain releases it (fixes a crash with the Metal HUD on while a swap chain is recreated).
14. loader: the 4 KB page-size re-exec is bounded to one attempt and exits with a message when the entitlement is missing.
15. An in-process synchronization backend for macOS behind upstream's in-process sync interface; see [SYNC.md](SYNC.md).
16. winemac: only windows the user can activate make the process a Dock application; explorer's systray window is a tool window.

Each change is a separate commit after the upstream base. Existing `ASTER_*` and `STRATUM_*` environment variable names are retained to match the tested integration; they are switches in Wine, not a dependency on a launcher.

## Build and integration status

See [BUILD.md](BUILD.md) for component build prerequisites and the remaining integration steps. This is a source development branch, not a ready-to-install Wine.app release. There are no binary release assets yet.

Do not use an existing valuable Wine prefix for experiments. In particular, do not symlink mutable PE build outputs into a prefix: prefix maintenance can modify or remove them. Use independent copies.

## Runtime switches

| Variable | Purpose |
| --- | --- |
| `ASTER_WX_PROBE=1` | Enables the diagnostic RW/RX transition and executable-commit paths. |
| `ASTER_CUSTOM_X18=1` | Enables the experimental macOS custom-x18 integration. |
| `ASTER_SKIP_HOST_REGIONS=1` | Enables the measured host address-region collision optimization. |
| `ASTER_STEAM_CEF_SINGLE_PROCESS=1` | Adds single-process and GPU-disable flags only to Steam's browser helper. Opt-in; reduces browser process isolation. |
| `ASTER_FEX_MAP_JIT=1` | Backs committed ARM64EC code allocations with MAP_JIT mappings. |
| `STRATUM_NATIVE_STEAM=1` | Resolves `steamclient.dll`/`steamclient64.dll` to a builtin `lsteamclient.dll` supplied by the integration. |
| `STRATUM_SYNC=1` (wineserver) | Enables the in-process synchronization backend; needs macOS 14.4 or later, otherwise server synchronization is kept. |

The tested FEX integration additionally requires enabling hardware TSO in **every emulation thread**. macOS threads did not inherit the initially enabled mode. That correction belongs to FEX, not this Wine tree; see BUILD.md. Do not treat an unpatched FEX build as equivalent to the tested configuration.

## Work needed

- Replace the process-wide diagnostic W^X mechanism with robust JIT/code-cache management and test concurrent execution/writes.
- Audit custom-x18 preservation for exceptions, signals, APCs, callbacks and thread suspension.
- Produce an independent packaging/provisioning workflow with caller-supplied credentials and profiles.
- Document and publish the external FEX and DXMT integration changes separately.
- Expand tests across Apple Silicon models and macOS versions.
- Profile tessellation and synchronization costs in the external renderer; keep CPU translation and GPU performance claims separate. A profile of Cities: Skylines II on the external renderer found the frame GPU-bound, dominated by the renderer's tessellation emulation and the game's post-processing, not by Wine or synchronization.
- Synchronization backend: per-object locks or lock-free fast paths instead of the single region lock; fixtures for a thread terminated mid-wait, a handle closed under a waiting thread and the server-side fallback.
- The loader bundle's Info.plist needs `LSUIElement`, as upstream's `loader/wine_info.plist.in` has; see BUILD.md.

For contributions, see [CONTRIBUTING.md](CONTRIBUTING.md). Wine's licensing remains in [COPYING.LIB](../../COPYING.LIB).
