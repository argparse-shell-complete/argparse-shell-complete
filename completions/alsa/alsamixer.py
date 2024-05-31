#!/usr/bin/python3

import argparse

from argparse_shell_complete import argparse_mod

argp = argparse.ArgumentParser(prog='alsamixer', description='soundcard mixer for ALSA soundcard driver, with ncurses interface')

argp.add_argument('-c', '--card', metavar='NUMBER',
                  help='sound card number or id').complete('exec', '_alsamixer_list_devices')

argp.add_argument('-D', '--device', metavar='DEVICE',
                  help='mixer device name')

argp.add_argument('-m', '--mouse', action='store_true',
                  help='enable mouse')

argp.add_argument('-M', '--no-mouse', action='store_true',
                  help='disable mouse')

argp.add_argument('-f', '--config', metavar='FILE',
                  help='configuration file').complete('file')

argp.add_argument('-F', '--no-config', action='store_true',
                  help='do not load configuration file')

argp.add_argument('-V', '--view', choices=('playback', 'capture', 'all'),
                  help='starting view mode')

argp.add_argument('-B', '--black-background', action='store_true',
                  help='use black background color')

argp.add_argument('-g', '--no-color', action='store_true',
                  help='toggle using of colors')

argp.add_argument('-a', '--abstraction', choices=('none', 'basic'),
                  help='mixer abstraction level')
