#!/usr/bin/python3

from collections import namedtuple
import subprocess

from . import shell, utils
from . import helpers, fish_helpers
from . import modeline
from . import generation_notice
from .fish_utils import *

def get_completions_file(program_name):
    command = ['pkg-config', '--variable=completionsdir', 'fish']
    directory = '/usr/share/fish/vendor_completions.d'
    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            directory = result.stdout.strip()
        else:
            utils.warn('%s failed: %s' % (' '.join(command), result.stderr.strip()))
    except FileNotFoundError:
        utils.warn('program `pkg-config` not found')

    return '%s/%s.fish' % (directory, program_name)

class FishCompletionBase():
    def get_args(self):
        raise NotImplementedError

class FishCompletionFromArgs(FishCompletionBase):
    def __init__(self, args):
        self.args = args

    def get_args(self):
        return self.args

class FishCompletionCommand(FishCompletionBase):
    def  __init__(self, command):
        self.command = command

    def get_args(self):
        return ['-f', '-a', '(%s)' % self.command]

class FishCompleter(shell.ShellCompleter):
    def none(self, ctxt):
        return FishCompletionFromArgs(['-f'])

    def choices(self, ctxt, choices):
        if hasattr(choices, 'items'):
            funcname = shell.make_completion_funcname_for_context(ctxt)
            code = 'printf "%s\\t%s\\n" \\\n'
            for item, description in choices.items():
                code += '  %s %s \\\n' % (shell.escape(str(item)), shell.escape(str(description)))
            code = code.rstrip(' \\\n')

            ctxt.helpers.add_function(helpers.FishFunction(funcname, code))
            funcname = ctxt.helpers.use_function(funcname)
            return FishCompletionCommand(funcname)

        return FishCompletionFromArgs(['-f', '-a', ' '.join(shell.escape(str(c)) for c in choices)])

    def command(self, ctxt):
        return FishCompletionCommand("__fish_complete_command")

    def directory(self, ctxt, opts={}):
        directory = opts.get('directory', None)
        if directory:
            funcname = ctxt.helpers.use_function('fish_complete_filedir')
            return FishCompletionCommand('%s -D -C %s' % (funcname, shell.escape(directory)))
        return FishCompletionCommand("__fish_complete_directories")

    def file(self, ctxt, opts={}):
        directory = opts.get('directory', None)
        if directory:
            funcname = ctxt.helpers.use_function('fish_complete_filedir')
            return FishCompletionCommand('%s -C %s' % (funcname, shell.escape(directory)))
        return FishCompletionFromArgs(['-F'])

    def group(self, ctxt):
        return FishCompletionCommand("__fish_complete_groups")

    def hostname(self, ctxt):
        return FishCompletionCommand("__fish_print_hostnames")

    def pid(self, ctxt):
        return FishCompletionCommand("__fish_complete_pids")

    def process(self, ctxt):
        return FishCompletionCommand("__fish_complete_proc")

    def range(self, ctxt, start, stop, step=1):
        if step == 1:
            return FishCompletionCommand(f"seq {start} {stop}")
        else:
            return FishCompletionCommand(f"seq {start} {step} {stop}")

    def service(self, ctxt):
        return FishCompletionCommand("__fish_systemctl_services")

    def user(self, ctxt):
        return FishCompletionCommand("__fish_complete_users")

    def variable(self, ctxt, option=None):
        if option == '-x':
            return FishCompletionCommand("set -n -x")
        else:
            return FishCompletionCommand("set -n")

    def exec(self, ctxt, command):
        return FishCompletionCommand(command)

    def value_list(self, ctxt, opts):
        separator = opts.get('separator', ',')

        funcname = shell.make_completion_funcname_for_context(ctxt)
        code = 'printf "%s\\n" \\\n'
        for value in opts['values']:
            code += '  %s \\\n' % shell.escape(str(value))
        code = code.rstrip(' \\\n')

        ctxt.helpers.add_function(helpers.FishFunction(funcname, code))
        funcname = ctxt.helpers.use_function(funcname)

        cmd = '__fish_complete_list %s %s' % (shell.escape(separator), funcname)
        return FishCompletionCommand(cmd)

