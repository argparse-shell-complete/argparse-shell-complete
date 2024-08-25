#!/usr/bin/python3

from . import helpers

_GET_POSITIONAL_FUNC = helpers.ShellFunction('zsh_helper', r'''
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
''')

_EXEC = helpers.ShellFunction('exec', r'''
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
''')

class ZSH_Helpers(helpers.GeneralHelpers):
    def __init__(self, function_prefix):
        super().__init__(function_prefix)
        self.add_function(_GET_POSITIONAL_FUNC)
        self.add_function(_EXEC)
