# Second clean build comparison

Date: 2026-10-10. **VERIFIED:** Two complete clean out-of-tree builds of Wine commit `a15ee2ccf20e2fc9f470badd916855801933d31f` completed on the same M1/macOS/Xcode host with identical pinned compiler, Bison, pkg-config and FreeType inputs. Both used `make -j2`, but distinct output roots:

- First: `/private/tmp/winferry-native-wine-build/build-upstream-a15ee2c`
- Second: `/private/tmp/winferry-native-wine-build/build-upstream-a15ee2c-second`

The full command logs are in [`logs/`](logs/) and [`logs-second/`](logs-second/). The machine-readable section report is [`compare-second-build.json`](compare-second-build.json); the disassembly normalization report is [`compare-macho-disassembly.json`](compare-macho-disassembly.json). The scripts are [`compare-build-sections.py`](compare-build-sections.py) and [`compare-macho-disassembly.py`](compare-macho-disassembly.py).

## Result

**Build reproducibility: PARTIAL PASS.** Both builds pass configure and compilation/linking, and each produces the expected native ARM64 Mach-O tools and ARM64X Wine PE modules. All five artifacts have matching formats. Raw SHA-256 hashes differ for all five; byte-for-byte reproducibility therefore does not pass.

The differences have been localized:

- The Mach-O `loader/wine` sections, executable code and unwind metadata match. Its `LC_UUID` differs between links, explaining its differing whole-file hash.
- `tools/wine/wine` and `server/wineserver` contain two output-root-specific absolute install strings in `__cstring`. Those strings have different lengths in the two output roots, so references to later string literals have different encoded immediates. `otool -tvV` disassembly for all three Mach-O tools is identical after normalizing only the immediate on lines explicitly annotated as a literal-pool string reference. All other disassembly lines are retained and compared. This establishes matching instruction sequences under that narrow normalization; the raw code-section hashes still differ for the two helpers.
- The ARM64 Windows `.text` sections and ARM64X metadata sections (`.a64xrm`, `.eh_fram`, `.pdata`) match for both `ntdll.dll` and `kernel32.dll`. Their `.rdata` sections each differ at ten bytes: the PE CodeView debug-directory timestamp and PDB GUID. `llvm-readobj --coff-debug-directory` reports timestamp/GUID `0x6ACA8F88` / `{50F759A0-7776-C9E1-4C4C-44205044422E}` in the first build and `0x6ACA9C36` / `{1FC09849-8CB8-BEDD-4C4C-44205044422E}` in the second. The COFF file-header timestamp changes to the same build time. These are linker-generated debug identity fields, not PE code or ARM64X metadata.
- PE `.debug_*` hashes differ. The `.debug_info` and `.debug_str` virtual sizes also change with the different path lengths; the debug data embeds each output root (`strings -a` shows the two distinct build directories). Debug sections were excluded from the non-debug section comparison.
- No code signing or signature was performed in either build.

This supports repeatable compilation with equivalent reviewed instruction streams and Windows code/ABI sections for these selected artifacts. It does **not** establish bit-for-bit reproducibility, test every output in the build tree, verify ARM64EC transitions, or demonstrate that any Wine process can execute. A future hermetic build should keep the installation prefix stable or make it relocatable, and should control linker-generated UUID/CodeView identifiers if byte-identical packages are a goal.

## Reproduction commands

```sh
WINFERRY_NATIVE_BUILD_LOG_DIR=/path/to/logs-first JOBS=2 research/experiments/native-wine-build/build.sh \
  /path/to/source/wine-a15ee2ccf20e2fc9f470badd916855801933d31f \
  /path/to/toolchain/llvm-mingw-20261006-ucrt-macos-universal \
  /path/to/tools/bison/bin /path/to/build-one

WINFERRY_NATIVE_BUILD_LOG_DIR=/path/to/logs-second JOBS=2 research/experiments/native-wine-build/build.sh \
  /path/to/source/wine-a15ee2ccf20e2fc9f470badd916855801933d31f \
  /path/to/toolchain/llvm-mingw-20261006-ucrt-macos-universal \
  /path/to/tools/bison/bin /path/to/build-two

python3 research/experiments/native-wine-build/compare-build-sections.py \
  /path/to/build-one /path/to/build-two --output compare-sections.json
python3 research/experiments/native-wine-build/compare-macho-disassembly.py \
  /path/to/build-one /path/to/build-two --output compare-disassembly.json
```

The two builds used different output-root names above; this is deliberate evidence explaining why raw hashes differ. Run on macOS with Xcode command-line tools for the disassembly comparison.
