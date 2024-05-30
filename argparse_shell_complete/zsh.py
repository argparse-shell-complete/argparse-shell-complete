#!/usr/bin/python3

from . import shell, utils
from . import commandline as _commandline
from . import config as _config
from . import zsh_helpers, helpers
from . import modeline

def get_completions_file(program_name):
    dir='/usr/share/zsh/site-functions'
    return '%s/_%s' % (dir, program_name)

class ZshCompleter(shell.ShellCompleter):
    def none(self, ctxt, *a):
        return "' '"

    def choices(self, ctxt, choices):
        if hasattr(choices, 'items'):
            # TODO: escape value and description
            funcname = '%s_%s' % (shell.make_completion_funcname(ctxt.commandline), ctxt.option.option_strings[0])
            code  = 'local -a DESCRIBE=(\n'
            for item, description in choices.items():
                code += '  %s:%s\n' % (shell.escape(escape_colon(str(item))), shell.escape(str(description)))
            code += ')\n\n'
            code += '_describe -- %s DESCRIBE' % shell.escape(ctxt.option.option_strings[0])

            ctxt.helpers.add_function(helpers.ShellFunction(funcname, code))
            funcname = ctxt.helpers.use(funcname)
            return funcname
        else:
            return shell.escape("(%s)" % (' '.join(shell.escape(str(c)) for c in choices)))

    def command(self, ctxt):
        return '_command_names'

    def directory(self, ctxt, opts={}):
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

        if directory:
            return '"_directories -W %s"' % directory
        return '_directories'

    def file(self, ctxt, opts={}):
        directory = None
        for name, value in opts.items():
            if name == 'directory':
                directory = value
            else:
                raise Exception('Unknown option: %s' % name)

        if directory:
            return '"_files -W %s"' % directory
        return '_files'

    def group(self, ctxt):
        return '_groups'

    def hostname(self, ctxt):
        return '_hosts'

    def pid(self, ctxt):
        return '_pids'

    def process(self, ctxt):
        return '"_process_names -a"'

    def range(self, ctxt, start, stop, step=1):
        if step == 1:
            return f"'({{{start}..{stop}}})'"
        else:
            return f"'({{{start}..{stop}..{step}}})'"

    def user(self, ctxt):
        return '_users'

    def variable(self, ctxt):
        return '_vars'

    def exec(self, ctxt, command):
        funcname = ctxt.helpers.use('exec', True)
        return shell.escape('{%s %s}' % (funcname, shell.escape(command)))

def escape_colon(s):
    return s.replace(':', '\\:')

def escape_square_brackets(s):
    return s.replace('[', '\\[').replace(']', '\\]')

def make_argument_option_spec(
        option_strings,
        conflicting_options = [],
        description = '',
        takes_args = False,
        multiple_option = False,
        metavar = '',
        action = ''
    ):
    # Any literal colon in an optname, message, or action must be preceded by a backslash, `\:'.
    conflicting_options = [escape_colon(s) for s in sorted(conflicting_options)]
    option_strings      = [escape_colon(s) for s in sorted(option_strings)]
    description         = '[%s]' % escape_colon(escape_square_brackets(description)) if description else ''
    metavar             = escape_colon(metavar)

    conflicting_options += option_strings

    if len(conflicting_options) > 1:
        conflicting_options = shell.escape("(%s)" % ' '.join(s for s in conflicting_options))
    else:
        conflicting_options = ''

    if takes_args == '?':
        option_strings = [o+'-' if len(o) == 2 else o+'=-' for o in option_strings]
    elif takes_args:
        option_strings = [o+'+' if len(o) == 2 else o+'=' for o in option_strings]

    if len(option_strings) == 1:
        option_strings = option_strings[0]
    else:
        option_strings = '{%s}' % ','.join(option_strings)

    description = shell.escape(description, escape_empty_string=False)
    metavar = shell.escape(metavar, escape_empty_string=False)
    multiple_option = "'*'" if multiple_option else ''

    # '(--option -o)'{--option=,-o+}'[Option description]':Metavar:'action'
    return f'{conflicting_options}{multiple_option}{option_strings}{description}:{metavar}:{action}'

