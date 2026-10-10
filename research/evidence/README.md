# Evidence index

Collected 2026-10-10. These files document source inspection, not successful runtime execution.

- [Native SDK inspection](native-sdk-inspection.txt): exact local header paths, relevant lines and SHA256 hashes.
- [Wine source inspection](native-source-inspection.txt): inspected file hashes and bounded query scope; [upstream metadata](native-wine-upstream-metadata.json) and [fork metadata](native-wine-fork-metadata.json) pin revisions. Fork [build](native-wine-fork-build.md) and [status](native-wine-fork-status.md) snapshots retain explicit reproducibility limitations.
- [FEX source inspection](fex-source-inspection.md): source hashes, revision dates, public fork comparison and line references; neighboring fex JSON files record API revision/history responses.
- [Graphics inspection index](graphics-index.md): source provenance, pinned snapshots, revision JSONs and SHA256 manifest. Original license/contribution notices are retained with snapshots.
- [Landscape source register](landscape-sources.md): primary source access dates, immutable metadata where acquired, mutable-source and access limitations.
- [Local experiment results](../experiments/README.md): actual commands/source/logs and separately labeled untested Wine/FEX procedure.

Do not equate a source download, build target, vendor claim or proposed procedure with a local successful execution. API commit metadata dates are preserved without interpreting them as release dates. Source code snapshots retain their original licenses; no proprietary binary or source was copied.

Upstream document snapshots retain their original relative links. Resolve those against the pinned upstream repository in the chapter/index, not this flattened evidence directory. Missing snapshot-relative targets are not missing authored report chapters.
