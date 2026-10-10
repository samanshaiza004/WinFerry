#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
    echo "usage: $0 LABEL EXECUTABLE [PROBE-ARG ...]" >&2
    exit 2
fi

label=$1
input=$2
shift 2
case "$label" in
    *[!A-Za-z0-9_.-]*|'') echo "label must use letters, digits, '.', '_' or '-'" >&2; exit 2 ;;
esac
if [ ! -f "$input" ]; then
    echo "executable not found: $input" >&2
    exit 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
output_dir=${CAPABILITY_PROBE_OUTPUT_DIR:-"$script_dir/results"}
mkdir -p "$output_dir"
binary_dir=$(CDPATH= cd -- "$(dirname -- "$input")" && pwd -P)
binary_name=$(basename -- "$input")
binary="$binary_dir/$binary_name"
stem="$output_dir/$label"

(cd "$binary_dir" && shasum -a 256 "./$binary_name") > "$stem.sha256.txt"
(cd "$binary_dir" && file "./$binary_name") > "$stem.file.txt"
(cd "$binary_dir" && otool -l "./$binary_name") > "$stem.load-commands.txt" 2>&1 || true

if (cd "$binary_dir" && codesign --display --verbose=4 --entitlements :- "./$binary_name") \
    > "$stem.signature.txt" 2>&1; then
    echo "display_exit=0" >> "$stem.signature.txt"
else
    code=$?
    echo "display_exit=$code" >> "$stem.signature.txt"
fi
if (cd "$binary_dir" && codesign --verify --strict --verbose=2 "./$binary_name") \
    > "$stem.verify.txt" 2>&1; then
    echo "verify_exit=0" >> "$stem.verify.txt"
else
    code=$?
    echo "verify_exit=$code" >> "$stem.verify.txt"
fi

started_at=$(date '+%Y-%m-%d %H:%M:%S%z')
set +e
"$binary" "$@" > "$stem.result.jsonl" 2> "$stem.stderr.txt"
run_code=$?
ended_at=$(date '+%Y-%m-%d %H:%M:%S%z')
set -e
echo "process_exit=$run_code" >> "$stem.stderr.txt"
printf 'start=%s\nend=%s\n' "$started_at" "$ended_at" > "$stem.unified-log-window.txt"

set +e
/usr/bin/log show --start "$started_at" --end "$ended_at" --style json \
    --predicate "process == \"$(basename -- "$binary")\"" \
    > "$stem.unified-log.json" 2> "$stem.unified-log.stderr.txt"
log_code=$?
set -e
if [ ! -s "$stem.unified-log.json" ]; then
    printf '{"status":"unavailable","command_exit":%s,"reason":"%s"}\n' \
        "$log_code" "$(cat "$stem.unified-log.stderr.txt" | tr '\n' ' ' | sed 's/"/\\"/g')" \
        > "$stem.unified-log.json"
fi

# A failed posix_spawn may leave no event under the target executable's name.
# Keep this query in the same short launch window and look for process launch,
# code-signing, and cross-architecture diagnostics from the relevant services.
set +e
/usr/bin/log show --start "$started_at" --end "$ended_at" --style json \
    --predicate "(process == \"$(basename -- "$binary")\" OR process == \"amfid\" OR process == \"taskgated\" OR process == \"launchd\") OR (subsystem CONTAINS[c] \"codesign\" OR eventMessage CONTAINS[c] \"posix_spawn\" OR eventMessage CONTAINS[c] \"EBADMACHO\" OR eventMessage CONTAINS[c] \"malformed Mach-O\" OR eventMessage CONTAINS[c] \"cross-architecture\")" \
    > "$stem.unified-log-diagnostics.json" 2> "$stem.unified-log-diagnostics.stderr.txt"
diagnostics_code=$?
set -e
if [ ! -s "$stem.unified-log-diagnostics.json" ]; then
    printf '{"status":"unavailable","command_exit":%s,"reason":"%s"}\n' \
        "$diagnostics_code" "$(cat "$stem.unified-log-diagnostics.stderr.txt" | tr '\n' ' ' | sed 's/"/\\"/g')" \
        > "$stem.unified-log-diagnostics.json"
fi

repo_dir=$(CDPATH= cd -- "$script_dir/../.." && pwd -P)
python3 - "$repo_dir" "$stem" <<'PY'
from pathlib import Path
import sys

repo_dir, stem = sys.argv[1:]
for suffix in (".sha256.txt", ".file.txt", ".load-commands.txt", ".signature.txt",
               ".verify.txt", ".result.jsonl", ".stderr.txt",
               ".unified-log-window.txt", ".unified-log.json", ".unified-log.stderr.txt",
               ".unified-log-diagnostics.json", ".unified-log-diagnostics.stderr.txt"):
    path = Path(stem + suffix)
    if path.exists():
        content = path.read_text(errors="replace")
        path.write_text(content.replace(repo_dir, "<repository>"))
PY

printf '%s: process exit %s; results in %s\n' "$label" "$run_code" "$stem"
