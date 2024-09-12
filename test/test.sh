#!/bin/bash

cd "$(dirname "$0")"

if [[ -x ../argparse-shell-complete ]]; then
  argparse_shell_complete='../argparse-shell-complete'
elif which argparse-shell-complete; then
  argparse_shell_complete=argparse-shell-complete
else
  echo "No argparse-shell-complete found"
  exit 1
fi

ARGPARSE_SHELLCOMPLETE_TEST=./argparse-shell-complete-test
ARGPARSE_SHELLCOMPLETE_TEST_BIN_FILE=/bin/argparse-shell-complete-test

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root"
  exit 1
fi

declare -a SHELLS=()
SHELLS+=(bash)
SHELLS+=(fish)
SHELLS+=(zsh)

install-completions() {
  cp "$ARGPARSE_SHELLCOMPLETE_TEST" "$ARGPARSE_SHELLCOMPLETE_TEST_BIN_FILE"

  for SHELL_ in ${SHELLS[@]}; do
    case "$SHELL_" in
      bash)
        $argparse_shell_complete -i --allow-python --include-file include.bash \
          bash argparse-shell-complete-test || {
          echo "$argparse_shell_complete bash failed" >&2
          exit 1
        };;
      fish)
        $argparse_shell_complete -i --allow-python --include-file include.fish \
          fish argparse-shell-complete-test || {
          echo "$argparse_shell_complete fish failed" >&2
          exit 1
        };;
      zsh)
        $argparse_shell_complete -i --allow-python --include-file include.zsh \
          zsh  argparse-shell-complete-test || {
          echo "$argparse_shell_complete zsh failed" >&2
          exit 1
        };;
    esac
  done
}

uninstall-completions() {
  rm -f "$ARGPARSE_SHELLCOMPLETE_TEST_BIN_FILE"

  for SHELL_ in ${SHELLS[@]}; do
    case "$SHELL_" in
      bash) $argparse_shell_complete -u --allow-python bash argparse-shell-complete-test;;
      fish) $argparse_shell_complete -u --allow-python fish argparse-shell-complete-test;;
      zsh)  $argparse_shell_complete -u --allow-python zsh  argparse-shell-complete-test;;
    esac
  done
}

do-test() {
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo ""
  echo "This script will install argparse-shell-complete-test completions"
  echo ""
  echo "Press Enter to continue, or CTRL+C to exit"
  read

  install-completions

  echo ""
  echo "Press Enter to remove the completion files"
  read

  uninstall-completions
}

if [[ $# -eq 0 ]]; then
  cat << EOF
Usage: $0 test|install|uninstall
EOF
  exit 1
elif [[ "$1" == "test" ]]; then
  do-test
elif [[ "$1" == "install" ]]; then
  install-completions
elif [[ "$1" == "uninstall" ]]; then
  uninstall-completions
else
  echo "Invalid command: $1" >&2
  exit 1
fi
