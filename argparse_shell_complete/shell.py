#!/usr/bin/python3

import sys, re, argparse, collections

from . import commandline as _commandline

def make_identifier(string):
    '''
    Make `string` a valid shell identifier.

    This function replaces any dashes '-' with underscores '_',
    removes any characters that are not letters, digits, or underscores,
    and ensures that consecutive underscores are replaced with a single underscore.

    Args:
        string (str): The input string to be converted into a valid shell identifier.

    Returns:
        str: The modified string that is a valid shell identifier.
    '''
    assert isinstance(string, str), "make_identifier: string: expected str, got %r" % string

    string = string.replace('-', '_')
    string = re.sub('[^a-zA-Z0-9_]', '', string)
    string = re.sub('_+', '_', string)
    if string[0] in '0123456789':
        return '_' + string
    return string

def escape(string, escape_empty_string=True):
    '''
    Escapes special characters in a string for safe usage in shell commands or scripts.

    Args:
        string (str): The input string to be escaped.
        escape_empty_string (bool, optional): Determines whether to escape an empty string or not.
            Defaults to True.

    Returns:
        str: The escaped string.
    '''
    assert isinstance(string, str), "escape: s: expected str, got %r" % string

    if not string and escape_empty_string is False:
        return ''

    if re.fullmatch('[a-zA-Z0-9_@%+=:,./-]+', string):
        return string

    if "'" not in string:
        return "'%s'" % string

    if '"' not in string:
        return '"%s"' % string.replace('\\', '\\\\').replace('$', '\\$').replace('`', '\\`')

    return "'%s'" % string.replace("'", '\'"\'"\'')

def make_completion_funcname(cmdline, prefix='_', suffix=''):
    '''
    Generates a function name for auto-completing a program or subcommand.

    Args:
        cmdline (CommandLine): The CommandLine instance representing the program or subcommand.

    Returns:
        str: The generated function name for auto-completion.

    This function is used to generate a unique function name for auto-completing
    a program or subcommand in the specified shell. It concatenates the names of
    all parent commandlines, including the current commandline, and converts them
    into a valid function name format.

    Example:
        For a program with the name 'my_program' and a subcommand with the name 'subcommand',
        the generated function name is '_my_program_subcommand'.
    '''
    assert isinstance(cmdline, _commandline.CommandLine), "make_completion_funcname: cmdline: expected CommandLine, got %r" % cmdline

    commandlines = cmdline.get_parents(include_self=True)

    r = '%s%s%s' % (
        prefix,
        make_identifier('_'.join(p.prog for p in commandlines)),
        suffix
    )

    return r

class ShellCompleter():
    # TODO: this is actually a mess

    def complete(self, ctxt, completion, *a):
        if not hasattr(self, completion):
            print("Warning: ShellCompleter: Falling back from `%s` to `none`" % (completion,), file=sys.stderr)
            completion = 'none'

        return getattr(self, completion)(ctxt, *a)

    def fallback(self, ctxt, from_, to, *a):
        print("Warning: ShellCompleter: Falling back from `%s` to `%s`" % (from_, to), file=sys.stderr)
        return self.complete(ctxt, to, *a)

    def none(self, ctxt, *a):
        return ''

    def signal(self, ctxt, prefix=''):
        SIG = prefix
        signals = collections.OrderedDict([
            (SIG+'ABRT',   'Process abort signal'),
            (SIG+'ALRM',   'Alarm clock'),
            (SIG+'BUS',    'Access to an undefined portion of a memory object'),
            (SIG+'CHLD',   'Child process terminated, stopped, or continued'),
            (SIG+'CONT',   'Continue executing, if stopped'),
            (SIG+'FPE',    'Erroneous arithmetic operation'),
            (SIG+'HUP',    'Hangup'),
            (SIG+'ILL',    'Illegal instruction'),
            (SIG+'INT',    'Terminal interrupt signal'),
            (SIG+'KILL',   'Kill (cannot be caught or ignored)'),
            (SIG+'PIPE',   'Write on a pipe with no one to read it'),
            (SIG+'QUIT',   'Terminal quit signal'),
            (SIG+'SEGV',   'Invalid memory reference'),
            (SIG+'STOP',   'Stop executing (cannot be caught or ignored)'),
            (SIG+'TERM',   'Termination signal'),
            (SIG+'TSTP',   'Terminal stop signal'),
            (SIG+'TTIN',   'Background process attempting read'),
            (SIG+'TTOU',   'Background process attempting write'),
            (SIG+'USR1',   'User-defined signal 1'),
            (SIG+'USR2',   'User-defined signal 2'),
            (SIG+'POLL',   'Pollable event'),
            (SIG+'PROF',   'Profiling timer expired'),
            (SIG+'SYS',    'Bad system call'),
            (SIG+'TRAP',   'Trace/breakpoint trap'),
            (SIG+'XFSZ',   'File size limit exceeded'),
            (SIG+'VTALRM', 'Virtual timer expired'),
            (SIG+'XCPU',   'CPU time limit exceeded'),
        ])

        return self.complete(ctxt, 'choices', signals)

    def range(self, ctxt, _range):
        # TODO!!!!!!
        l = list(_range)

        if len(l) > 32:
            l = l[0:16] + ['...'] + l[-32:]

        return self.complete('choices', l)

    def directory(self, ctxt, opts):
        return self.fallback(ctxt, 'directory', 'file', opts)

    def process(self, ctxt):
        return self.fallback(ctxt, 'process', 'none')

    def pid(self, ctxt):
        return self.fallback(ctxt, 'pid', 'none')

    def command(self, ctxt):
        return self.fallback(ctxt, 'command', 'file')

    def variable(self, ctxt):
        return self.fallback(ctxt, 'variable', 'none')

    def service(self, ctxt):
        return self.fallback(ctxt, 'service', 'none')

    def user(self, ctxt):
        return self.fallback(ctxt, 'user', 'none')

    def group(self, ctxt):
        return self.fallback(ctxt, 'group', 'none')

class GenerationContext():
    def __init__(self, config, helpers):
        self.config = config
        self.helpers = helpers

    def getOptionGenerationContext(self, commandline, option):
        return OptionGenerationContext(
            self.config,
            self.helpers,
            commandline,
            option
        )

class OptionGenerationContext(GenerationContext):
    def __init__(self, config, helpers, commandline, option):
        super().__init__(config, helpers)
        self.commandline = commandline
        self.option = option

class CompletionGenerator():
    def __init__(self, completion_klass, helpers_klass, commandline, program_name, config):
        commandline = commandline.copy()

        if program_name is not None:
            commandline.prog = program_name

        if config is None:
            config = _config.Config()

        _commandline.CommandLine_Apply_Config(commandline, config)

        self.include_files_content = []
        for file in config.include_files:
            with open(file, 'r') as fh:
                self.include_files_content.append(fh.read().strip())

        self.completion_klass = completion_klass
        self.ctxt = GenerationContext(config, helpers_klass(commandline.prog))
        self.result = []
        self._call_generator(commandline)

    def _call_generator(self, commandline):
        self.result.append(self.completion_klass(self.ctxt, commandline))

        if commandline.get_subcommands_option():
            for subcommand in commandline.get_subcommands_option().subcommands.values():
                self._call_generator(subcommand)
