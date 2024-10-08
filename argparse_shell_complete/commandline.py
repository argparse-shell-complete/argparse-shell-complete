#!/usr/bin/python3

from collections import OrderedDict

from . import config as _config

def is_bool(obj):
    return isinstance(obj, bool)

class ExtendedBool:
    TRUE    = True
    FALSE   = False
    INHERIT = 'INHERIT'

class CommandLine:
    '''
    Represents a command line interface with options, positionals, and subcommands.
    '''

    def __init__(self,
                 program_name,
                 parent=None,
                 help=None,
                 aliases=[],
                 abbreviate_commands=ExtendedBool.INHERIT,
                 abbreviate_options=ExtendedBool.INHERIT,
                 inherit_options=ExtendedBool.INHERIT):

        '''
        Initializes a CommandLine object with the specified parameters.

        Args:
            program_name (str): The name of the program (or subcommand).
            help (str): The help message for the program (or subcommand).
            parent (CommandLine or None): The parent command line object, if any.
            abbreviate_commands (ExtendedBool): Specifies if commands can be abbreviated.
            abbreviate_options (ExtendedBool): Specifies if options can be abbreviated.
            inherit_options (ExtendedBool): Specifies if options are visible to subcommands.
        '''
        assert isinstance(program_name, str), "CommandLine: program_name: expected str, got %r" % program_name
        assert isinstance(help, (str, None.__class__)), "CommandLine: help: expected str, got %r" % help
        assert isinstance(parent, (CommandLine, None.__class__)), "CommandLine: parent: expected CommandLine, got %r" % parent

        self.prog = program_name
        self.parent = parent
        self.help = help
        self.aliases = aliases
        self.abbreviate_commands = abbreviate_commands
        self.abbreviate_options = abbreviate_options
        self.inherit_options = inherit_options
        self.options = []
        self.positionals = []
        self.subcommands = None

    def add_option(self,
            option_strings,
            metavar=None,
            help=None,
            complete=None,
            takes_args=True,
            group=None,
            multiple_option=ExtendedBool.INHERIT,
            when=None):
        '''
        Adds a new option to the command line.

        Args:
            option_strings (list of str): The list of option strings.
            metavar (str): The metavar for the option.
            help (str): The help message for the option.
            complete (tuple): The completion specification for the option.
            takes_args (bool): Specifies if the option takes arguments.
            group (str): Specify to which mutually exclusive group this option belongs to.
            multiple_option (ExtendedBool): Specifies if the option can be repeated.
            when (str): Specifies a condition for showing this option.

        Returns:
            Option: The newly added Option object.
        '''

        o = Option(self,
                   option_strings,
                   metavar=metavar,
                   help=help,
                   complete=complete,
                   takes_args=takes_args,
                   group=group,
                   multiple_option=multiple_option,
                   when=when)
        self.options.append(o)
        return o

    def add_positional(self,
            number,
            metavar=None,
            help=None,
            repeatable=False,
            complete=None,
            when=None):
        '''
        Adds a new positional argument to the command line.

        Args:
            metavar (str): The metavar for the positional.
            help (str): The help message for the positional.
            repeatable (bool): Specifies if positional can be specified more times
            complete (tuple): The completion specification for the positional.
            when (str): Specifies a condition for showing this positional.

        Returns:
            Positional: The newly added Positional object.
        '''

        p = Positional(self,
                       number,
                       metavar=metavar,
                       help=help,
                       repeatable=repeatable,
                       complete=complete,
                       when=when)
        self.positionals.append(p)
        return p

    def add_mutually_exclusive_group(self):
        '''
        Adds a new mutually exclusive group

        Returns:
            MutuallyExclusiveGroup: The newly created mutually exclusive group.
        '''
        group = MutuallyExclusiveGroup(self)
        return group

    def add_subcommands(self, name='command', help=None):
        '''
        Adds a subcommands option to the command line if none exists already.

        Args:
            name (str): The name of the subcommands option.
            help (str): The help message for the subcommands option.

        Returns:
            SubCommandsOption: The newly created subcommands option.

        Raises:
            Exception: If the command line object already has subcommands.
        '''
        assert isinstance(name, str), "CommandLine.add_subcommands: name: expected str, got %r" % name
        assert isinstance(help, (str, None.__class__)), "CommandLine.add_subcommands: help: expected str, got %r" % help

        if self.subcommands:
            raise Exception('CommandLine object already has subcommands')

        self.subcommands = SubCommandsOption(self, name, help)
        return self.subcommands

    def get_options(self, with_parent_options=False, only_with_arguments=False):
        '''
        Gets a list of options associated with the command line.

        Args:
            with_parent_options (bool): If True, include options from parent command lines.
            only_with_arguments (bool): If True, include only options that take arguments.

        Returns:
            list: A list of Option objects
        '''
        assert is_bool(with_parent_options), "CommandLine.get_options: with_parent_options: expected bool, got %r" % with_parent_options
        assert is_bool(only_with_arguments), "CommandLine.get_options: only_with_arguments: expected bool, got %r" % only_with_arguments

        commandlines = self.get_parents(include_self=True) if with_parent_options else [self]
        result = []

        for commandline in commandlines:
            for option in commandline.options:
                if only_with_arguments is False or option.takes_args:
                    result.append(option)
        return result

    def get_option_strings(self, with_parent_options=False, only_with_arguments=False):
        '''
        Gets a list of option strings associated with the command line.

        Args:
            with_parent_options (bool): If True, include options from parent command lines.
            only_with_arguments (bool): If True, include only options that take arguments.

        Returns:
            list: A list of option strings
        '''
        assert is_bool(with_parent_options), "CommandLine.get_option_strings: with_parent_options: expected bool, got %r" % with_parent_options
        assert is_bool(only_with_arguments), "CommandLine.get_option_strings: only_with_arguments: expected bool, got %r" % only_with_arguments

        option_strings = []

        for o in self.get_options(with_parent_options=with_parent_options, only_with_arguments=only_with_arguments):
            option_strings.extend(o.option_strings)

        return option_strings

    def get_positionals(self):
        '''
        Gets a list of positional arguments associated with the command line.

        Note:
            SubCommandsOption objects are not considered positional arguments and are not included in the list.

        Returns:
            list: A list of positional arguments
        '''
        return list(self.positionals)

    def get_subcommands_option(self):
        '''
        Gets the subcommands option of the command line.

        Returns:
            SubCommandsOption or None: The subcommands option if it exists, otherwise None.
        '''
        return self.subcommands

    def get_parents(self, include_self=False):
        '''
        Gets a list of parent CommandLine objects.

        Args:
            include_self (bool): If True, includes the current CommandLine object in the list.

        Returns:
            list: A list of parent CommandLine objects.
        '''
        assert is_bool(include_self), "CommandLine.get_parents: include_self: expected bool, got %r" % include_self

        parents = []

        parent = self.parent
        while parent:
            parents.insert(0, parent)
            parent = parent.parent

        if include_self:
            parents.append(self)

        return parents

    def get_highest_positional_num(self):
        highest = 0
        for positional in self.positionals:
            highest = max(highest, positional.number)
        if self.subcommands:
            highest += 1
        return highest

    def get_program_name(self):
        commandlines = self.get_parents(include_self=True)
        return commandlines[0].prog

    def copy(self):
        '''
        Make a copy of the current CommandLine object, including sub-objects.
        '''
        copy = CommandLine(
            self.prog,
            parent=None,
            help=self.help,
            aliases=self.aliases,
            abbreviate_commands=self.abbreviate_commands,
            abbreviate_options=self.abbreviate_options,
            inherit_options=self.inherit_options)

        for option in self.options:
            copy.add_option(
                option.option_strings,
                metavar = option.metavar,
                help = option.help,
                complete = option.complete,
                takes_args = option.takes_args,
                group = option.group,
                multiple_option = option.multiple_option,
                when = option.when
            )

        for positional in self.positionals:
            copy.add_positional(
                positional.number,
                metavar = positional.metavar,
                help = positional.help,
                repeatable = positional.repeatable,
                complete = positional.complete,
                when = positional.when
            )

        if self.subcommands is not None:
            subcommands_option = copy.add_subcommands(self.subcommands.metavar, self.subcommands.help)
            for subparser in self.subcommands.subcommands:
                subcommands_option.add_commandline_object(subparser.copy())

        return copy

    def __eq__(self, other):
        return (
            isinstance(other, CommandLine) and
            self.prog                == other.prog and
            self.aliases             == other.aliases and
            self.help                == other.help and
            self.abbreviate_commands == other.abbreviate_commands and
            self.abbreviate_options  == other.abbreviate_options and
            self.inherit_options     == other.inherit_options and
            self.options             == other.options and
            self.positionals         == other.positionals and
            self.subcommands         == other.subcommands
        )

    def __repr__(self):
        return '{\nprog: %r,\nhelp: %r,\nabbreviate_commands: %r,\noptions: %r,\npositionals: %r,\nsubcommands: %r}' % (
            self.prog, self.help, self.abbreviate_commands, self.options, self.positionals, self.subcommands)

