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
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

        if directory:
            funcname = ctxt.helpers.use_function('fish_complete_filedir')
            return FishCompletionCommand('%s -D -C %s' % (funcname, shell.escape(directory)))
        return FishCompletionCommand("__fish_complete_directories")

    def file(self, ctxt, opts={}):
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

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

class Conditions:
    def __init__(self):
        self.condition_to_guard = {}
        self.counter = 0

    def add(self, condition):
        if condition in self.condition_to_guard:
            return '$%s' % self.condition_to_guard[condition]

        condition_guard = 'guard%03d' % self.counter
        self.condition_to_guard[condition] = condition_guard
        self.counter += 1
        return '$%s' % condition_guard

    def get_lines(self):
        r = []
        for condition, guard in self.condition_to_guard.items():
            r.append('set -l %s "%s"' % (guard, condition))
        return r

class FishCompletionGenerator:
    def __init__(self, ctxt, commandline):
        self.commandline = commandline
        self.ctxt = ctxt
        self.completer = FishCompleter()
        self.lines = []
        self.conditions = Conditions()
        self.command_comment = '# command %s' % ' '.join(p.prog for p in self.commandline.get_parents(include_self=True))
        self.options_for_helper = 'set -l options "%s"' % self._get_option_strings_for_helper()

        for option in self.commandline.get_options():
            self.complete_option(option)

        for positional in self.commandline.get_positionals():
            self.complete_positional(positional)

        if self.commandline.get_subcommands_option():
            self.complete_subcommands(self.commandline.get_subcommands_option())

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
          requires_argument=False,    # Option requires an argument
          no_files=False,             # Don't use file completion
          choices=[],                 # Add those words for completion
          flags=set(),                # Add those flags (without leading dash)
          when=None
        ):

        r = []
        conditions = []
        flags = set(flags)

        if no_files:
            flags.add('f')

        if requires_argument:
            flags.add('r')

        if len(positional_contains):
            for num, words in positional_contains.items():
                guard = "$helper '$options' positional_contains %d %s" % (num, ' '.join(words))
                conditions += [guard]

        if len(conflicting_options):
            guard = "not $helper '$options' has_option %s" % ' '.join(conflicting_options)
            conditions += [guard]

        if positional is not None:
            guard = "$helper '$options' num_of_positionals -eq %d" % (positional - 1)
            conditions += [guard]

        if when is not None:
            guard = "$helper '$options' %s" % when
            conditions += [guard]

        if len(conditions):
            conditions = ' && '.join(conditions)

            if False: # TODO...
                r += ["-n %s" % shell.escape(conditions)]
            else:
                r += ["-n %s" % self.conditions.add(conditions)]

        for o in sorted(short_options):
            r += ['-s %s' % shell.escape(o.lstrip('-'))]

        for o in sorted(long_options):
            r += ['-l %s' % shell.escape(o.lstrip('-'))]

        for o in sorted(old_options):
            r += ['-o %s' % shell.escape(o.lstrip('-'))]

        if description:
            r += ['-d %s' % shell.escape(description)]

        for s in choices:
            r += ['-a %s' % shell.escape(s)]

        # -r -f is the same as -x
        if 'r' in flags and 'f' in flags:
            flags.add('x')

        # -x implies -r -f
        if 'x' in flags:
            flags.discard('r')
            flags.discard('f')

        if len(flags):
            r += ['-%s' % ''.join(flags)]

        return ('complete -c $prog %s' % ' '.join(r)).rstrip()

    def complete_option(self, option):
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, *option.complete).get_args()

        flags = set() # Drop '-f' and add it to flags
        if len(completion_args) and completion_args[0] == '-f':
            flags.add('f')
            completion_args.pop(0)

        conflicting_options = option.get_conflicting_option_strings()
        if not option.multiple_option:
            conflicting_options.extend(option.option_strings)

        # TODO: fix or at least explain this...
        if not self.commandline.inherit_options and self.commandline.get_subcommands_option():
            positional = self.commandline.get_subcommands_option().get_positional_num()
        else:
            positional = None

        r = self.make_complete(
            requires_argument   = (option.takes_args is True),
            description         = option.help,
            positional          = positional,
            positional_contains = self._get_positional_contains(option),
            short_options       = option.get_short_option_strings(),
            long_options        = option.get_long_option_strings(),
            old_options         = option.get_old_option_strings(),
            conflicting_options = conflicting_options,
            flags               = flags,
            when                = option.when
        )

        r = ('%s %s' % (r, ' '.join(completion_args))).rstrip()
        self.lines.append(r)

    def complete_positional(self, option):
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, *option.complete).get_args()

        flags = set() # Drop '-f' and add it to flags
        if len(completion_args) and completion_args[0] == '-f':
            flags.add('f')
            del completion_args[0]

        r = self.make_complete(
            requires_argument   = option.takes_args,
            description         = option.help,
            positional_contains = self._get_positional_contains(option),
            positional          = option.get_positional_num(),
            flags               = flags,
            when                = option.when
        )

        r = ('%s %s' % (r, ' '.join(completion_args))).rstrip()
        self.lines.append(r)

    def complete_subcommands(self, option):
        items = dict()
        for name, subcommand in option.subcommands.items():
            items[name] = subcommand.help

        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        completion_args = self.completer.complete(context, 'choices', items).get_args()

        flags = set() # Drop '-f' and add it to flags
        if len(completion_args) and completion_args[0] == '-f':
            flags.add('f')
            del completion_args[0]

        r = self.make_complete(
            no_files       = True,
            description    = 'Commands',
            positional_contains = self._get_positional_contains(option),
            positional     = option.get_positional_num(),
            flags          = flags
        )
        r = ('%s %s' % (r, ' '.join(completion_args))).rstrip()
        self.lines.append(r)

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
