# Pinned upstream Wine source audit

Inspection date: 2026-10-10. Source: `wine-mirror/wine` commit [`a15ee2ccf20e2fc9f470badd916855801933d31f`](https://github.com/wine-mirror/wine/commit/a15ee2ccf20e2fc9f470badd916855801933d31f), downloaded archive SHA-256 `f87b071f5f19f4cc5b6a51d3000ae03ee791325d5873ba221da191fd5b933a41`.

## Verified source facts

- `configure.ac:991` sets the macOS loader flags to `-Wl,-segalign,0x1000,-pagezero_size,0x1000,...`. This pinned upstream source does not use the reported newer `-x86_64_layout_emulation` layout.
- `configure.ac:19`, `configure.ac:382-414`, and `configure.ac:438-444` support multi-architecture PE builds and select architecture-specific MinGW compilers. The native host is separately detected as `aarch64-apple-darwin27.0.0` in the local configure log.
- Exact-symbol searches over the full unpacked source returned no matches for `posix_spawnattr_set_4k_page_size_np`, `os_set_custom_x18_abi_enabled`, or `x86_64_layout_emulation`. This verifies only that those spellings and mechanisms are absent in this source revision; it does not show that no equivalent behavior exists under another name.

These findings are scoped to the upstream snapshot above. They do not describe the proprietary CrossOver Preview tree or the separate experimental Wine fork, and they do not establish whether the source can be made runnable with a small patch.
