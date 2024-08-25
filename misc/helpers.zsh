#!/usr/bin/zsh

zsh_helper() {
  local FUNC="zsh_helper"
  local CONTAINS="${FUNC}_contains"

  $CONTAINS() {
    local ARG KEY="$1"; shift
    for ARG; do [[ "$KEY" == "$ARG" ]] && return 0; done
    return 1
  }

  local IFS=','
  local -a OPTIONS=(${=1})
  unset IFS
  shift

  # ===========================================================================
  # Command parsing
  # ===========================================================================

  if [[ $# == 0 ]]; then
    echo "$FUNC: missing command" >&2
    return 1;
  fi

  local CMD=$1
  shift

  case "$CMD" in
    get_positional)
      local WANTED_POSITIONAL=$1
      shift
      if test $WANTED_POSITIONAL -eq 0; then
        echo "$FUNC: argv[2]: positionals start at 1, not 0!" >&2
        return 1
      fi
      ;;
    has_option)
      local -a HAS_OPTION
      local IS_END_OF_OPTIONS=false
      while test $# -ge 0; do
        if [[ "$1" == "--" ]]; then
          IS_END_OF_OPTIONS=true
          shift
          break
        else
          HAS_OPTION+=("$1")
          shift
        fi
      done

      if ! $IS_END_OF_OPTIONS; then
        echo "$FUNC: has_option: missing terminating '--'" >&2
        return 1
      fi
      ;;
    option_is)
      local -a CMD_OPTION_IS_OPTIONS CMD_OPTION_IS_VALUES
      local END_OF_OPTIONS_NUM=0

      while test $# -ge 0; do
        if [[ "$1" == "--" ]]; then
          if test $(( ++END_OF_OPTIONS_NUM )) -eq 2; then
            shift
            break
          fi
        elif test $END_OF_OPTIONS_NUM -eq 0; then
          CMD_OPTION_IS_OPTIONS+=("$1")
        elif test $END_OF_OPTIONS_NUM -eq 1; then
          CMD_OPTION_IS_VALUES+=("$1")
        fi

        shift
      done

      if test $END_OF_OPTIONS_NUM -ne 2; then
        echo "$FUNC: option_is: missing terminating '--'" >&2
        return 1
      fi
      ;;
    *)
      echo "$FUNC: argv[1]: invalid command" >&2
      return 1
      ;;
  esac

  # ===========================================================================
  # Parsing of available options
  # ===========================================================================

  local -a   OLD_OPTS_WITH_ARG   OLD_OPTS_WITH_OPTIONAL_ARG   OLD_OPTS_WITHOUT_ARG
  local -a  LONG_OPTS_WITH_ARG  LONG_OPTS_WITH_OPTIONAL_ARG  LONG_OPTS_WITHOUT_ARG
  local -a SHORT_OPTS_WITH_ARG SHORT_OPTS_WITH_OPTIONAL_ARG SHORT_OPTS_WITHOUT_ARG

  local OPTION
  for OPTION in "${OPTIONS[@]}"; do
    case "$OPTION" in
      --?*=)    LONG_OPTS_WITH_ARG+=("${OPTION%=}");;
      --?*=\?)  LONG_OPTS_WITH_OPTIONAL_ARG+=("${OPTION%=?}");;
      --?*)     LONG_OPTS_WITHOUT_ARG+=("$OPTION");;

      -?=)      SHORT_OPTS_WITH_ARG+=("${OPTION%=}");;
      -?=\?)    SHORT_OPTS_WITH_OPTIONAL_ARG+=("${OPTION%=?}");;
      -?)       SHORT_OPTS_WITHOUT_ARG+=("$OPTION");;

      -??*=)    OLD_OPTS_WITH_ARG+=("${OPTION%=}");;
      -??*=\?)  OLD_OPTS_WITH_OPTIONAL_ARG+=("${OPTION%=?}");;
      -??*)     OLD_OPTS_WITHOUT_ARG+=("$OPTION");;

      *) echo "$FUNC: $OPTION: not a valid short, long or oldstyle option" >&2; return 1;;
    esac
  done

  # ===========================================================================
  # Parsing of command line options
  # ===========================================================================

  local -a POSITIONALS
  local -a HAVING_OPTIONS
  local -a OPTION_VALUES

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
            OPTION_VALUES+=("${ARG#$OPTION=}")
            break
          elif [[ "$ARG" == "$OPTION" ]]; then
            if $CONTAINS "$OPTION" "${LONG_OPTS_WITH_ARG[@]}"; then
              if $HAVE_TRAILING_ARG; then
                HAVING_OPTIONS+=("$OPTION")
                OPTION_VALUES+=("${@[$((ARGI + 1))]}")
                (( ARGI++ ))
              fi
            else
              HAVING_OPTIONS+=("$OPTION")
              OPTION_VALUES+=("")
            fi
            break
          fi
        done;;
      (-*)
        local HAVE_MATCH=false

        for OPTION in $OLD_OPTS_WITH_ARG $OLD_OPTS_WITHOUT_ARG $OLD_OPTS_WITH_OPTIONAL_ARG; do
          if [[ "$ARG" == "$OPTION="* ]]; then
            HAVING_OPTIONS+=("$OPTION")
            OPTION_VALUES+=("${ARG#$OPTION=}")
            HAVE_MATCH=true
            break
          elif [[ "$ARG" == "$OPTION" ]]; then
            if $CONTAINS "$OPTION" "${OLD_OPTS_WITH_ARG[@]}"; then
              if $HAVE_TRAILING_ARG; then
                HAVING_OPTIONS+=("$OPTION")
                OPTION_VALUES+=("${@[$((ARGI + 1))]}")
                (( ARGI++ ))
              fi
            else
              HAVING_OPTIONS+=("$OPTION")
              OPTION_VALUES+=("")
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
                    OPTION_VALUES+=("${ARG:$((I+1))}")
                    IS_END=true
                  elif $HAVE_TRAILING_ARG; then
                    HAVING_OPTIONS+=("$OPTION")
                    OPTION_VALUES+=("${@[$((ARGI + 1))]}")
                    (( ARGI++ ))
                    IS_END=true
                  fi
                elif $CONTAINS "$OPTION" "${SHORT_OPTS_WITH_OPTIONAL_ARG[@]}"; then
                  HAVING_OPTIONS+=("$OPTION")

                  if $HAVE_TRAILING_CHARS; then
                    IS_END=true
                    OPTION_VALUES+=("${ARG:$((I+1))}")
                  else
                    OPTION_VALUES+=("")
                  fi
                else
                  HAVING_OPTIONS+=("$OPTION")
                  OPTION_VALUES+=("")
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

  # ===========================================================================
  # Execution of command
  # ===========================================================================

  case "$CMD" in
    get_positional)
      printf "%s" "${POSITIONALS[$WANTED_POSITIONAL]}"
      return 0
      ;;
    has_option)
      local OPTION=''
      for OPTION in "${HAVING_OPTIONS[@]}"; do
        $CONTAINS "$OPTION" "${HAS_OPTION[@]}" && return 0
      done
      return 1
      ;;
    option_is)
      local I=${#HAVING_OPTIONS[@]}
      while test $I -ge 1; do
        local OPTION="${HAVING_OPTIONS[$I]}"
        if $CONTAINS "$OPTION" "${CMD_OPTION_IS_OPTIONS[@]}"; then
          local VALUE="${OPTION_VALUES[$I]}"
          $CONTAINS "$VALUE" "${CMD_OPTION_IS_VALUES[@]}" && return 0
        fi

        (( --I ))
      done

      return 1
      ;;
  esac
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

if [[ $# == 1 ]] && [[ "$1" == "-q" ]]; then
  echo() {}
fi

test_case() {
  local TEST_NUMBER="$1"; shift
  local EXPECTED="$1"; shift
  local RESULT
  RESULT="$(zsh_helper "$@")"
  local RESULT_EXIT=$?
  echo -n "Testing $TEST_NUMBER ... "

  if [[ "$EXPECTED" == "-true" ]]; then;
    if test $RESULT_EXIT -ne 0; then
      echo "expected TRUE, got $RESULT_EXIT"
      exit 1
    fi
  elif [[ "$EXPECTED" == "-false" ]]; then;
    if test $RESULT_EXIT -eq 0; then
      echo "expected FALSE, got $RESULT_EXIT"
      exit 1
    fi
  elif [[ "$EXPECTED" != "$RESULT" ]]; then
    echo "expected '$EXPECTED', got '$RESULT'"
    exit 1
  fi

  echo "OK"
}

for i in $(seq 9999); do
opts='-f,--flag,-flag,-a=,--arg=,-arg=,-o=?,--optional=?,-optional=?'
test_case 01 'foo' ''      get_positional 1 prog foo
test_case 02 'foo' "$opts" get_positional 1 prog foo
test_case 03 'foo' "$opts" get_positional 1 prog -f foo
test_case 04 'foo' "$opts" get_positional 1 prog -flag foo
test_case 05 'foo' "$opts" get_positional 1 prog --flag foo
test_case 06 'foo' "$opts" get_positional 1 prog -a arg foo
test_case 07 'foo' "$opts" get_positional 1 prog -arg arg foo
test_case 08 'foo' "$opts" get_positional 1 prog --arg arg foo
test_case 09 'foo' "$opts" get_positional 1 prog -aarg foo
test_case 10 'foo' "$opts" get_positional 1 prog -arg=arg foo
test_case 11 'foo' "$opts" get_positional 1 prog --arg=arg foo
test_case 12 'foo' "$opts" get_positional 1 prog -o foo
test_case 13 'foo' "$opts" get_positional 1 prog -optional foo
test_case 14 'foo' "$opts" get_positional 1 prog --optional foo
test_case 15 'foo' "$opts" get_positional 1 prog -oarg foo
test_case 16 'foo' "$opts" get_positional 1 prog -optional=arg foo
test_case 17 'foo' "$opts" get_positional 1 prog --optional=arg foo
test_case 18 'foo' "$opts" get_positional 1 prog -foarg foo
test_case 19 'foo' "$opts" get_positional 1 prog -faarg foo
test_case 20 'foo' "$opts" get_positional 1 prog -fa arg foo
test_case 21 'foo' "$opts" get_positional 1 prog -- foo
test_case 22 '-'   "$opts" get_positional 1 prog -
test_case 23 '-f'  "$opts" get_positional 1 prog -- -f
test_case 24 -true "$opts" has_option -f --flag -flag -- prog -f
test_case 25 -true "$opts" has_option -f --flag -flag -- prog --flag
test_case 26 -true "$opts" has_option -f --flag -flag -- prog -flag
test_case 27 -false "$opts" has_option -f --flag -flag -- prog -- -f
test_case 28 -false "$opts" has_option -f --flag -flag -- prog -- --flag
test_case 29 -false "$opts" has_option -f --flag -flag -- prog -- -flag
test_case 30 -false "$opts" has_option -f --flag -flag -- prog --arg --flag
test_case 31 -false "$opts" has_option -f --flag -flag -- prog -a --flag
test_case 32 -true "$opts" option_is -a --arg -arg -- foo bar -- prog -a foo
test_case 33 -true "$opts" option_is -a --arg -arg -- foo bar -- prog --arg foo
test_case 34 -true "$opts" option_is -a --arg -arg -- foo bar -- prog -arg foo
test_case 35 -true "$opts" option_is -o --optional -optional -- foo bar -- prog -ofoo
test_case 36 -true "$opts" option_is -o --optional -optional -- foo bar -- prog --optional=foo
test_case 37 -true "$opts" option_is -o --optional -optional -- foo bar -- prog -optional=foo
test_case 38 -true "$opts" option_is -o --optional -optional -- foo bar -- prog -obar
test_case 39 -true "$opts" option_is -o --optional -optional -- foo bar -- prog --optional=bar
test_case 40 -true "$opts" option_is -o --optional -optional -- foo bar -- prog -optional=bar
test_case 41 -false "$opts" option_is -a --arg -arg -- foo -- prog -flag
done
