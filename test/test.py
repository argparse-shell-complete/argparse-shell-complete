#!/usr/bin/python3

import os
import sys
import time
import threading
import queue
import subprocess

import tests

SHELLS = ['bash', 'fish', 'zsh']
TMUX_SESSION_NAME = 'argparse-shell-complete-test'
TESTS_OUTFILE = 'tests.new.py'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run(args, env=None):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    if result.returncode != 0:
        raise Exception("Cmd %r failed: %s" % (args, result.stderr))

    return result.stdout

class TmuxClient:
    def __init__(self, session):
        self.session = session

    def run(self, args):
        env = os.environ.copy()
        env.pop('TMUX', None)
        return run(['tmux'] + args, env)

    def new_session(self, command_args=[]):
        self.run(['new-session', '-d', '-s', self.session] + command_args)

    def kill_session(self):
        self.run(['kill-session', '-t', self.session])

    def send_keys(self, *keys):
        self.run(['send-keys', '-t', self.session] + list(keys))

    def capture_pane(self):
        return self.run(['capture-pane', '-t', self.session, '-p'])

    def resize_window(self, x, y):
        self.run(['resize-window', '-t', self.session, '-x', str(x), '-y', str(y)])

def start_shell(tmux, shell, completion_file):
    if shell == 'bash':
        cmd = ['bash', '--norc']
        in_lines = '''\
PS1='> '
. /usr/share/bash-completion/bash_completion
. %s
''' % completion_file
    elif shell == 'fish':
        cmd = ['fish', '--no-config']
        in_lines = '''\
function fish_prompt; printf '> '; end
source %s
''' % completion_file
    elif shell == 'zsh':
        cmd = ['zsh', '--no-rcs']
        in_lines = '''\
PROMPT='> '
autoload -U compinit && compinit
source %s
''' % completion_file
    else:
        raise Exception('Invalid shell: %r' % shell)

    tmux.new_session(cmd)
    tmux.resize_window(80, 100)
    tmux.send_keys(in_lines)
    time.sleep(0.5)

def stop_shell(tmux):
    tmux.kill_session()

def complete(tmux, commandline, num_tabs=1):
    # Clear screen
    tmux.send_keys('C-c')
    tmux.send_keys('clear')
    tmux.send_keys('Enter')

    time.sleep(0.3)

    # Write commandline
    tmux.send_keys(commandline)

    # Write tabs
    for i in range(num_tabs):
        tmux.send_keys('Tab')

    time.sleep(1)

    result = tmux.capture_pane()
    result = result.rstrip()
    return result

def generate_completion(shell, outfile, args):
    run(['../argparse-shell-complete', shell, '-o', outfile, 'argparse-shell-complete-test'] + args)

def find_test_by_number(num):
    for test in tests.tests:
        if 'number' in test and test['number'] == num:
            return test

    raise Exception("No test with number %r found" % num)

def write_tests_file():
    def test_to_str(test):
        r  = "{\n"
        r += " 'number': %d,\n" % test['number']
        r += " 'description': %r,\n" % test['description']
        if 'comment' in test:
            r += " 'comment': %r,\n" % test['comment']
        r += " 'send': %r,\n" % test['send']
        if test.get('bash_tabs', 1) != 1:
            r += " 'bash_tabs': %d,\n" % test['bash_tabs']
        r += " 'bash_expected': '''\\\n%s\\\n''',\n" % test['bash_result'].replace('\\', '\\\\')
        if test.get('fish_tabs', 1) != 1:
            r += " 'fish_tabs': %d,\n" % test['fish_tabs']
        r += " 'fish_expected': '''\\\n%s\\\n''',\n" % test['fish_result'].replace('\\', '\\\\')
        if test.get('zsh_tabs', 1) != 1:
            r += " 'zsh_tabs': %d,\n" % test['zsh_tabs']
        r += " 'zsh_expected': '''\\\n%s\\\n'''\n" % test['zsh_result'].replace('\\', '\\\\')
        r += '}'
        return r

    r = 'tests = [\n\n'
    for test in tests.tests:
        if 'generate-scripts' in test:
            r += '%r,\n\n' % test
        else:
            r += '%s,\n\n' % test_to_str(test)
    r += ']'

    with open(TESTS_OUTFILE, 'w') as fh:
        fh.write(r)

def enumerate_tests():
    number = 1
    for test in tests.tests:
        if 'send' in test:
            test['number'] = number
            number += 1

def add_empty_expected_to_tests():
    for test in tests.tests:
        if 'generate-scripts' in test:  continue
        if 'bash_expected' not in test: test['bash_expected'] = ''
        if 'fish_expected' not in test: test['fish_expected'] = ''
        if 'zsh_expected'  not in test: test['zsh_expected']  = ''

def do_tests(shell, result_queue):
    tmux = TmuxClient(TMUX_SESSION_NAME + '-' + shell)

    for test in tests.tests:
        test = test.copy()
        if 'generate-scripts' in test:
            try:    stop_shell(tmux)
            except: pass
            completion_file = 'out.%s' % shell
            generate_completion(shell, completion_file, ['--zsh-compdef=False'] + test['generate-scripts'])
            start_shell(tmux, shell, completion_file)
        else:
            test[shell+'_result'] = complete(tmux, test['send'], test.get(shell+'_tabs', 1))
            result_queue.put(test)

    try:
        stop_shell(tmux)
    except:
        pass

class Tester():
    def __init__(self):
        self.result_queue = queue.Queue()
        self.threads = []
        self.failed = False

    def run(self):
        for shell in SHELLS:
            thread = threading.Thread(target=do_tests, args=(shell, self.result_queue))
            self.threads.append(thread)
            thread.start()

        while self.threads_are_running():
            self.eat_queue()
            time.sleep(0.5)
        self.eat_queue()

    def threads_are_running(self):
        for thread in self.threads:
            if thread.is_alive():
                return True
        return False

    def eat_queue(self):
        while not self.result_queue.empty():
            self.process_result(self.result_queue.get())

    def process_result(self, result):
        test = find_test_by_number(result['number'])
        for shell in SHELLS:
            shell_result_key   = '%s_result' % shell
            shell_expected_key = '%s_expected' % shell

            if shell_result_key in result:
                test[shell_result_key] = result[shell_result_key]

                if test[shell_result_key] != test[shell_expected_key]:
                    self.failed = True
                    print("Test #%02d (%-4s - %s) failed" % (test['number'], shell, test['description']))
                else:
                    print("Test #%02d (%-4s - %s) OK" % (test['number'], shell, test['description']))

                break

# =============================================================================
#
# =============================================================================

enumerate_tests()
add_empty_expected_to_tests()
tester = Tester()
tester.run()
write_tests_file()
if tester.failed:
    sys.exit(1)