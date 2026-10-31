#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [[ -n "${PYTHON:-}" ]]; then
  candidates=("$PYTHON")
else
  candidates=(python3 python)
fi
for python_bin in "${candidates[@]}"; do
  if command -v "$python_bin" >/dev/null 2>&1; then
    # command -v only confirms a file exists on PATH: Windows ships a python3
    # App Execution Alias stub by default that resolves this way but exits
    # nonzero telling the user to install from the Microsoft Store. Actually
    # invoke the candidate and check its reported version to confirm it runs.
    version=$("$python_bin" --version 2>&1 || true)
    if [[ "$version" =~ ^Python\ 3\.([0-9]+) ]] && ((10#${BASH_REMATCH[1]} >= 10)); then
      exec "$python_bin" "$script_dir/select-skillset.py" "$@"
    fi
  fi
done
printf 'select-skillset: Python 3.10 or later is required. Set PYTHON or install python3.\n' >&2
exit 127
