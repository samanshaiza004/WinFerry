# Experimental Darwin loader patch

This directory contains one small, **build-only** forward-port against Wine
`a15ee2ccf20e2fc9f470badd916855801933d31f`. It adds a macOS ARM64-only,
one-attempt re-exec request for a 4 KB process before the loader reserves Wine's
guest address space. It preserves the original argument vector and inherited
environment, reports each API failure, and stops if the process replacement
unexpectedly returns.

The layout flags in [`build-darwin-loader-only.sh`](../../build-darwin-loader-only.sh)
are an isolated linker override based on the manual command documented by the
[public experimental Wine fork](https://github.com/gzimbric/wine-arm64-macos/blob/21c45a2c3bb32e5b2a1ed92d72be6f2e6e3e72f6/docs/macos-arm64/BUILD.md#L32).
The source patch follows the fork's reported `posix_spawnattr_set_4k_page_size_np`
and `POSIX_SPAWN_SETEXEC` design, but is newly written against the pinned source
and is not a cherry-pick.

The patched Wine source file carries Wine's LGPL-2.1-or-later notice. The WinFerry
research repository does not currently include a top-level license, so this
artifact is experimental and is not a packaged runtime release. See the
[license status](../../../../06-licensing-security.md) before reuse or distribution.

`build-darwin-loader-only.sh` copies the supplied pinned source tree, applies the
patch to that copy, configures a minimal tree, replaces one exact loader-link
value in Wine's generated top-level Makefile, and links only `loader/wine` with
the experimental low-address layout. The script aborts unless that generated
rule occurs exactly once, then checks the linked `__PAGEZERO` and `__TEXT`
addresses and verifies its local ad-hoc signature with
[`verify-darwin-loader-artifact.py`](../../verify-darwin-loader-artifact.py). It never runs the output. The static check
[`test-darwin-loader-contract.py`](../../test-darwin-loader-contract.py) verifies
ordering, platform/API guards, re-exec bounds, argument/environment preservation,
and the deliberately limited patch scope. It does not prove entitlement access,
successful process creation, correct page size, low-address mappings, x18 state,
signal behavior, or any Wine execution.

This tranche is capped at one Wine source file and one loader-specific link
recipe. The platform capability harness remains independent. x18 ABI transitions,
signals/exceptions, FEX, graphics, UI, bundle signing, and Gate 0A/0B authorization
are deferred. Do not use this as evidence that a stock Mac can launch the loader.
