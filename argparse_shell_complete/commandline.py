#!/usr/bin/python3

import sys
import argparse
from collections import OrderedDict, defaultdict
from itertools import chain

from . import shell
from . import config as _config

def is_bool(obj):
    return isinstance(obj, bool)

class ExtendedBool():
    TRUE    = True
    FALSE   = False
    INHERIT = 'inherit'

class CommandLine():
    '''
    Represents a command line interface with options, positionals, and subcommands.
    '''

    def __init__(self,
                 program_name,
                 help=None,
                 parent=None,
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
        '''
        assert isinstance(program_name, str), "CommandLine: program_name: expected str, got %r" % program_name
        assert isinstance(help, (str, None.__class__)), "CommandLine: help: expected str, got %r" % help
        assert isinstance(parent, (CommandLine, None.__class__)), "CommandLine: parent: expected CommandLine, got %r" % parent

        self.prog = program_name
        self.help = help
        self.parent = parent
        self.abbreviate_commands = abbreviate_commands
        self.abbreviate_options = abbreviate_options
        self.inherit_options = inherit_options
        self.options = []
        self.positionals = []
        self.subcommands = None

    def add_option(self,
            option_strings,
            metavar='',
            help='',
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
            multiple_option (ExtendedBool): Specifies if the option can be repeated.

        Returns:
            Option: The newly added option object.
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
            #positional_number,
            metavar='',
            help='',
            complete=None,
            #takes_args=True,
            when=None):
        '''
        Adds a new option or positional argument to the command line.

        Args:
            option_strings (list of str): The list of option strings.
            metavar (str): The metavar for the option.
            help (str): The help message for the option.
            complete (tuple): The completion specification for the option.
            takes_args (bool): Specifies if the option takes arguments.
            multiple_option (ExtendedBool): Specifies if the option can be repeated.

        Returns:
            Option: The newly added option object.
        '''

        p = Positional(self,
                       metavar=metavar,
                       help=help,
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

    def add_subcommands(self, name='command', help=''):
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
        assert isinstance(help, str), "CommandLine.add_subcommands: help: expected str, got %r" % help

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

    def get_program_name(self):
        commandlines = self.get_parents(include_self=True)
        return commandlines[0].prog

    def copy(self, parent=None):
        '''
        Make a copy of the current CommandLine object, including sub-objects.
        '''
        copy = CommandLine(self.prog, help=self.help, parent=parent)

        for option in self.options:
            o = copy.add_option(
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
                metavar = positional.metavar,
                help = positional.help,
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
            #positional_number,
            metavar='',
            help='',
            complete=None,
            #nargs
            when=None):
        self.parent = parent
        self.metavar = metavar
        self.help = help
        #self.nargs = nargs
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
        positionals = []

        for commandline in self.parent.get_parents(include_self=True):
            positionals.extend(commandline.get_positionals())
            if commandline.get_subcommands_option():
                positionals.append(commandline.get_subcommands_option())

        return positionals.index(self)

    def get_positional_num(self):
        '''
        Returns the number of the current positional argument within the current commandline, including parent commandlines.

        Note:
            This is the same as `CommandLine.get_positional_index() + 1`.

        Returns:
            int: The number of the positional argument.
        '''
        return self.get_positional_index() + 1

class Option:
    def __init__(
            self,
            parent,
            option_strings,
            metavar='',
            help='',
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

    def equals(self, other):
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

    def __eq__(self, other): # TODO: drop eequals?
        return self.equals(other)

    def __repr__(self):
        # TODO
        return '{option_strings: %r, metavar: %r, help: %r}' % (
            self.option_strings, self.metavar, self.help)

class SubCommandsOption(Positional):
    def __init__(self, parent, name, help):
        self.subcommands = list()

        super().__init__(
            parent,
            metavar='command',
            help=help)

    def add_commandline_object(self, commandline):
        commandline.parent = self.parent
        self.subcommands.append(commandline)

    def add_commandline(self, name, help=''):
        commandline = CommandLine(name, help=help, parent=self.parent)
        self.subcommands.append(commandline)
        return commandline

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
            metavar='',
            help='',
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

def JSON_To_Commandline(json):
    def find_CommandLine_by_id(list, id):
        for commandline in list:
            if commandline['id'] == id:
                return commandline

        raise KeyError(id)

    def jsonToObject(commandlines, json, parent):
        commandline = CommandLine(
            json['prog'],
            json['help'],
            parent,
            abbreviate_commands=json['abbreviate_commands'],
            abbreviate_options=json['abbreviate_options'])

        groups = defaultdict(list)
        for json_option in json['options']:
            o = commandline.add(
                json_option['option_strings'],
                json_option['metavar'],
                json_option['help'],
                json_option['complete'],
                json_option['takes_args'],
                json_option['multiple_option'],
                json_option['when'])
            if json_option['group'] is not None:
                groups[json_option['group']].append(o)

        for group, options in groups.items():
            g = commandline.add_mutually_exclusive_group()
            for option in options:
                g.add_option(option)

        if 'subcommands' in json:
            subcommands = commandline.add_subcommands()
            for name, id in json['subcommands'].items():
                subcommands.add_commandline_object(
                    jsonToObject(commandlines, find_CommandLine_by_id(commandlines, id), commandline)
                )

        return commandline

    commandlines = json['commandlines']
    commandline = jsonToObject(commandlines, find_CommandLine_by_id(commandlines, 'main'), None)
    return commandline

def CommandLine_To_JSON(commandline, config=None):
    def get_CommandLine_Object(commandline):
        commandline_json = OrderedDict()

        if commandline.parent is None:
            commandline_json['id'] = 'main'
        else:
            commandline_json['id'] = shell.make_completion_funcname(commandline)

        commandline_json['prog'] = commandline.prog
        commandline_json['help'] = commandline.help
        commandline_json['abbreviate_commands'] = commandline.abbreviate_commands
        commandline_json['abbreviate_options'] = commandline.abbreviate_options
        commandline_json['options'] = []

        groups = []
        for option in chain(commandline.options, commandline.positionals):
            option_json = OrderedDict()
            option_json['option_strings']  = option.option_strings
            option_json['metavar']         = option.metavar
            option_json['help']            = option.help
            option_json['takes_args']      = option.takes_args
            option_json['multiple_option'] = option.multiple_option
            option_json['complete']        = option.complete
            option_json['when']            = option.when

            if option.group is None:
                option_json['group'] = None
            else:
                if option.group not in groups:
                    groups.append(option.group)
                option_json['group'] = 'group%d' % (groups.index(option.group) + 1)
            commandline_json['options'].append(option_json)
            # TODO

        if commandline.subcommands is not None:
            commandline_json['subcommands'] = {}

            for parser in commandline.subcommands.subcommands.values():
                commandline_json['subcommands'][parser.prog] = shell.make_completion_funcname(parser)

        return commandline_json

    def get_CommandLine_Objects(commandline, out_list):
        out_list.append(get_CommandLine_Object(commandline))
        if commandline.subcommands is not None:
            for parser in commandline.subcommands.subcommands.values():
                get_CommandLine_Objects(parser, out_list)

    root_json = OrderedDict()
    commandline_json = root_json['commandlines'] = []

    get_CommandLine_Objects(commandline, commandline_json)

    return root_json

def Action_Get_Metavar(action):
    if action.metavar:
        return action.metavar
    elif action.type is int:
        return 'INT'
    elif action.type is bool:
        return 'BOOL'
    elif action.type is float:
        return 'FLOAT'
    else:
        return action.dest.upper()

def ArgumentParser_to_CommandLine(parser, prog=None, description=None):
    '''
    Converts an ArgumentParser object to a CommandLine object.

    Args:
        parser (argparse.ArgumentParser): The ArgumentParser object to convert.
        prog (str, optional): The name of the program. Defaults to the program name of the parser.
        description (str, optional): The description of the program. Defaults to the description of the parser.

    Returns:
        CommandLine: A CommandLine object representing the converted parser.
    '''

    def get_multiple_option(action):
        return getattr(action, 'multiple_option', ExtendedBool.INHERIT)

    def get_when(action):
        return getattr(action, 'condition', None)

    def get_takes_args(action):
        # TODO...
        if action.nargs is None or action.nargs == 1:
            return True
        elif action.nargs == '?':
            return '?'
        elif action.nargs == 0:
            return False
        elif action.nargs == '+':
            print('Truncating %r nargs' % action, file=sys.stderr)
            return True
        elif action.nargs == '*':
            print('Truncating %r nargs' % action, file=sys.stderr)
            return '?'
        elif isinstance(action.nargs, int) and action.nargs > 1:
            print('Truncating %r nargs' % action, file=sys.stderr)
            return True
        raise

    def get_complete(action):
        if isinstance(action, argparse._HelpAction):
            return None
        elif isinstance(action, argparse._VersionAction):
            return None
        elif isinstance(action, argparse._StoreTrueAction) or \
             isinstance(action, argparse._StoreFalseAction) or \
             isinstance(action, argparse._StoreConstAction) or \
             isinstance(action, argparse._AppendConstAction) or \
             isinstance(action, argparse._CountAction):

            if hasattr(action, 'completion'):
                raise Exception('Action has completion but takes not arguments', action)

            return None
        elif isinstance(action, argparse._StoreAction) or \
             isinstance(action, argparse._ExtendAction) or \
             isinstance(action, argparse._AppendAction):

            if action.choices and hasattr(action, 'completion'):
                raise Exception('Action has both choices and completion set', action)

            if action.choices:
                if isinstance(action.choices, range):
                    if action.choices.step == 1:
                        complete = ('range', action.choices.start, action.choices.stop)
                    else:
                        complete = ('range', action.choices.start, action.choices.stop, action.choices.step)
                else:
                    complete = ('choices', action.choices)
            elif hasattr(action, 'completion'):
                complete = action.completion
            else:
                complete = None

            return complete

        elif isinstance(action, argparse.BooleanOptionalAction):
            raise Exception("not supported")

        raise Exception('Unknown action: %r' % action)

    if not description:
        description = parser.description

    if not prog:
        prog = parser.prog

    commandline = CommandLine(prog, description)

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subparsers  = OrderedDict()

            for name, subparser in action.choices.items():
                subparsers[name] = {'parser': subparser, 'help': ''}

            for action in action._get_subactions():
                subparsers[action.dest]['help'] = action.help

            subp = commandline.add_subcommands(name='command', help='Subcommands')

            for name, data in subparsers.items():
                suboptions = ArgumentParser_to_CommandLine(data['parser'], name, data['help'])
                subp.add_commandline_object(suboptions)
        elif not action.option_strings:
            commandline.add_positional(
                metavar=action.metavar or action.dest,
                complete=get_complete(action),
                help=action.help,
                #takes_args=get_takes_args(action),
                when=get_when(action)
            )
        else:
            metavar = None
            takes_args = get_takes_args(action)
            if takes_args:
                metavar = action.metavar or action.dest.upper() # TODO

            commandline.add_option(
                action.option_strings,
                metavar=metavar,
                complete=get_complete(action),
                help=action.help,
                takes_args=takes_args,
                multiple_option=get_multiple_option(action),
                when=get_when(action)
            )

    group_counter = 0
    for group in parser._mutually_exclusive_groups:
        group_counter += 1
        group_name = 'group%d' % group_counter

        exclusive_group = MutuallyExclusiveGroup(commandline, group_name)
        for action in group._group_actions:
            for option in commandline.get_options():
                for option_string in action.option_strings:
                    if option_string in option.option_strings:
                        exclusive_group.add_option(option)
                        break

    return commandline


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

    if commandline.get_subcommands_option():
        for subcommand in commandline.get_subcommands_option().subcommands:
            CommandLine_Apply_Config(subcommand, config)