class Positional:
    def __init__(
            self,
            parent,
            number,
            metavar=None,
            help=None,
            complete=None,
            repeatable=False,
            when=None):

        assert isinstance(number, int), "Positional: number: expected int, got %r" % number

        self.parent = parent
        self.number = number
        self.metavar = metavar
        self.help = help
        self.repeatable = repeatable
        self.when = when

        if complete:
            self.complete = complete
        else:
            self.complete = ('none',)

    def get_positional_index(self):
        '''
        Returns the index of the current positional argument within the current commandline, including parent commandlines.

        Returns:
            int: The index of the positional argument.
        '''
        positional_no = self.number - 1

        for commandline in self.parent.get_parents():
            highest = 0
            for positional in commandline.get_positionals():
                highest = max(highest, positional.number)
            positional_no += highest

            if commandline.get_subcommands_option():
                positional_no += 1

        return positional_no

    def get_positional_num(self):
        '''
        Returns the number of the current positional argument within the current commandline, including parent commandlines.

        Note:
            This is the same as `CommandLine.get_positional_index() + 1`.

        Returns:
            int: The number of the positional argument.
        '''
        return self.get_positional_index() + 1


    def OrderedDict(self):
        r = OrderedDict()

        r['number'] = self.number

        if self.metavar is not None:
            r['metavar'] = self.metavar

        if self.help is not None:
            r['help'] = self.help

        if self.repeatable is not False:
            r['repeatable'] = self.repeatable

        if self.when is not None:
            r['when'] = self.when

        if self.complete and self.complete[0] != 'none':
            r['complete'] = self.complete

        return r

