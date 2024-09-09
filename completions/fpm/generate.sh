#!/bin/bash

if [[ -x ../../argparse-shell-complete ]]; then
  argparse_shell_complete='../../argparse-shell-complete'
elif which argparse-shell-complete; then
  argparse_shell_complete=argparse-shell-complete
else
  echo "No argparse-shell-complete found"
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 {bash,fish,zsh} <options>" >&2
  exit 1
fi

[[ "$1" == "bash" ]] || [[ "$1" == "fish" ]] || [[ "$1" == "zsh" ]] || {
  echo "\$1: invalid argument: $1" >&2
  exit 1
}

opts=''
if [[ "$1" == 'fish' ]]; then
  # --multiple-options=False (which is the default) makes the
  # commpletion slower.
  opts='--multiple-options=True'
fi

$argparse_shell_complete --allow-python $opts "$@" fpm.py
