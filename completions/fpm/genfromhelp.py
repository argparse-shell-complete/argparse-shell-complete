#!/usr/bin/python3

import re
import sys

FPM_HELP_FILE = 'fpm.help.txt'

COMPLETE = {
    '-t': {"choices": ['apk', 'cpan', 'deb', 'dir', 'empty', 'freebsd', 'gem',
                       'npm', 'osxpkg', 'p5p', 'pacman', 'pear', 'pkgin', 'pleaserun',
                       'puppet', 'python', 'rpm', 'sh', 'snap', 'solaris', 'tar',
                       'virtualenv', 'zip']},

    '-s': {"choices": ['apk', 'cpan', 'deb', 'dir', 'empty', 'freebsd', 'gem',
                       'npm', 'osxpkg', 'p5p', 'pacman', 'pear', 'pkgin', 'pleaserun',
                       'puppet', 'python', 'rpm', 'sh', 'snap', 'solaris', 'tar',
                       'virtualenv', 'zip']},

    '-C': {"complete": ['file']},

    '--log': {"choices": ['error', 'warn', 'info', 'debug']},

    '--exclude-file': {"complete": ['file']},

    '--inputs': {"complete": ['file']},

    '--post-install': {"complete": ['file']},
    '--pre-install': {"complete": ['file']},
    '--post-uninstall': {"complete": ['file']},
    '--pre-uninstall': {"complete": ['file']},
    '--after-install': {"complete": ['file']},
    '--before-install': {"complete": ['file']},
    '--after-remove': {"complete": ['file']},
    '--before-remove': {"complete": ['file']},
    '--after-upgrade': {"complete": ['file']},
    '--before-upgrade': {"complete": ['file']},

    '--workdir': {"complete": ['directory']},

    '--fpm-options-file': {"complete": ['file']},

    '--rpm-digest': {"choices":  ['md5','sha1','sha256','sha384','sha512']},

    '--rpm-compression-level': {"choices": range(0, 10)},

    '--rpm-compression': {"choices": ['none','xz','xzmt','gzip','bzip2']},

    '--osxpkg-postinstall-action': {'choices': ['logout', 'restart', 'shutdown']},
}

def find_complete_by_opts(opts):
    for opt in opts:
        if opt in COMPLETE:
            return COMPLETE.pop(opt)
    return None

def process(line):
    line = line.strip()
    if not line:
        return

    words = line.split(' ')
    opts = []
    metavar = None
    when = None
    multiple_option = False
    choices = None
    complete = None

    while words[0].startswith('-'):
        opts.append(words[0].replace(',', ''))
        del words[0]

    if words[0].isupper():
        metavar = words[0]
        del words[0]

    description = ' '.join(words).strip()

    m = re.match(r'\((\w+) only\)', description)
    if m:
        when = m[1]
        description = re.sub(r'\((\w+) only\) ', '', description)

    if 'multiple times' in description:
        multiple_option = True

    compl = find_complete_by_opts(opts)
    if compl:
        choices = compl.get('choices', None)
        complete = compl.get('complete', None)

    if '[no-]' not in opts[0]:
        print_argument(opts, metavar, description, choices, complete, when, multiple_option)
    else:
        opts_without_no = [opts[0].replace('[no-]', '')]
        opts_with_no = [opts[0].replace('[no-]', 'no-')]
        print_argument(opts_without_no, metavar, description, choices, complete, when, multiple_option)
        print_argument(opts_with_no, metavar, description, choices, complete, when, multiple_option)

def make_complete(complete):
    return '%r' % complete[0]

def print_argument(opts, metavar, description, choices, complete, when, multiple_option):
    print('argp.add_argument(%s,' % repr(opts).strip('[]'), end='')
    if metavar:
        print(' metavar=%r,' % metavar)
    else:
        print(' action=\'store_true\',')
    if choices:
        print('  choices=%r,' % choices)
    print('  help=%r)' % description, end='')
    if complete:
        print('.complete(%s)' % make_complete(complete), end='')
    if when:
        print('.when("option_is -t --output-type -s --input-type -- %s")' % when, end='')
    if multiple_option:
        print('.set_multiple_option()', end='')
    print()
    print()

# =============================================================================
# Main
# =============================================================================

with open(FPM_HELP_FILE, 'r') as fh:
    help_text = fh.read()
lines = help_text.split('\n')

have_options = False
for line in lines:
    if line == 'Options:':
        have_options = True
    elif have_options:
        process(line)

if len(COMPLETE):
    print("Warning, not everything in COMPLETE has been consumed", file=sys.stderr)

