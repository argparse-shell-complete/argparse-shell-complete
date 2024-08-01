#!/usr/bin/python3

import subprocess

from . import shell, utils
from . import bash_helpers
from . import modeline
from . import generation_notice

def get_completions_file(program_name):
    command = ['pkg-config', '--variable=completionsdir', 'bash-completion']
    try:
        # throws FileNotFoundError if command is not available
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception('returncode != 0')
        dir = result.stdout.strip()
    except:
        utils.warn('%s failed' % ' '.join(command))
        dir = '/usr/share/bash-completion/completions'

    return '%s/%s' % (dir, program_name)

# =============================================================================
# Completion code
# =============================================================================

class BashCompletionBase():
    '''
    Base class for BASH completions.
    '''

    def get_command(self, append=False):
        '''
        Returns the command for BASH completion. If `append` is `True`, then
        the results will be appended to COMPREPLY, otherwise COMPREPLY will be truncated.

        Args:
            append (bool): If True, the results will be appended to COMPREPLY.

        Returns:
            str: The command for Bash completion.
        '''
        raise NotImplementedError

class BashCompletionCommand(BashCompletionBase):
    '''
    Used for completion functions that internally modify COMPREPLY.
    '''
    def __init__(self, ctxt, cmd):
        self.ctxt = ctxt
        self.cmd = cmd

    def get_command(self, append=False):
        if not self.cmd:
            return ''

        r = []

        if append:
            r += ['local -a COMPREPLY_BACK=("${COMPREPLY[@]}")']

        r += [self.cmd]

        if append:
            r += ['COMPREPLY=("${COMPREPLY_BACK[@]}" "${COMPREPLY[@]}")']

        return '\n'.join(r)

class Compgen_W(BashCompletionBase):
    def __init__(self, ctxt, values):
        self.ctxt = ctxt
        self.values = values

    def get_command(self, append=False):
        compgen_funcname = self.ctxt.helpers.use('compgen_w_replacement', True)
        return ('%s %s-- "$cur" %s' % (
            compgen_funcname,
            ('-a ' if append else ''),
            ' '.join(shell.escape(str(s)) for s in self.values)))

class BashCompletionCompgen(BashCompletionBase):
    '''
    Used for completion using `compgen`
    '''
    def __init__(self, ctxt, compgen_args, word='"$cur"'):
        self.compgen_args = compgen_args
        self.word = word

    def get_command(self, append=False):
        return 'COMPREPLY%s=($(compgen %s -- %s))' % (
            ('+' if append else ''),
            self.compgen_args,
            self.word)

