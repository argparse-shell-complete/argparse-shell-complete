#!/usr/bin/zsh

get_positional() {
  local FUNC="get_positional"
  local CONTAINS="${FUNC}_contains"

  $CONTAINS() {
    local ARG KEY="$1"; shift
    for ARG; do [[ "$KEY" == "$ARG" ]] && return 0; done
    return 1
  }

  local IFS=','
  local -a OPTIONS=(${=1})
  local WANTED_POSITIONAL=$2
  unset IFS
  shift 2

  local -a   OLD_OPTS_WITH_ARG   OLD_OPTS_WITH_OPTIONAL_ARG   OLD_OPTS_WITHOUT_ARG
  local -a  LONG_OPTS_WITH_ARG  LONG_OPTS_WITH_OPTIONAL_ARG  LONG_OPTS_WITHOUT_ARG
  local -a SHORT_OPTS_WITH_ARG SHORT_OPTS_WITH_OPTIONAL_ARG SHORT_OPTS_WITHOUT_ARG

  local OPTION
  for OPTION in "${OPTIONS[@]}"; do
    case "$OPTION" in
      (--?*=)    LONG_OPTS_WITH_ARG+=("${OPTION//=/}");;
      (--?*=\?)  LONG_OPTS_WITH_OPTIONAL_ARG+=("${OPTION//=?/}");;
      (--?*);    LONG_OPTS_WITHOUT_ARG+=("$OPTION");;

      (-?=)      SHORT_OPTS_WITH_ARG+=("${OPTION//=/}");;
      (-?=\?)    SHORT_OPTS_WITH_OPTIONAL_ARG+=("${OPTION//=?/}");;
      (-?)       SHORT_OPTS_WITHOUT_ARG+=("$OPTION");;

      (-??*=)    OLD_OPTS_WITH_ARG+=("${OPTION//=/}");;
      (-??*=\?)  OLD_OPTS_WITH_OPTIONAL_ARG+=("${OPTION//=?/}");;
      (-??*)     OLD_OPTS_WITHOUT_ARG+=("$OPTION");;

      (*) echo "$FUNC: $OPTION: not a valid short, long or oldstyle option" >&2; return 1;;
    esac
  done

  local -a POSITIONALS
  local -a HAVING_OPTIONS

  local ARGI=2 # ARGI[1] is program name
  while [[ $ARGI -le $# ]]; do
    local ARG="${@[$ARGI]}"
    local HAVE_TRAILING_ARG=$(test $ARGI -lt $# && echo true || echo false)

    case "$ARG" in
      (-)
        POSITIONALS+=(-);;
      (--)
        for ARGI in $(seq $((ARGI + 1)) $#); do
          POSITIONALS+=("${@[$ARGI]}")
        done
        break;;
      (--*)
        for OPTION in $LONG_OPTS_WITH_ARG $LONG_OPTS_WITHOUT_ARG $LONG_OPTS_WITH_OPTIONAL_ARG; do
          if [[ "$ARG" == "$OPTION="* ]]; then
            HAVING_OPTIONS+=("$OPTION")
            break
          elif [[ "$ARG" == "$OPTION" ]]; then
            if $CONTAINS "$OPTION" "${LONG_OPTS_WITH_ARG[@]}"; then
              if $HAVE_TRAILING_ARG; then
                HAVING_OPTIONS+=("$OPTION")
                (( ARGI++ ))
              fi
            else
              HAVING_OPTIONS+=("$OPTION")
            fi
            break
          fi
        done;;
      (-*)
        local HAVE_MATCH=false

        for OPTION in $OLD_OPTS_WITH_ARG $OLD_OPTS_WITHOUT_ARG $OLD_OPTS_WITH_OPTIONAL_ARG; do
          if [[ "$ARG" == "$OPTION="* ]]; then
            HAVING_OPTIONS+=("$OPTION")
            HAVE_MATCH=true
            break
          elif [[ "$ARG" == "$OPTION" ]]; then
            if $CONTAINS "$OPTION" "${OLD_OPTS_WITH_ARG[@]}"; then
              if $HAVE_TRAILING_ARG; then
                HAVING_OPTIONS+=("$OPTION")
                (( ARGI++ ))
              fi
            else
              HAVING_OPTIONS+=("$OPTION")
            fi

            HAVE_MATCH=true
            break
          fi
        done

        if ! $HAVE_MATCH; then
          local ARG_LENGTH=${#ARG}
          local I=1
          local IS_END=false
          while ! $IS_END && test $I -lt $ARG_LENGTH; do
            local ARG_CHAR="${ARG:$I:1}"
            local HAVE_TRAILING_CHARS=$(test $((I+1)) -lt $ARG_LENGTH && echo true || echo false)

            for OPTION in $SHORT_OPTS_WITH_ARG $SHORT_OPTS_WITHOUT_ARG $SHORT_OPTS_WITH_OPTIONAL_ARG; do
              local OPTION_CHAR="${OPTION:1:1}"

              if test "$ARG_CHAR" = "$OPTION_CHAR"; then
                if $CONTAINS "$OPTION" "${SHORT_OPTS_WITH_ARG[@]}"; then
                  if $HAVE_TRAILING_CHARS; then
                    HAVING_OPTIONS+=("$OPTION")
                    IS_END=true
                  elif $HAVE_TRAILING_ARG; then
                    HAVING_OPTIONS+=("$OPTION")
                    (( ARGI++ ))
                    IS_END=true
                  fi
                elif $CONTAINS "$OPTION" "${SHORT_OPTS_WITH_OPTIONAL_ARG[@]}"; then
                  HAVING_OPTIONS+=("$OPTION")

                  if $HAVE_TRAILING_CHARS; then
                    IS_END=true
                  fi
                else
                  HAVING_OPTIONS+=("$OPTION")
                fi

                break
              fi
            done

            (( I++ ))
          done
        fi;;
      (*)
        POSITIONALS+=("$ARG");;
    esac
  
    (( ARGI++ ))
  done

  if test $WANTED_POSITIONAL -eq 0; then
    echo "$FUNC: argv[2]: positionals start at 1, not 0!" >&2
    return 1
  fi

  printf "%s" "${POSITIONALS[$WANTED_POSITIONAL]}"
}

_exec() {
  local IFS=$'\n'
  local -a OUTPUT_LINES=($(eval "$1"))
  unset IFS

  local -a DESCRIBE
  local LINE

  for LINE in "${OUTPUT_LINES[@]}"; do
    LINE="${LINE/:/\\:/}"
    LINE="${LINE/$'\t'/:}"
    DESCRIBE+=("$LINE")
  done

  _describe '' DESCRIBE
}

# =============================================================================
# TEST CODE
# =============================================================================

test_case() {
  local TEST_NUMBER="$1"; shift
  local EXPECTED="$1"; shift
  local RESULT="$(get_positional "$@")"
  echo -n "Testing $TEST_NUMBER ... "
  if [[ "$EXPECTED" != "$RESULT" ]]; then
    echo "expected '$EXPECTED', got '$RESULT'"
    exit 1
  else
    echo "OK"
  fi
}

opts='-f,--flag,-flag,-a=,--arg=,-arg=,-o=?,--optional=?,-optional=?'
test_case 01 'foo' ''      1 foo
test_case 02 'foo' "$opts" 1 foo
test_case 03 'foo' "$opts" 1 -f foo
test_case 04 'foo' "$opts" 1 -flag foo
test_case 05 'foo' "$opts" 1 --flag foo
test_case 06 'foo' "$opts" 1 -a arg foo
test_case 07 'foo' "$opts" 1 -arg arg foo
test_case 08 'foo' "$opts" 1 --arg arg foo
test_case 09 'foo' "$opts" 1 -aarg foo
test_case 10 'foo' "$opts" 1 -arg=arg foo
test_case 11 'foo' "$opts" 1 --arg=arg foo
test_case 12 'foo' "$opts" 1 -o foo
test_case 13 'foo' "$opts" 1 -optional foo
test_case 14 'foo' "$opts" 1 --optional foo
test_case 15 'foo' "$opts" 1 -oarg foo
test_case 16 'foo' "$opts" 1 -optional=arg foo
test_case 17 'foo' "$opts" 1 --optional=arg foo
test_case 18 'foo' "$opts" 1 -foarg foo
test_case 19 'foo' "$opts" 1 -faarg foo
test_case 20 'foo' "$opts" 1 -fa arg foo
test_case 21 'foo' "$opts" 1 -- foo
test_case 22 '-'   "$opts" 1 -
test_case 23 '-f'  "$opts" 1 -- -f
