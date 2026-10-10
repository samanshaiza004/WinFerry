# Experimental Darwin loader patch

This directory contains two small, **build-only** forward-port patches against Wine
`a15ee2ccf20e2fc9f470badd916855801933d31f`. It adds a macOS ARM64-only,
one-attempt re-exec request for a 4 KB process before the loader reserves Wine's
guest address space, clears its re-exec marker after entering a 4 KB process,
and puts the low-address loader layout in Wine's Darwin ARM64 configure branch.
The re-exec preserves the original argument vector and inherited environment,
reports each API failure, and stops if the process replacement unexpectedly
returns.

Patch 0002 applies the linker flags from the manual command documented by the
[public experimental Wine fork](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/docs/macos-arm64/BUILD.md#L32)
through `configure.ac` and the checked-in generated `configure` script. Patch
0001 follows the fork's reported `posix_spawnattr_set_4k_page_size_np` and
`POSIX_SPAWN_SETEXEC` design, but both patches are newly written against the
pinned source and are not cherry-picks.

The Wine-derived patches retain LGPL-2.1-or-later terms and notices. WinFerry's
original research and code are MIT-licensed; see [`THIRD_PARTY.md`](../../../../../THIRD_PARTY.md)
for the boundary and attribution details. This artifact is experimental and is
not a packaged runtime release.

`build-darwin-loader-only.sh` copies the supplied pinned source tree, applies both
patches to that copy, configures a minimal tree, verifies Wine emitted the exact
expected loader-link flags, and links only `loader/wine` with the experimental
low-address layout. It then checks the linked `__PAGEZERO` and `__TEXT` addresses
and verifies its local ad-hoc signature with
[`verify-darwin-loader-artifact.py`](../../verify-darwin-loader-artifact.py). It never runs the output. The static check
[`test-darwin-loader-contract.py`](../../test-darwin-loader-contract.py) verifies
ordering, platform/API guards, marker cleanup and re-exec bounds, configured
layout flags, argument/environment preservation, and the deliberately limited
patch scope. These are structural checks. They do not prove entitlement access,
successful process creation, correct page size, low-address mappings, x18 state,
signal behavior, or any Wine execution.

This tranche is capped at one Wine loader source file and two small build-system
files (`configure.ac` and generated `configure`). The platform capability harness
remains independent. x18 ABI transitions,
signals/exceptions, FEX, graphics, UI, bundle signing, and Gate 0A/0B authorization
are deferred. Do not use this as evidence that a stock Mac can launch the loader.
