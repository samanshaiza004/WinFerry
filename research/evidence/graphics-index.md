# Graphics evidence provenance

Collected 2026-10-10 using read-only public GitHub commit API and raw source requests. No build or graphics execution was performed. Original line numbering is preserved in the downloaded text files. Source revisions are recorded in `graphics-*-revision.json`; hashes in `graphics-sha256.tsv`. Files are unmodified upstream source evidence, subject to the included upstream licenses; they are not WinFerry implementation code.

The provenance URL template is `https://raw.githubusercontent.com/<repository>/<sha>/<original_path>`. Snapshot filenames use `graphics-<key>-` followed by the original path with `/` replaced by `_`. Existing underscores in original filenames are preserved.

| Key | Repository | Revision | Original paths preserved |
|---|---|---|---|
| dxmt | 3Shain/dxmt | e94c312f5c054263acf261cfa109edf13e757587 | README.md; LICENSE; LICENSE.OLD; CONTRIBUTING.md; docs/DEVELOPMENT.md; meson.build; meson.options; build-arm64ec.txt; .github/workflows/ci.yml; src/d3d11/d3d11_device.cpp; src/d3d11/d3d11_swapchain.cpp; src/d3d11/d3d11_swapchain.hpp; src/d3d12/d3d12_swapchain.cpp; src/dxmt/dxmt_shader_cache.cpp; src/dxmt/dxmt_shader_cache.hpp; src/winemetal/meson.build; src/winemetal/unix/cache.c; src/winemetal/unix/install.sh; src/winemetal/unix/meson.build; src/winemetal/unix/winemetal_unix.c |
| dxvk | doitsujin/dxvk | 71ec7b5be6c517db39bcca4d38f38a63f6ddbc56 | README.md; LICENSE; meson.build; VP_DXVK_requirements.json; src/dxvk/dxvk_adapter.cpp |
| moltenvk | KhronosGroup/MoltenVK | 67b2682699d7903606b97a0392061d85d27d49e6 | README.md; LICENSE; Docs/MoltenVK_Runtime_UserGuide.md; MoltenVK/MoltenVK/GPUObjects/MVKDevice.mm; MoltenVK/MoltenVK/Layers/MVKExtensions.def |
| vkd3d | HansKristian-Work/vkd3d-proton | 2230755878b01993b4b82d0ac0c0624f3ab4d333 | README.md; COPYING; LICENSE; meson.build; libs/vkd3d/device.c |
| d3dmetal-native | utmapp/d3dmetal-native | d374b21668f94b7b7b059f152794fdb93e944b84 | README.md |

Non-pinned live sources (accessed 2026-10-10) are Apple's [Game Porting Toolkit product page](https://developer.apple.com/games/game-porting-toolkit/), [agreements page](https://developer.apple.com/support/terms/), and [MoltenVK issue 2158](https://github.com/KhronosGroup/MoltenVK/issues/2158). The report marks maintainer/wrapper runtime claims REPORTED and current Apple-package redistribution details UNKNOWN. No proprietary Apple framework or GPTK binary has been downloaded.

The shell network environment initially denied DNS resolution. Read-only public-source fetching subsequently succeeded under approved network access. Failed source-path lookups produced no fabricated source content. Public commits were selected using the cutoff `2026-10-10T23:59:59Z`; no post-cutoff change is intentionally cited.
