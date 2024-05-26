#!/usr/bin/python3

from . import helpers

_COMPGEN_W_REPLACEMENT = helpers.ShellFunction('compgen_w_replacement', r'''
local APPEND=0

[[ "$1" == "-a" ]] && { shift; APPEND=1; }
[[ "$1" == "--" ]] && { shift; }

local cur="$1"
shift

(( APPEND )) || COMPREPLY=()

for word; do
if [[ "$word" == "$cur"* ]]; then
  COMPREPLY+=("$(printf '%q' "$word")")
fi
done
''')

_EXEC = helpers.ShellFunction('exec', r'''
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
''')

class BASH_Helpers(helpers.GeneralHelpers):
    def __init__(self, function_prefix):
        super().__init__(function_prefix)
        self.add_function(_COMPGEN_W_REPLACEMENT)
        self.add_function(_EXEC)
