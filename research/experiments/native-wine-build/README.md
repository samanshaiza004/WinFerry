# Pinned native Wine build experiment

Status: **BUILD PASS; runtime not run.** The full configured build completed. No Wine process or Windows application has been launched by this experiment.

## Inputs

| Input | Pin | Acquisition / verification |
|---|---|---|
| Wine source | `wine-mirror/wine` commit `a15ee2ccf20e2fc9f470badd916855801933d31f` (2026-10-09) | [Commit](https://github.com/wine-mirror/wine/commit/a15ee2ccf20e2fc9f470badd916855801933d31f); archive SHA-256: `f87b071f5f19f4cc5b6a51d3000ae03ee791325d5873ba221da191fd5b933a41` |
| Windows cross compiler | `llvm-mingw 20261006`, LLVM 23.1.3 | [Release](https://github.com/mstorsjo/llvm-mingw/releases/tag/20261006); macOS universal archive SHA-256: `a7a19b11048e89372637d26279cdb7c430ed3cf8c1e224310421312bf986ebf6` |
| Parser generator | GNU Bison 3.8.2 | [GNU source archive](https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz); SHA-256: `9bba0214ccf7f1079c5d59210045227bcf619519840ebfa80cd3849cff5a5bf2`; built into the temporary experiment directory because `/usr/bin/bison` is 2.3 |

All three archive hashes above are locally calculated hashes of the exact files used; they are recorded for repeatability, not represented as publisher-signed checksums. The Wine commit identity was cross-checked against the upstream commit metadata. The cross compiler reports LLVM 23.1.3 and target triples `aarch64-w64-windows-gnu` and `arm64ec-w64-windows-gnu`.

## Host and scope

Host: Apple M1 MacBook Air (`MacBookAir10,1`), macOS 27.0 build `26A428`, Xcode 27.0 build `27A266a`, ARM64. The build runs in `/private/tmp/winferry-native-wine-build`; it does not install into the system or change signing, provisioning, SIP, or other security settings. Configure requests native ARM64 macOS host code and ARM64/ARM64EC Windows PE modules. `arm64ec` causes Wine's configure logic to also probe x86-64 PE tools. Optional X11, CUPS, PulseAudio, ALSA, GStreamer, Vulkan and regression-test builds are disabled to reduce unrelated host dependencies. Homebrew's existing `pkg-config` is selected explicitly so configure can find the already-installed FreeType headers (no package was installed); GnuTLS is absent and is not added by this experiment.

This is a **public upstream baseline**. It must not be confused with the CrossOver Preview or the separate experimental Wine branch: the source audit records the old loader layout and exact-symbol checks in [native-wine-upstream-a15ee2-audit.md](../../evidence/native-wine-upstream-a15ee2-audit.md). A component build can establish compiler and source buildability, not process authorization or runtime compatibility.

## Reproduction

Fetch the three pinned archives, verify their SHA-256 values, and build GNU Bison 3.8.2 under a user-writable temporary prefix:

```sh
research/experiments/native-wine-build/fetch-inputs.sh /path/to/downloads
research/experiments/native-wine-build/build-bison.sh \
  /path/to/downloads/bison-3.8.2.tar.xz /path/to/tools/bison
mkdir -p /path/to/source /path/to/toolchain
tar -xzf /path/to/downloads/wine-a15ee2ccf20e2fc9f470badd916855801933d31f.tar.gz -C /path/to/source
tar -xJf /path/to/downloads/llvm-mingw-20261006-ucrt-macos-universal.tar.xz -C /path/to/toolchain

research/experiments/native-wine-build/build.sh \
  /path/to/source/wine-a15ee2ccf20e2fc9f470badd916855801933d31f \
  /path/to/toolchain/llvm-mingw-20261006-ucrt-macos-universal \
  /path/to/tools/bison/bin \
  /path/to/out-of-tree-build
```

The script does not run `make install`. Use `JOBS=2` by default on the 8 GB host; increase only after checking available memory. Toolchain and build directories stay outside the repository. The script writes configure/build logs under `research/experiments/native-wine-build/logs` unless `WINFERRY_NATIVE_BUILD_LOG_DIR` is set. The captured logs must not be treated as runtime evidence.

## Result record

The initial configure attempt with stock Bison 2.3 stopped at Wine's explicit minimum-version check. After building Bison 3.8.2 in a temporary prefix and selecting the host's installed `pkg-config`, configure and the full `make -j2` build both passed. The build produced ARM64 Mach-O `loader/wine`, `tools/wine/wine`, and `server/wineserver`, plus PE outputs identified by LLVM's reader as `COFF-ARM64X` (`IMAGE_FILE_MACHINE_ARM64X`, `0xA64E`). Their SHA-256 values and paths under the temporary build tree are recorded in [manifest.json](manifest.json); the concise [build result](logs/build-result.txt) and full build logs are retained. This is one successful build; a clean second build and byte-for-byte comparison remain pending. Runtime milestones A/B/C remain **UNTESTED**: no binary was launched and the pinned upstream source lacks the required 4 KB spawn, custom x18, and new loader-layout implementation.
