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
  echo "Usage: $0 {bash,fish,zsh}" >&2
  exit 1
elif [[ $# -gt 1 ]]; then
  echo "Too many arguments provided" >&2
  exit 1
fi

[[ "$1" == "bash" ]] || [[ "$1" == "fish" ]] || [[ "$1" == "zsh" ]] || {
  echo "\$1: invalid argument: $1" >&2
  exit 1
}

$argparse_shell_complete --multiple-options=True --zsh-compdef=False $1 fpm.py