class ZshCompletionGenerator():
    def __init__(self, ctxt, commandline):
        self.commandline = commandline
        self.ctxt = ctxt
        self.funcname = shell.make_completion_funcname(commandline)
        self.subcommands = commandline.get_subcommands_option()
        self.command_counter = 0
        self.completer = ZshCompleter()
        self._generate_completion_function()

    def _get_option_strings(self):
        r = []
        for o in self.commandline.get_options(with_parent_options=True):
            if o.takes_args == '?':
                r.extend('%s=?' % s for s in o.option_strings)
            elif o.takes_args:
                r.extend('%s=' % s for s in o.option_strings)
            else:
                r.extend('%s' % s for s in o.option_strings)
        return ','.join(r)

    def complete(self, option, command, *args):
        context = self.ctxt.getOptionGenerationContext(self.commandline, option)
        return self.completer.complete(context, command, *args)

    def complete_option(self, option):
        return make_argument_option_spec(
            option.option_strings,
            conflicting_options = option.get_conflicting_option_strings(),
            description = option.help,
            takes_args = option.takes_args,
            multiple_option = option.multiple_option,
            metavar = option.metavar,
            action = self.complete(option, *option.complete)
        )

    def complete_subcommands(self, option):
        choices = {}
        for name, subcommand in option.subcommands.items():
            choices[name] = subcommand.help
        self.command_counter += 1
        return "%d:command%d:%s" % (
            option.get_positional_num(),
            self.command_counter,
            self.complete(option, 'choices', choices)
        )

    def complete_positional(self, option):
        return "%d:%s:%s" % (
            option.get_positional_num(),
            shell.escape(escape_colon(option.help)) if option.help else "' '",
            self.complete(option, *option.complete)
        )

    def _generate_completion_function(self):
        args = []

        r = '%s() {\n' % self.funcname

        if self.subcommands:
            if self.commandline.abbreviate_commands:
                abbrevs = utils.CommandAbbreviationGenerator(self.subcommands.subcommands.keys())
            else:
                abbrevs = utils.DummyAbbreviationGenerator()

            get_positional_func = self.ctxt.helpers.use('get_positional', True)
            r += '  # We have to check for subcommands here, because _arguments modifies $words\n'
            r += '  local opts="%s"\n' % self._get_option_strings()
            r += '  case "$(%s "$opts" %d "${words[@]}")" in\n' % (get_positional_func, self.subcommands.get_positional_num())
            for name, subcommand in self.subcommands.subcommands.items():
                sub_funcname = shell.make_completion_funcname(subcommand)
                pattern = '|'.join(abbrevs.get_abbreviations(name))
                r += f'    ({pattern}) {sub_funcname}; return $?;;\n'
            r += '  esac\n\n'

        if self.commandline.inherit_options:
            options = self.commandline.get_options(with_parent_options=True)
        else:
            options = self.commandline.get_options()

        for option in options:
            args.append(self.complete_option(option))

        # TODO: describe why we need this
        for cmdline in self.commandline.get_parents():
            for option in cmdline.get_positionals():
                args.append(self.complete_positional(option))

            if cmdline.get_subcommands_option():
                args.append(self.complete_subcommands(cmdline.get_subcommands_option()))

        for option in self.commandline.get_positionals():
            args.append(self.complete_positional(option))

        if self.subcommands:
            args.append(self.complete_subcommands(self.subcommands))
            #args.append("'*::arg:->args'")

        if len(args):
            # TODO: add -s to _arguments
            r += '  local -a arguments=(\n'
            r += '%s\n' % utils.indent('\n'.join(args), 4)
            r += '  )\n'
            r += '\n'
            r += '  _arguments -S "${arguments[@]}"\n'

        r += '}'

        self.result = r

def generate_completion(commandline, program_name=None, config=None):
    result = shell.CompletionGenerator(ZshCompletionGenerator, zsh_helpers.ZSH_Helpers, commandline, program_name, config)
    functions = result.result

    output = ['#compdef %s' % functions[0].commandline.prog]

    output.extend(result.include_files_content)

    for code in result.ctxt.helpers.get_code():
        output.append(code)

    output += [r.result for r in functions]
    output += ['%s "$@"' % functions[0].funcname]

    if config.vim_modeline:
        output += [modeline.get_vim_modeline('zsh')]

    return '\n\n'.join(output)