class Conditions:
    NumOfPositionals = namedtuple('NumOfPositionals', ['operator', 'value'])

    def __init__(self):
        self.positional_contains = dict()
        self.not_has_option = list()
        self.num_of_positionals = None

    def get(self, unsafe=False):
        conditions = []

        for num, words in self.positional_contains.items():
            if unsafe:
                guard = "__fish_seen_subcommand_from %s" % (' '.join(words))
            else:
                guard = "$helper '$options' positional_contains %d %s" % (num, ' '.join(words))
            conditions += [guard]

        if len(self.not_has_option):
            use_helper = False
            if unsafe:
                guard = "__fish_not_contain_opt"
                for opt in self.not_has_option:
                    if opt.startswith('--'):
                        guard += ' %s' % opt.lstrip('-')
                    elif opt.startswith('-') and len(opt) == 2:
                        guard += ' -s %s' % opt[1]
                    else:
                        # __fish_not_contain_opt does not support oldoptions
                        use_helper = True
            else:
                use_helper = True

            if use_helper:
                guard = "not $helper '$options' has_option %s" % ' '.join(self.not_has_option)
            conditions += [guard]

        if self.num_of_positionals is not None:
            if unsafe:
                guard = "test (__fish_number_of_cmd_args_wo_opts) %s %d" % (
                    self.num_of_positionals.operator, self.num_of_positionals.value) # TODO - 1)
            else:
                guard = "$helper '$options' num_of_positionals %s %d" % (
                    self.num_of_positionals.operator, self.num_of_positionals.value - 1)
            conditions += [guard]

        if self.when is not None:
            guard = "$helper '$options' %s" % self.when
            conditions += [guard]

        if not conditions:
            return None

        return '"%s"' % ' && '.join(conditions)

