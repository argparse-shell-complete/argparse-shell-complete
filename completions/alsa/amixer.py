#!/usr/bin/python3

import argparse

from argparse_shell_complete import argparse_mod

argp = argparse.ArgumentParser(prog='amixer', description='command-line mixer for ALSA soundcard driver')

argp.add_argument('-c', '--card', metavar='NUMBER',
                  help='sound card number or id').complete('exec', '_amixer_list_devices')

argp.add_argument('-D', '--device', metavar='DEVICE',
                  help='mixer device name')

argp.add_argument('-d', '--debug', action='store_true',
                  help='debug mode')

argp.add_argument('-n', '--no-check', action='store_true',
                  help='do not perform range checking')

argp.add_argument('-q', '--quiet', action='store_true',
                  help='quiet mode, do not show results of changes.')

argp.add_argument('-a', '--abstraction', choices=('none', 'basic'),
                  help='mixer abstraction level')

argp.add_argument('-s', '--stdin', action='store_true',
                  help='read commands from stdout')

argp.add_argument('-R', '--raw-volume', action='store_true',
                  help='Use the raw value (default)')

argp.add_argument('-M', '--mapped-volumen', action='store_true',
                  help='Use the mapped volume')

subp = argp.add_subparsers(description='commands')

# =============================================================================
# Command 'info'
# =============================================================================
cmdp = subp.add_parser('info', help='Shows the information about a mixer device')

# =============================================================================
# Command 'scontrols'
# =============================================================================
cmdp = subp.add_parser('scontrols', help='Show all mxier simple controls')

# =============================================================================
# Command 'scontents'
# =============================================================================
cmdp = subp.add_parser('scontents', help='Show contents of all mixer simple controls (default command)')

# =============================================================================
# Command 'sset'
# =============================================================================
# alias set
#cmdp = subp.add_parser('sset sID P      set contents for one mixer simple control
cmdp = subp.add_parser('sset', help='Set contents for one mixer simple control')

cmdp.add_argument('SCONTROL').complete('exec', '_amixer_list_simple_mixer_control')

cmdp.add_argument('PARAMETER')

# =============================================================================
# Command 'sget'
# =============================================================================
# alias get
#cmdp = subp.add_parser('sget sID        get contents for one mixer simple control
cmdp = subp.add_parser('sget', help='Get contents for one mixer simple control')

cmdp.add_argument('SCONTROL').complete('exec', '_amixer_list_simple_mixer_control')

# =============================================================================
# Command 'controls'
# =============================================================================
cmdp = subp.add_parser('controls', help='Show all controls for given card')

# =============================================================================
# Command 'contents'
# =============================================================================
cmdp = subp.add_parser('contents', help='Show contents of all controls for given card')

# =============================================================================
# Command 'cset'
# =============================================================================
#cmdp = subp.add_parser('cset cID P      set control contents for one control
cmdp = subp.add_parser('cset', help='Set control contents for one control')

cmdp.add_argument('CONTROL').complete('exec', '_amixer_list_mixer_control')

cmdp.add_argument('PARAMETER')

# =============================================================================
# Command 'cget'
# =============================================================================
#cmdp = subp.add_parser('cget cID        get control contents for one control
cmdp = subp.add_parser('cget', help='Get control contents for one control')

cmdp.add_argument('CONTROL').complete('exec', '_amixer_list_mixer_control')

# =============================================================================
# Command 'sevents'
# =============================================================================
cmdp = subp.add_parser('sevents', help='Show the mixer events for simple controls')

# =============================================================================
# Command 'events'
# =============================================================================
cmdp = subp.add_parser('events', help='Show contents of all mixer controls')