class Option:
    def __init__(
            self,
            parent,
            option_strings,
            metavar=None,
            help=None,
            complete=None,
            group=None,
            takes_args=True,
            multiple_option=ExtendedBool.INHERIT,
            when=None):
        self.parent = parent
        self.option_strings = option_strings
        self.metavar = metavar
        self.help = help
        self.group = group
        self.takes_args = takes_args
        self.multiple_option = multiple_option
        self.when = when

        if not len(option_strings):
            raise Exception('Empty option strings')

        for option_string in option_strings:
            if ' ' in option_string:
                raise Exception("Invalid option: %r" % option_string)

            if not option_string.startswith('-'):
                raise Exception("Invalid option: %r" % option_string)

        if complete:
            self.complete = complete
        else:
            self.complete = ('none',)

        if not self.takes_args and self.metavar:
            raise Exception('Option does not take an argument but has metavar set')

    def OrderedDict(self):
        r = OrderedDict()
        r['option_strings'] = self.option_strings

        if self.metavar is not None:
            r['metavar'] = self.metavar

        if self.help is not None:
            r['help'] = self.help

        if self.takes_args != True:
            r['takes_args'] = self.takes_args

        if self.group is not None:
            r['group'] = self.group

        if self.multiple_option != ExtendedBool.INHERIT:
            r['multiple_option'] = self.multiple_option

        if self.complete and self.complete[0] != 'none':
            r['complete'] = self.complete

        if self.when is not None:
            r['when'] = self.when

        return r

    def get_option_strings(self):
        '''
        Returns the option strings associated with the Option object.

        Returns:
            list: A list of strings representing the option strings.
        '''
        return self.option_strings

    def get_short_option_strings(self):
        '''
        Returns the short option strings associated with the Option object.

        Returns:
            list: A list of short option strings ("-o").
        '''
        return [o for o in self.option_strings if o.startswith('-') and len(o) == 2]

    def get_long_option_strings(self):
        '''
        Returns the long option strings associated with the Option object.

        Returns:
            list: A list of long option strings ("--option").
        '''
        return [o for o in self.option_strings if o.startswith('--')]

    def get_old_option_strings(self):
        '''
        Returns the old-style option strings associated with the Option object.

        Returns:
            list: A list of old-style option strings ("-option").
        '''
        return [o for o in self.option_strings if o.startswith('-') and not o.startswith('--') and len(o) > 2]

    def get_conflicting_options(self):
        '''
        Returns a list of conflicting options within the same mutually exclusive group.

        Returns:
            list: A list of Option objects representing conflicting options.
        '''
        if not self.group:
            return []
        r = []
        for option in self.parent.options:
            if option.group == self.group:
                r.append(option)
        r.remove(self)
        return r

    def get_conflicting_option_strings(self):
        '''
        Returns a list of option strings conflicting with the current option within the same mutually exclusive group.

        Returns:
            list: A list of option strings representing conflicting options.
        '''
        option_strings = []
        for option in self.get_conflicting_options():
            option_strings.extend(option.get_option_strings())
        return option_strings

    def __eq__(self, other):
        return (
            isinstance(other, Option) and
            self.option_strings  == other.option_strings and
            self.metavar         == other.metavar and
            self.help            == other.help and
            self.takes_args      == other.takes_args and
            self.multiple_option == other.multiple_option and
            self.complete        == other.complete and
            self.group           == other.group
        )

    def __repr__(self):
        return '{option_strings: %r, metavar: %r, help: %r}' % (
            self.option_strings, self.metavar, self.help)