class FishCompletionGenerator:
    def __init__(self, ctxt, commandline):
        self.commandline = commandline
        self.ctxt = ctxt
        self.completer = FishCompleter()
        self.lines = []
        self.conditions = VariableManager('guard')
        self.command_comment = '# command %s' % ' '.join(p.prog for p in self.commandline.get_parents(include_self=True))
        self.options_for_helper = 'set -l options "%s"' % self._get_option_strings_for_helper()

        complete_cmds = []
        for option in self.commandline.get_options():
            complete_cmds.append(self.complete_option(option))

        for positional in self.commandline.get_positionals():
            complete_cmds.append(self.complete_positional(positional))

        if self.commandline.get_subcommands_option():
            complete_cmds.append(self.complete_subcommands(self.commandline.get_subcommands_option()))

        for cmd in complete_cmds:
            if cmd.condition is not None and '$helper' in cmd.condition.s:
                self.ctxt.helpers.use_function('fish_helper')

            if not self.ctxt.config.fish_inline_conditions:
                if cmd.condition is not None:
                    cmd.set_condition(self.conditions.add(cmd.condition.s), raw=True)

            self.lines.append(cmd.get())

    def _get_option_strings_for_helper(self):
        r = []
        for option in self.commandline.get_options(with_parent_options=True):
            if option.takes_args == '?':
                r.extend('%s=?' % s for s in option.option_strings)
            elif option.takes_args:
                r.extend('%s=' % s for s in option.option_strings)
            else:
                r.extend(option.option_strings)
        return ','.join(r)

    def _get_positional_contains(self, option):
        cmdlines = option.parent.get_parents(include_self=True)
        del cmdlines[0]

        r = dict()

        for cmdline in cmdlines:
            if self.commandline.abbreviate_commands:
                abbrev = utils.CommandAbbreviationGenerator(
                    cmdline.parent.get_subcommands_option().get_all_subcommands(with_aliases=False))
            else:
                abbrev = utils.DummyAbbreviationGenerator()

            cmds = abbrev.get_abbreviations(cmdline.prog)
            for alias in cmdline.aliases:
                cmds.append(alias)

            r[cmdline.parent.get_subcommands_option().get_positional_num()] = cmds

        return r

    def make_complete(
          self,
          short_options=[],           # List of short options
          long_options=[],            # List of long options
          old_options=[],             # List of old-style options
          positional_contains=dict(), # Only show if these words are given on commandline
          conflicting_options=[],     # Only show if these options are not given on commandline
          description=None,           # Description
          positional=None,            # Only show if current word number is `positional`
          repeatable=False,           # Positional is repeatable
          requires_argument=False,    # Option requires an argument
          when=None,
          completion_args=None
        ):
        cmd = FishCompleteCommand()
        cmd.set_command('$prog', raw=True)
        cmd.add_short_options(short_options)
        cmd.add_long_options(long_options)
        cmd.add_old_options(old_options)

        if description:
            cmd.set_description(description)

        if requires_argument:
            cmd.flags.add('r')

        cmd.parse_args(completion_args)

        conds = Conditions()
        conds.positional_contains = positional_contains
        conds.not_has_option = conflicting_options
        conds.when = when

        if positional is not None:
            operator = '-eq'
            if repeatable:
                operator = '-ge'
            conds.num_of_positionals = Conditions.NumOfPositionals(operator, positional) # -1 TODO

        cmd.set_condition(conds.get(unsafe=self.ctxt.config.fish_fast), raw=True)

        return cmd

    def complete_option(self, option):
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, *option.complete).get_args()

        conflicting_options = option.get_conflicting_option_strings()
        if not option.multiple_option:
            conflicting_options.extend(option.option_strings)

        # TODO: fix or at least explain this...
        if not self.commandline.inherit_options and self.commandline.get_subcommands_option():
            positional = self.commandline.get_subcommands_option().get_positional_num()
        else:
            positional = None

        return self.make_complete(
            requires_argument   = (option.takes_args is True),
            description         = option.help,
            positional          = positional,
            positional_contains = self._get_positional_contains(option),
            short_options       = option.get_short_option_strings(),
            long_options        = option.get_long_option_strings(),
            old_options         = option.get_old_option_strings(),
            conflicting_options = conflicting_options,
            when                = option.when,
            completion_args     = completion_args
        )

    def complete_positional(self, option):
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, *option.complete).get_args()

        return self.make_complete(
            requires_argument   = True,
            description         = option.help,
            positional_contains = self._get_positional_contains(option),
            positional          = option.get_positional_num(),
            repeatable          = option.repeatable,
            when                = option.when,
            completion_args     = completion_args
        )

    def complete_subcommands(self, option):
        items = option.get_all_subcommands()
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, 'choices', items).get_args()

        return self.make_complete(
            description    = 'Commands',
            positional_contains = self._get_positional_contains(option),
            positional     = option.get_positional_num(),
            completion_args = completion_args,
        )

def generate_completion(commandline, program_name=None, config=None):
    result = shell.CompletionGenerator(FishCompletionGenerator, fish_helpers.FISH_Helpers, commandline, program_name, config)

    output = []

    output.append(generation_notice.GENERATION_NOTICE)
    output.append('')

    for code in result.include_files_content:
        output.append(code)
        output.append('')

    for code in result.ctxt.helpers.get_used_functions_code():
        output.append(code)
        output.append('')

    output.append('set -l prog "%s"'   % result.result[0].commandline.prog)
    if result.ctxt.helpers.is_used('fish_helper'):
        output.append('set -l helper "%s"' % result.ctxt.helpers.use_function('fish_helper'))

    output.append('')
    output.append('# Generally disable file completion')
    output.append('complete -c $prog -x')

    for generator in result.result:
        output.append('')
        output.append(generator.command_comment)
        output.append(generator.options_for_helper)
        output.extend(generator.conditions.get_lines())
        output.extend(generator.lines)

    if config.vim_modeline:
        output += ['']
        output += [modeline.get_vim_modeline('fish')]

    return '\n'.join(output)