class BashCompleter(shell.ShellCompleter):
    def none(self, ctxt):
        return BashCompletionCommand(ctxt, '')

    def choices(self, ctxt, choices):
        return Compgen_W(ctxt, choices)

    def command(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A command')

    def directory(self, ctxt, opts={}):
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

        if directory:
            return BashCompletionCommand(ctxt, 'cd %s\nfiledir -d\ncd -' % shell.escape(directory))
        else:
            return BashCompletionCommand(ctxt, '_filedir -d')

    def file(self, ctxt, opts={}):
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

        if directory:
            return BashCompletionCommand(ctxt, 'cd %s\nfiledir\ncd -' % shell.escape(directory))
        else:
            return BashCompletionCommand(ctxt, '_filedir')

    def group(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A group')

    def hostname(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A hostname')

    def pid(self, ctxt):
        return BashCompletionCommand(ctxt, '_pids')

    def process(self, ctxt):
        return BashCompletionCommand(ctxt, '_pnames')

    def range(self, ctxt, start, stop, step=1):
        if step == 1:
            return BashCompletionCompgen(ctxt, f"-W '{{{start}..{stop}}}'")
        else:
            return BashCompletionCompgen(ctxt, f"-W '{{{start}..{stop}..{step}}}'")

    def service(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A service')

    def user(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A user')

    def variable(self, ctxt):
        return BashCompletionCompgen(ctxt, '-A variable')

    def exec(self, ctxt, command):
        funcname = ctxt.helpers.use('exec', True)
        return BashCompletionCommand(ctxt, '%s %s' % (funcname, shell.escape(command)))

# =============================================================================
# Code for generating BASH auto completion scripts
# =============================================================================

def make_switch_case_pattern(option_strings):
    '''
    Generates a switch case pattern for `option_strings'
    '''
    r = []
    for option_string in sorted(option_strings):
        if len(option_string) == 2:
            r.append('-!(-*)' + shell.escape(option_string[1]))
        else:
            r.append(shell.escape(option_string))

    return '|'.join(r)

def make_option_variable_name(option):
    long_options = option.get_long_option_strings()
    if long_options:
        return shell.make_identifier('HAVE_%s' % long_options[0].lstrip('-'))

    old_options = option.get_old_option_strings()
    if old_options:
        return shell.make_identifier('HAVE_%s' % old_options[0].lstrip('-'))

    short_options = option.get_short_option_strings()
    if short_options:
        return 'HAVE_%s' % short_options[0][1]

    assert False, "make_option_variable_name: Should not be reached"

class BashCompletionGenerator():
    def __init__(self, ctxt, commandline):
        self.commandline = commandline
        self.ctxt        = ctxt
        self.options     = commandline.get_options()
        self.positionals = commandline.get_positionals()
        self.subcommands = commandline.get_subcommands_option()
        self.completer   = BashCompleter()
        self._complete_commandline()

    def _complete_action(self, action, append=True):
        context = self.ctxt.getOptionGenerationContext(self.commandline, action)
        return self.completer.complete(context, *action.complete).get_command(append)

    def _get_AbbreviationGeneratorForOptions(self, options):
        return utils.OptionAbbreviationGenerator(
            utils.flatten(o.get_long_option_strings() + o.get_old_option_strings() for o in options)
        )

    def _generate_options_parsing(self):
        def get_long_options_case_without_arg(options):
            return '|'.join(options)

        def get_long_options_case_with_arg(options):
            return '|'.join('%s=*' % o for o in options)

        def get_short_options_case(options):
            return '|'.join(o[1] for o in options)

        options = self.commandline.get_options(with_parent_options=True)

        if self.commandline.abbreviate_options:
            abbreviations = self._get_AbbreviationGeneratorForOptions(options)
        else:
            abbreviations = utils.DummyAbbreviationGenerator()

        local = ' '.join('%s=0' % make_option_variable_name(o) for o in options)

        case_long_options = []
        case_short_options = []

        for option in options:
            long_options  = abbreviations.get_many_abbreviations(option.get_long_option_strings())
            long_options += abbreviations.get_many_abbreviations(option.get_old_option_strings())
            short_options = option.get_short_option_strings()

            if long_options:
                if option.takes_args == '?':
                    r  = '%s);&\n'  % get_long_options_case_without_arg(long_options)
                    r += '%s)\n'    % get_long_options_case_with_arg(long_options)
                    r += '  %s=1;;' % make_option_variable_name(option)
                    case_long_options.append(r)
                elif option.takes_args:
                    r  = '%s)\n'    % get_long_options_case_without_arg(long_options)
                    r += '  (( ++argi ));&\n'
                    r += '%s)\n'    % get_long_options_case_with_arg(long_options)
                    r += '  %s=1;;' % make_option_variable_name(option)
                    case_long_options.append(r)
                else:
                    r  = '%s)\n' % get_long_options_case_without_arg(long_options)
                    r += '  %s=1;;' % make_option_variable_name(option)
                    case_long_options.append(r)

            if short_options:
                if option.takes_args == '?':
                    r  = '%s)\n'    % get_short_options_case(short_options)
                    r += '  %s=1\n' % make_option_variable_name(option)
                    r += '  break;;'
                    case_short_options.append(r)
                elif option.takes_args:
                    r  = '%s)\n'    % get_short_options_case(short_options)
                    r += '  %s=1\n' % make_option_variable_name(option)
                    r += '  $has_trailing_chars || (( ++argi ))\n'
                    r += '  break;;'
                    case_short_options.append(r)
                else:
                    r  = '%s)\n'    % get_short_options_case(short_options)
                    r += '  %s=1;;' % make_option_variable_name(option)
                    case_short_options.append(r)

        s = '''\
local -a POSITIONALS
local END_OF_OPTIONS=0 POSITIONAL_NUM=0 %LOCALS%

local argi
for ((argi=1; argi < ${#words[@]} - 1; ++argi)); do
  local arg="${words[$argi]}"

  case "$arg" in
%CASE_LONG_OPTIONS%
    --)
      END_OF_OPTIONS=1
      for ((++argi; argi < ${#words[@]}; ++argi)); do
        POSITIONALS[$((POSITIONAL_NUM++))]="${words[$argi]}"
      done
      break;;
    --*)
      ;;
    -)
      POSITIONALS[$((POSITIONAL_NUM++))]="-";;
    -*)
      local c
      for ((c=1; c < ${#arg}; ++c)); do
        local char="${arg:$c:1}"
        local has_trailing_chars=$( (( $c + 1 < ${#arg} )) && echo true || echo false)
        case "$char" in
%CASE_SHORT_OPTIONS%
        esac
      done;;
    *)
      POSITIONALS[$((POSITIONAL_NUM++))]="$arg";;
  esac
done

for ((; argi < ${#words[@]}; ++argi)); do
  local arg="${words[$argi]}"

  case "$arg" in
    -) POSITIONALS[$((POSITIONAL_NUM++))]="$arg";;
    -*);;
    *) POSITIONALS[$((POSITIONAL_NUM++))]="$arg";;
  esac
done'''
        s = s.replace('%LOCALS%', local)

        if len(case_long_options):
            s = s.replace('%CASE_LONG_OPTIONS%', utils.indent('\n'.join(case_long_options), 4))
        else:
            s = s.replace('%CASE_LONG_OPTIONS%\n', '')

        if len(case_short_options):
            s = s.replace('%CASE_SHORT_OPTIONS%', utils.indent('\n'.join(case_short_options), 10))
        else:
            s = s.replace('%CASE_SHORT_OPTIONS%\n', '')

        return s

    def _generate_option_strings_completion(self):
        r  = 'if (( ! END_OF_OPTIONS )) && [[ "$cur" = -* ]]; then\n'
        r += '  local -a POSSIBLE_OPTIONS=()\n'
        for option in self.options:
            option_guard = []

            if not option.multiple_option:
                option_guard += [make_option_variable_name(option)]

            for exclusive_option in option.get_conflicting_options():
                option_guard += [make_option_variable_name(exclusive_option)]

            if option_guard:
                option_guard = '(( %s )) || ' % ' || '.join(option_guard)
            else:
                option_guard = ''

            r += '  %sPOSSIBLE_OPTIONS+=(%s)\n' % (option_guard, ' '.join(shell.escape(o) for o in option.option_strings))
        r += '  %s -a -- "$cur" "${POSSIBLE_OPTIONS[@]}"\n' % self.ctxt.helpers.use('compgen_w_replacement', True)
        r += 'fi'
        return r

    def _generate_option_completion(self):
        class MasterCompletionFunction():
            def __init__(self, name):
                self.name = name
                self.code = []

            def add(self, completion_code, option_strings):
                r  = '%s)\n' % '|'.join(option_strings)
                if completion_code:
                    r += '%s\n' % utils.indent(completion_code, 2)
                r += '  return 0;;'
                self.code.append(r)

            def get(self):
                if self.code:
                    r  = '%s() {\n' % self.name
                    r += '  local option="$1" cur="$2"\n\n'
                    r += '  case "$option" in\n'
                    r += '%s\n' % utils.indent('\n'.join(self.code), 4)
                    r += '  esac\n\n'
                    r += '  return 1\n'
                    r += '}'
                    return r
                else:
                    return '%s() { return 1; }' % self.name

        class CompletionFunction():
            def __init__(self, name):
                self.name = name
                self.code = []

            def add(self, option_strings_in, option_strings_out):
                r  = '%s)\n' % make_switch_case_pattern(option_strings_in)
                r += '  __complete_options %s "$cur" && return 0;;' % option_strings_out[0]
                self.code.append(r)

            def get(self):
                if self.code:
                    r  = '%s() {\n' % self.name
                    r += '  local option="$1" cur="$2"\n\n'
                    r += '  case "$option" in\n'
                    r += '%s\n' % utils.indent('\n'.join(self.code), 4)
                    r += '  esac\n\n'
                    r += '  return 1\n'
                    r += '}'
                    return r
                else:
                    return '%s() { return 1; }' % self.name

        options = self.commandline.get_options(only_with_arguments=True)

        complete_options = MasterCompletionFunction('__complete_options')
        complete_short_with_required_arg = CompletionFunction('__complete_short_with_required_arg')
        complete_short_with_optional_arg = CompletionFunction('__complete_short_with_optional_arg')
        complete_long_with_required_arg = CompletionFunction('__complete_long_with_required_arg')
        complete_long_with_optional_arg = CompletionFunction('__complete_long_with_optional_arg')
        complete_old_with_required_arg = CompletionFunction('__complete_old_with_required_arg')
        complete_old_with_optional_arg = CompletionFunction('__complete_old_with_optional_arg')

        if self.commandline.abbreviate_options:
            # TODO: describe why we use with_parent_options=True here
            # TODO: with_parent_options only if inherit_options is true
            abbreviations = self._get_AbbreviationGeneratorForOptions(
                self.commandline.get_options(with_parent_options=True, only_with_arguments=True))
        else:
            abbreviations = utils.DummyAbbreviationGenerator()

        for option in options:
            short_option_strings = option.get_short_option_strings()
            long_option_strings  = option.get_long_option_strings()
            old_option_strings   = option.get_old_option_strings()
            completion_code      = self._complete_action(option, False)

            complete_options.add(completion_code, option.option_strings)

            if len(short_option_strings):
                if option.takes_args == '?':
                    complete_short_with_optional_arg.add(short_option_strings, short_option_strings)
                else:
                    complete_short_with_required_arg.add(short_option_strings, short_option_strings)

            if len(long_option_strings):
                opts = abbreviations.get_many_abbreviations(long_option_strings)
                if option.takes_args == '?':
                    complete_long_with_optional_arg.add(opts, long_option_strings)
                else:
                    complete_long_with_required_arg.add(opts, long_option_strings)

            if len(old_option_strings):
                opts = abbreviations.get_many_abbreviations(old_option_strings)
                if option.takes_args == '?':
                    complete_old_with_optional_arg.add(opts, old_option_strings)
                else:
                    complete_old_with_required_arg.add(opts, old_option_strings)

        funcs = [
            complete_options,
            complete_short_with_required_arg,
            complete_short_with_optional_arg,
            complete_long_with_required_arg,
            complete_long_with_optional_arg,
            complete_old_with_required_arg,
            complete_old_with_optional_arg
        ]

        r  = '\n\n'.join(f.get() for f in funcs if f.code)
        r += '\n\n'

        if complete_short_with_required_arg.code or complete_short_with_optional_arg.code:
            all_options = utils.flatten(abbreviations.get_many_abbreviations(
                o.get_old_option_strings()) for o in self.commandline.get_options(with_parent_options=True))
            if all_options:
                r += '''\
__is_oldstyle_option() {
  local OLD_OPT
  for OLD_OPT in %s; do [[ "$1" == "$OLD_OPT" ]] && return 0; done
  return 1
}\n\n''' % ' '.join(all_options)
            else:
                r += '__is_oldstyle_option() { return 1; }\n\n'

        G0 = complete_long_with_required_arg.code or \
             complete_old_with_required_arg.code or \
             complete_short_with_required_arg.code

        G1 = complete_long_with_required_arg.code or \
             complete_long_with_optional_arg.code or \
             complete_old_with_required_arg.code or \
             complete_old_with_optional_arg.code or \
             complete_short_with_optional_arg.code or \
             complete_short_with_optional_arg.code

        G2 = complete_short_with_required_arg.code or \
             complete_short_with_optional_arg.code

        OR = complete_old_with_required_arg.code
        OO = complete_old_with_optional_arg.code
        LR = complete_long_with_required_arg.code
        LO = complete_long_with_optional_arg.code
        SR = complete_short_with_required_arg.code
        SO = complete_short_with_optional_arg.code

        code = [
          # CONDITION, TEXT
          (G0, 'case "$prev" in\n'),
          (G0, '  --*)'),
          (LR, '\n    __complete_long_with_required_arg "$prev" "$cur" && return 0'),
          (G0, ';;\n'),
          (G0, '  -*)'),
          (OR, '\n    __complete_old_with_required_arg "$prev" "$cur" && return 0'),
          (SR, '\n    __complete_short_with_required_arg "$prev" "$cur" && return 0'),
          (G0, ';;\n'),
          (G0, 'esac\n'),
          (G0, '\n'),
          (G1, 'case "$cur" in\n'),
          (G1, '  --*=*)'),
          (LR, '\n    __complete_long_with_required_arg "${cur%%=*}" "${cur##*=}" && return 0'),
          (LO, '\n    __complete_long_with_optional_arg "${cur%%=*}" "${cur##*=}" && return 0'),
          (G1, ';;\n'),
          (G1, '  -*=*)'),
          (OR, '\n    __complete_old_with_required_arg "${cur%%=*}" "${cur##*=}" && return 0'),
          (OO, '\n    __complete_old_with_optional_arg "${cur%%=*}" "${cur##*=}" && return 0'),
          (G1, ';;\n'),
          (G1, '  -*)\n'),
          (G2, '    __prefix_compreply() {\n'),
          (G2, '      local I PREFIX="$1"\n'),
          (G2, '      for ((I=0; I < ${#COMPREPLY[@]}; ++I)); do\n'),
          (G2, '        COMPREPLY[$I]="$PREFIX${COMPREPLY[$I]}"\n'),
          (G2, '      done\n'),
          (G2, '    }\n'),
          (G2, '    if ! __is_oldstyle_option "$cur"; then\n'),
          (G2, '      # TODO: check if -* is an oldstyle option without an argument\n'),
          (G2, '      local i\n'),
          (G2, '      for ((i=2; i <= ${#cur}; ++i)); do\n'),
          (G2, '        local option="${cur:0:$i}" value="${cur:$i}"\n'),
          (SR, '        __complete_short_with_required_arg "$option" "$value" && __prefix_compreply "$option" && return 0\n'),
          (SO, '        __complete_short_with_optional_arg "$option" "$value" && __prefix_compreply "$option" && return 0\n'),
          (G2, '      done\n'),
          (G2, '    fi\n'),
          (G1, '    ;;\n'),
          (G1, 'esac')
        ]

        r += ''.join(c[1] for c in code if c[0])

        return r.strip()

    def _generate_positionals_completion(self):
        r  = '# complete positionals\n'
        r += 'case $POSITIONAL_NUM in\n'
        for positional in self.positionals:
            r += '  %d)\n'  % positional.get_positional_num()
            r += '%s;;\n'     % utils.indent(self._complete_action(positional), 4)
        if self.subcommands:
            r += '  %d)\n' % self.subcommands.get_positional_num()
            r += '%s;;\n'    % utils.indent(self._complete_action(self.subcommands), 4)
        r += 'esac'
        return r

    def _generate_subcommand_call(self):
        # This code is used to call subcommand functions

        if self.commandline.abbreviate_commands:
            abbrevs = utils.CommandAbbreviationGenerator(self.subcommands.subcommands.keys())
        else:
            abbrevs = utils.DummyAbbreviationGenerator()

        r  = 'if (( %i < POSITIONAL_NUM )); then\n' % (self.subcommands.get_positional_num() - 1)
        r += '  case "${POSITIONALS[%i]}" in\n' % (self.subcommands.get_positional_num() - 1)
        for name, parser in self.subcommands.subcommands.items():
            pattern = '|'.join([shell.escape(n) for n in abbrevs.get_abbreviations(name)])

            if self.commandline.inherit_options:
                r += '    %s) %s && return 0;;\n' % (pattern, shell.make_completion_funcname(parser))
            else:
                r += '    %s) %s && return 0 || return 1;;\n' % (pattern, shell.make_completion_funcname(parser))
        r += '  esac\n'
        r += 'fi'
        return r

    def _complete_commandline(self):
        # The completion function returns 0 (success) if there was a completion match.
        # This return code is used for dealing with subcommands.

        if not utils.is_worth_a_function(self.commandline):
            r  = '%s() {\n' % shell.make_completion_funcname(self.commandline)
            r += '  return 1\n'
            r += '}'
            self.result = r
            return

        code        = []

        if self.commandline.parent is None:
            # The root parser makes those variables local and sets up the completion.
            r  = 'local cur prev words cword split\n'
            r += '_init_completion -n = || return'
            code += [r]

        # This sets up END_OF_OPTIONS, POSITIONALS, POSITIONAL_NUM and the HAVE_* variables.
        code += [self._generate_options_parsing()]

        if self.subcommands:
            code += [self._generate_subcommand_call()]

        if len(self.options):
            # This code is used to complete arguments of options
            code += [self._generate_option_completion()]

            # This code is used to complete option strings (--foo, ...)
            code += [self._generate_option_strings_completion()]

        if len(self.positionals) or self.subcommands:
            # This code is used to complete positionals
            code += [self._generate_positionals_completion()]

        r  = '%s() {\n' % shell.make_completion_funcname(self.commandline)
        r += '%s\n\n'   % utils.indent('\n\n'.join(c for c in code if c), 2)
        r += '  return 1\n'
        r += '}'

        self.result = r

def generate_completion(commandline, program_name=None, config=None):
    result = shell.CompletionGenerator(BashCompletionGenerator, bash_helpers.BASH_Helpers, commandline, program_name, config)
    commandline = result.result[0].commandline

    output  = [generation_notice.GENERATION_NOTICE]
    output += result.include_files_content
    output += result.ctxt.helpers.get_code()
    output += [r.result for r in result.result]
    output += ['complete -F %s %s' % (shell.make_completion_funcname(commandline), commandline.prog)]
    if config.vim_modeline:
        output += [modeline.get_vim_modeline('sh')]

    return '\n\n'.join(output)
