#!/usr/bin/python3

import subprocess

from . import shell, utils
from . import helpers, fish_helpers
from . import modeline
from . import generation_notice

def get_completions_file(program_name):
    command = ['pkg-config', '--variable=completionsdir', 'fish']
    try:
        # throws FileNotFoundError if command is not available
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception('returncode != 0')
        dir = result.stdout.strip()
    except:
        utils.warn('%s failed' % ' '.join(command))
        dir = '/usr/share/fish/vendor_completions.d'

    return '%s/%s.fish' % (dir, program_name)

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
        return ['-f', '-a', shell.escape('(%s)' % self.command)]

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

        return FishCompletionFromArgs(['-f', '-a', shell.escape(' '.join(shell.escape(str(c)) for c in choices))])

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

    def variable(self, ctxt):
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

# =============================================================================
# Helper function for creating a `complete` command in fish
# =============================================================================

class VariableManager:
    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.value_to_variable  = {}
        self.counter = 0

    def add(self, value):
        if value in self.value_to_variable:
            return '$%s' % self.value_to_variable[value]

        var = '%s%03d' % (self.variable_name, self.counter)
        self.value_to_variable[value] = var
        self.counter += 1
        return '$%s' % var

    def get_lines(self):
        r = []
        for value, variable in self.value_to_variable.items():
            r.append('set -l %s %s' % (variable, value))
        return r

class FishCompleteCommand:
    def __init__(self, command=None):
        self.command       = command
        self.short_options = []
        self.long_options  = []
        self.old_options   = []
        self.condition     = None
        self.description   = None
        self.flags         = set()
        self.arguments     = None

    def set_command(self, command):
        self.command = command

    def set_short_options(self, opts):
        self.short_options = opts

    def set_long_options(self, opts):
        self.long_options = opts

    def set_old_options(self, opts):
        self.old_options = opts

    def set_condition(self, condition):
        self.condition = condition

    def set_flags(self, flags):
        self.flags = flags

    def set_arguments(self, arguments):
        self.arguments = arguments

    def parse_args(self, args):
        while len(args):
            arg = args.pop(0)
            if   arg == '-f': self.flags.add('f')
            elif arg == '-F': self.flags.add('F')
            elif arg == '-a': self.arguments = args.pop(0)
            else:             raise Exception(arg)

    def get(self):
        r = ['complete']

        if self.command is not None:
            r.extend(['-c', self.command])

        if self.condition is not None:
            r.extend(['-n', self.condition])

        for o in sorted(self.short_options):
            r.extend(['-s %s' % shell.escape(o.lstrip('-'))])

        for o in sorted(self.long_options):
            r.extend(['-l %s' % shell.escape(o.lstrip('-'))])

        for o in sorted(self.old_options):
            r.extend(['-o %s' % shell.escape(o.lstrip('-'))])

        if self.description is not None:
            r.extend(['-d', self.description])

        # -r -f is the same as -x
        if 'r' in self.flags and 'f' in self.flags:
            self.flags.add('x')

        # -x implies -r -f
        if 'x' in self.flags:
            self.flags.discard('r')
            self.flags.discard('f')

        if len(self.flags):
            r += ['-%s' % ''.join(self.flags)]

        if self.arguments is not None:
            r.extend(['-a', self.arguments])

        return ' '.join(r)

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
            if True: # TODO
                if cmd.condition is not None:
                    cmd.condition = self.conditions.add(cmd.condition)

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
                abbrev = utils.CommandAbbreviationGenerator(cmdline.parent.get_subcommands_option().subcommands.keys())
            else:
                abbrev = utils.DummyAbbreviationGenerator()

            r[cmdline.parent.get_subcommands_option().get_positional_num()] = abbrev.get_abbreviations(cmdline.prog)

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

        cmd = FishCompleteCommand('$prog')
        conditions = []

        if requires_argument:
            cmd.flags.add('r')

        if len(positional_contains):
            for num, words in positional_contains.items():
                guard = "$helper '$options' positional_contains %d %s" % (num, ' '.join(words))
                conditions += [guard]

        if len(conflicting_options):
            guard = "not $helper '$options' has_option %s" % ' '.join(conflicting_options)
            conditions += [guard]

        if positional is not None:
            if repeatable:
                guard = "$helper '$options' num_of_positionals -ge %d" % (positional - 1)
            else:
                guard = "$helper '$options' num_of_positionals -eq %d" % (positional - 1)
            conditions += [guard]

        if when is not None:
            guard = "$helper '$options' %s" % when
            conditions += [guard]

        if len(conditions):
            conditions = ' && '.join(conditions)
            cmd.condition = '"%s"' % conditions

        cmd.short_options = short_options
        cmd.long_options = long_options
        cmd.old_options = old_options

        if description:
            cmd.description = shell.escape(description)

        cmd.parse_args(completion_args)

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
        items = dict()
        for subcommand in option.subcommands:
            items[subcommand.prog] = subcommand.help

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
    result.ctxt.helpers.use_function('fish_helper')

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
    output.append('set -l helper "%s"' % result.ctxt.helpers.use_function('fish_helper'))

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
