#!/usr/bin/env bash
# Bridge the multi-agent launcher's file-path prompt delivery to a worker CLI
# that reads its prompt from stdin instead of a file-path argument (for
# example `claude -p` or `codex exec`, both documented to read stdin when no
# prompt argument is given). The launcher's schema requires {prompt_file} to
# appear literally in the command array; this script consumes that argument,
# then execs the real worker with the file's bytes on stdin.
#
# Usage: pipe-prompt-file.sh <prompt-file> -- <command> [args...]
set -euo pipefail

usage() {
  printf 'usage: pipe-prompt-file.sh <prompt-file> -- <command> [args...]\n' >&2
}

prompt_file=${1:-}
if [[ -z "$prompt_file" ]]; then
  usage
  exit 2
fi
shift
if [[ "${1:-}" != "--" ]]; then
  usage
  exit 2
fi
shift
if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi
if [[ ! -f "$prompt_file" ]]; then
  printf 'pipe-prompt-file: prompt file not found: %s\n' "$prompt_file" >&2
  exit 2
fi

exec "$@" < "$prompt_file"
