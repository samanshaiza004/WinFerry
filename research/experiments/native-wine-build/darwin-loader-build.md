# Darwin loader build-only experiment

Date: 2026-10-10. Status: **PATCH AND LINK-LAYOUT BUILD PASS; RUNTIME NOT RUN.**

The bounded loader patch compiles against the pinned public Wine source when
combined with the reported low-address linker layout. The build was performed
from a disposable copy of Wine commit
[`a15ee2ccf20e2fc9f470badd916855801933d31f`](https://github.com/wine-mirror/wine/tree/a15ee2ccf20e2fc9f470badd916855801933d31f)
on an Apple M1 MacBook Air (`MacBookAir10,1`), macOS 27.0 build `26A428`, Xcode
27.0 build `27A266a`, and SDK 27.0. Inputs were llvm-mingw 20261006 (LLVM
23.1.3), Bison 3.8.2, and Homebrew pkgconf/pkg-config 3.0.8. The host and tool
versions are captured in [`host-environment.txt`](logs-darwin-loader/final-success/host-environment.txt).

The script applied the 4 KB re-exec source patch to its temporary source copy,
configured Wine with tests and unrelated host integrations disabled, then
changed exactly one generated loader link command to:

```text
-Wl,-x86_64_layout_emulation,-no_fixup_chains,-no_huge,-image_base,0x170000000,-pagezero_size,0x170000000,-segalign,0x1000,-sectcreate,__TEXT,__info_plist,loader/wine_info.plist
```

The generated `loader/wine` is a native ARM64 Mach-O. `otool -l` confirms
`__PAGEZERO` at `vmaddr 0` with `vmsize 0x170000000`, and `__TEXT` at
`vmaddr 0x170000000`. The linker emitted an ad-hoc signature (`TeamIdentifier`
not set); `codesign --verify --strict` passed. The executable SHA-256 is
`4fdf9964898a091b13a1788fd55eeeb6bc0f68d483cff1bb3d26773d5e8dde8a`.

This is build evidence only. The loader was not launched, the requested 4 KB
process was not attempted, authorization was not tested, and x18, signals,
exception handling, FEX, and Windows applications were not exercised. The
signature is not Developer ID signing or a provisioning profile. No claim is
made that an ordinary user can install or run this binary.

Reproduce with the command in
[`build-darwin-loader-only.sh`](build-darwin-loader-only.sh), using the pinned
source, toolchain, and Bison roots documented in the parent [build record](README.md).
The recipe also records configure, compiler, linker, load-command, and signature
logs, plus machine-readable output from the dedicated artifact verifier, under [`logs-darwin-loader/final-success/`](logs-darwin-loader/final-success/).
The static patch contract passes with:

```sh
python3 research/experiments/native-wine-build/test-darwin-loader-contract.py
```

## Troubleshooting evidence

The first configure attempt stopped because this minimal loader-only invocation
had not disabled unrelated FreeType discovery; the recipe now uses
`--without-freetype`. A second attempt compiled and linked the patched loader,
but inspection showed that a make-time variable did not override the flags
Wine had expanded into its generated Makefile. The final recipe now replaces
only the unique inline loader rule and checks the resulting Mach-O addresses.
One intermediate configure-only run ended before linking while the recipe was
being updated; the clean final run exercised the complete build and verifier.
Logs for the first two troubleshooting attempts are preserved under the two
`attempt-*` directories. The interrupted configure-only run is documented but
is not counted as a build or layout pass.
