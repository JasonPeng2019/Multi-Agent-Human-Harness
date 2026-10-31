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
    version=$("$python_bin" --version 2>&1 || true)
    if [[ "$version" =~ ^Python\ 3\.([0-9]+) ]] && ((10#${BASH_REMATCH[1]} >= 10)); then
      exec "$python_bin" "$script_dir/multi_agent.py" launch "$@"
    fi
  fi
done
printf 'Python 3.10 or later is required to launch a portable multi-agent worker. Set PYTHON or install python3.\n' >&2
exit 127