class SubCommandsOption(Positional):
    def __init__(self, parent, name, help):
        self.subcommands = list()

        super().__init__(
            parent,
            parent.get_highest_positional_num() + 1,
            metavar='command',
            help=help)

    def add_commandline_object(self, commandline):
        commandline.parent = self.parent
        self.subcommands.append(commandline)

    def add_commandline(self, name, help=''):
        commandline = CommandLine(name, help=help, parent=self.parent)
        self.subcommands.append(commandline)
        return commandline

    def get_all_subcommands(self, with_aliases=True):
        r = OrderedDict()
        for subcommand in self.subcommands:
            r[subcommand.prog] = subcommand.help
            if with_aliases:
                for alias in subcommand.aliases:
                    r[alias] = subcommand.help
        return r

    def __eq__(self, other):
        return (
            isinstance(other, SubCommandsOption) and
            self.subcommands    == other.subcommands and
            self.help           == other.help and
            self.metavar        == other.metavar and
            self.complete       == other.complete
        )

    def __repr__(self):
        return '{help: %r, subcommands %r}' % (
            self.help, self.subcommands)

class MutuallyExclusiveGroup:
    def __init__(self, parent, group):
        assert isinstance(parent, CommandLine), "MutuallyExclusiveGroup: parent: expected CommandLine, got %r" % parent

        self.parent = parent
        self.group = group

    def add(self,
            option_strings,
            metavar=None,
            help=None,
            complete=None,
            takes_args=True,
            multiple_option=ExtendedBool.INHERIT):
        ''' Creates and adds a new option '''
        return self.parent.add_option(
            option_strings,
            metavar=metavar,
            help=help,
            complete=complete,
            takes_args=takes_args,
            group=self.group,
            multiple_option=multiple_option)

    def add_option(self, option):
        ''' Adds an option object '''
        option.parent = self.parent
        option.group = self.group

def CommandLine_Apply_Config(commandline, config):
    '''
    Applies configuration settings to a command line object.

    If a setting in the CommandLine or Option object is set to ExtendedBool.INHERIT,
    it will be overridden by the corresponding setting from the config object.

    Args:
        commandline (CommandLine): The command line object to apply the configuration to.
        config (Config): The configuration object containing the settings to apply.

    Returns:
        None
    '''
    assert isinstance(commandline, CommandLine), "CommandLine_Apply_Config: commandline: expected CommandLine, got %r" % commandline
    assert isinstance(config, _config.Config), "CommandLine_Apply_Config: config: expected Config, got %r" % config

    if commandline.abbreviate_commands == ExtendedBool.INHERIT:
        commandline.abbreviate_commands = config.abbreviate_commands

    if commandline.abbreviate_options == ExtendedBool.INHERIT:
        commandline.abbreviate_options = config.abbreviate_options

    if commandline.inherit_options == ExtendedBool.INHERIT:
        commandline.inherit_options = config.inherit_options

    for option in commandline.options:
        if option.multiple_option == ExtendedBool.INHERIT:
            option.multiple_option = config.multiple_options
            # TODO: this shold be commandline.multiple_options

    if commandline.get_subcommands_option():
        for subcommand in commandline.get_subcommands_option().subcommands:
            CommandLine_Apply_Config(subcommand, config)
