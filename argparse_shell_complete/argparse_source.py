#!/usr/bin/python3

import sys
import argparse

from .commandline import *

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
            if action.nargs in ('+', '*'):
                is_repeatable = True
            elif action.nargs in (1, None):
                is_repeatable = False
            else:
                raise Exception("Invalid nargs: %r" % action)

            commandline.add_positional(
                metavar=action.metavar or action.dest,
                complete=get_complete(action),
                help=action.help,
                repeatable=is_repeatable,
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

