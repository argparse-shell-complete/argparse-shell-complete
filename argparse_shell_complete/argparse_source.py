#!/usr/bin/python3

import sys
import argparse

from .commandline import *

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

        if action.get_complete():
            raise Exception('Action has complete but takes no arguments', action)

        return None
    elif isinstance(action, argparse._StoreAction) or \
         isinstance(action, argparse._ExtendAction) or \
         isinstance(action, argparse._AppendAction):

        if action.choices and action.get_complete():
            raise Exception('Action has both choices and complete set', action)

        if action.choices:
            if isinstance(action.choices, range):
                if action.choices.step == 1:
                    complete = ('range', action.choices.start, action.choices.stop)
                else:
                    complete = ('range', action.choices.start, action.choices.stop, action.choices.step)
            else:
                complete = ('choices', action.choices)
        else:
            complete = action.get_complete()

        return complete

    elif isinstance(action, argparse.BooleanOptionalAction):
        raise Exception("not supported")

    raise Exception('Unknown action: %r' % action)

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
                when=action.get_when()
            )
        else:
            if action.nargs is None or action.nargs == 1:
                takes_args = True
            elif action.nargs == '?':
                takes_args = '?'
            elif action.nargs == 0:
                takes_args = False
            else:
                print('Truncating %r nargs' % action, file=sys.stderr)

            metavar = None
            if takes_args:
                metavar = action.metavar or action.dest

            commandline.add_option(
                action.option_strings,
                metavar=metavar,
                complete=get_complete(action),
                help=action.help,
                takes_args=takes_args,
                multiple_option=action.get_multiple_option(),
                when=action.get_when()
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

