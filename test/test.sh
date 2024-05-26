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

BASH_COMPLETIONS_DIR="$(pkg-config --variable=completionsdir bash-completion)" || {
  echo "'pkg-config --variable=completionsdir bash-completion' failed"
  BASH_COMPLETIONS_DIR=/usr/share/bash-completion/completions
}

FISH_COMPLETIONS_DIR="$(pkg-config --variable=completionsdir fish)" || {
  echo "'pkg-config --variable=completionsdir fish' failed"
  FISH_COMPLETIONS_DIR=/usr/share/fish/completions
}

ZSH_COMPLETIONS_DIR=/usr/share/zsh/site-functions

BASH_COMPLETION_FIlE="$BASH_COMPLETIONS_DIR/argparse-shell-complete-test"
FISH_COMPLETION_FILE="$FISH_COMPLETIONS_DIR/argparse-shell-complete-test.fish"
ZSH_COMPLETION_FILE="$ZSH_COMPLETIONS_DIR/_argparse-shell-complete-test"

declare -a SHELLS=()

if [[ -d "$BASH_COMPLETIONS_DIR" ]]; then
  SHELLS+=(bash)
else
  echo "BASH_COMPLETIONS_DIR ($BASH_COMPLETIONS_DIR) not found"
fi

if [[ -d "$FISH_COMPLETIONS_DIR" ]]; then
  SHELLS+=(fish)
else
  echo "FISH_COMPLETIONS_DIR ($FISH_COMPLETIONS_DIR) not found"
fi

if [[ -d "$ZSH_COMPLETIONS_DIR" ]]; then
  SHELLS+=(zsh)
else
  echo "ZSH_COMPLETIONS_DIR ($ZSH_COMPLETIONS_DIR) not found"
fi

install-completions() {
  cp "$ARGPARSE_SHELLCOMPLETE_TEST" "$ARGPARSE_SHELLCOMPLETE_TEST_BIN_FILE"

  for SHELL_ in ${SHELLS[@]}; do
    case "$SHELL_" in
      bash)
        $argparse_shell_complete --include-file argparse-shell-complete-test.bash \
          bash argparse-shell-complete-test > "$BASH_COMPLETION_FIlE" || {
          echo "$argparse_shell_complete bash failed" >&2
          exit 1
        };;
      fish)
        $argparse_shell_complete --include-file argparse-shell-complete-test.fish \
          fish argparse-shell-complete-test > "$FISH_COMPLETION_FILE" || {
          echo "$argparse_shell_complete fish failed" >&2
          exit 1
        };;
      zsh)
        $argparse_shell_complete --include-file argparse-shell-complete-test.zsh \
          zsh  argparse-shell-complete-test > "$ZSH_COMPLETION_FILE" || {
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
      bash) rm -f "$BASH_COMPLETION_FIlE";;
      fish) rm -f "$FISH_COMPLETION_FILE";;
      zsh)  rm -f "$ZSH_COMPLETION_FILE";;
    esac
  done
}

do-test() {
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo ""
  echo "This script will install argparse-shell-complete-test completions in the following directories:"
  echo " bash: $BASH_COMPLETIONS_DIR"
  echo " fish: $FISH_COMPLETIONS_DIR"
  echo "  zsh: $ZSH_COMPLETIONS_DIR"
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
