#!/bin/bash

unset CDPATH
set -u +o histexpand

foo() {
  local -a POSITIONALS
  local POSITIONAL_INDEX=0
  local argi c
  local HAVE_ARG=0 HAVE_A=0 HAVE_B=0

  for ((argi=1; argi <= $#; ++argi)); do
    local arg="${!argi}"

    case "$arg" in
      --arg|--arg=*)
        HAVE_ARG=1
        [[ "$arg" == *"="* ]] || (( ++argi ))
        ;;
      --)
        (( ++argi ))
        break
        ;;
      --*)
        ;;
      -)
        POSITIONALS[$((POSITIONAL_INDEX++))]="$arg"
        ;;
      -*)
        for ((c=1; c < ${#arg}; ++c)); do
          local char="${arg:$c:1}"
          case "$char" in
            a)
              HAVE_A=1
              (( $c + 1 < ${#arg} )) || (( ++argi ))
              break;
              ;;
            b)
              HAVE_B=1
          esac
        done
        ;;
      *)
        POSITIONALS[$((POSITIONAL_INDEX++))]="$arg"
        ;;
    esac
  done

  for ((; argi <= $#; ++argi)); do
    POSITIONALS[$((POSITIONAL_INDEX++))]="${!argi}"
  done

  echo "HAVE_B=$HAVE_B"
  echo "HAVE_A=$HAVE_A"
  echo "HAVE_ARG=$HAVE_ARG"
  echo "POSITIONALS=${POSITIONALS[@]}"
}

foo --arg=foo -ba bar foo -- bar baz

exec_() {
  local IFS=$'\n'
  local -a OUTPUT_LINES=($(eval "$1"))
  unset IFS
  local LINE
  for LINE in "${OUTPUT_LINES[@]}"; do
    LINE="${LINE%%$'\t'*}"
    if [[ "$LINE" == "$cur"* ]]; then
      COMPREPLY+=("$(printf '%q' "$LINE")")
    fi
  done
}
