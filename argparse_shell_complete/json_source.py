from collections import OrderedDict, namedtuple

from .commandline import *

def jsonToObject(json, prog):
    commandline = CommandLine(
        prog,
        parent = None,
        help = json['help'],
        aliases = json.get('aliases', []),
        abbreviate_commands=json.get('abbreviate_commands', ExtendedBool.INHERIT),
        abbreviate_options=json.get('abbreviate_options', ExtendedBool.INHERIT),
        inherit_options=json.get('inherit_options', ExtendedBool.INHERIT))

    for json_option in json.get('options', []):
        commandline.add_option(
            json_option['option_strings'],
            metavar = json_option.get('metavar', None),
            help = json_option.get('help', None),
            takes_args = json_option.get('takes_args', True),
            group = json_option.get('group', None),
            multiple_option = json_option.get('multiple_option', ExtendedBool.INHERIT),
            complete = json_option.get('complete', None),
            when = json_option.get('when', None)),

    for json_positional in json.get('positionals', []):
        commandline.add_positional(
            metavar = json_positional.get('metavar', None),
            help = json_positional.get('help', None),
            repeatable = json_positional.get('repeatable', False),
            complete = json_positional.get('complete', None),
            when = json_positional.get('when', None)),

    return commandline

class CommandlineTree:
    Node = namedtuple('Node', ['commandline', 'subcommands'])

    def __init__(self):
        self.root = CommandlineTree.Node(None, {})

    def add_commandline(self, commandline):
        previous_commands = commandline['prog'].split()
        command = previous_commands.pop()

        node = self.root

        for previous_command in previous_commands:
            node = node.subcommands[previous_command]

        node.subcommands[command] = CommandlineTree.Node(jsonToObject(commandline, command), {})

    def get_root_commandline(self):
        if len(self.root.subcommands) == 0:
            raise Exception("No programs defined")

        if len(self.root.subcommands) > 1:
            raise Exception("Too many programs defined")

        return list(self.root.subcommands.values())[0]

def JSON_To_Commandline(json):
    def visit(node):
        if len(node.subcommands):
            subp = node.commandline.add_subcommands()
            for subcommand in node.subcommands.values():
                subp.add_commandline_object(subcommand.commandline)
                visit(subcommand)

    commandline_tree = CommandlineTree()

    for commandline in json:
        commandline_tree.add_commandline(commandline)

    visit(commandline_tree.get_root_commandline())

    return commandline_tree.get_root_commandline().commandline


def CommandLine_To_JSON(commandline, config=None):
    def get_CommandLine_Object(commandline):
        commandline_json = OrderedDict()

        prog = ' '.join(c.prog for c in commandline.get_parents(include_self=True))

        commandline_json['prog'] = prog

        if commandline.aliases:
            commandline_json['aliases'] = commandline.aliases

        if commandline.help:
            commandline_json['help'] = commandline.help

        if commandline.abbreviate_commands != ExtendedBool.INHERIT:
            commandline_json['abbreviate_commands'] = commandline.abbreviate_commands

        if commandline.abbreviate_options != ExtendedBool.INHERIT:
            commandline_json['abbreviate_options'] = commandline.abbreviate_options

        if commandline.inherit_options != ExtendedBool.INHERIT:
            commandline_json['inherit_options'] = commandline.inherit_options

        if commandline.options:
            commandline_json['options'] = []
            for option in commandline.options:
                commandline_json['options'].append(option.OrderedDict())

        if commandline.positionals:
            commandline_json['positionals'] = []
            for positional in commandline.positionals:
                commandline_json['positionals'].append(positional.OrderedDict())

        return commandline_json

    def get_CommandLine_Objects(commandline, out_list):
        out_list.append(get_CommandLine_Object(commandline))
        if commandline.subcommands is not None:
            for parser in commandline.subcommands.subcommands:
                get_CommandLine_Objects(parser, out_list)

    commandline_json = []
    get_CommandLine_Objects(commandline, commandline_json)
    return commandline_json

