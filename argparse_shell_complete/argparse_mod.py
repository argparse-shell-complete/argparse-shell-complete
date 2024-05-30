#!/usr/bin/python3

import argparse


def _action_complete(self, command, *args):
    setattr(self, 'completion', (command, *args))
    return self


def _action_set_multiple_option(self, enable=True):
    setattr(self, 'multiple_option', enable)
    return self


argparse.Action.complete = _action_complete
argparse.Action.set_multiple_option = _action_set_multiple_option
