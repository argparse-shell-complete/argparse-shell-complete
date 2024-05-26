#!/usr/bin/python3

from . import utils

class ShellFunction():
    def __init__(self, funcname, code):
        self.funcname = funcname
        self.code = code.strip()

    def get(self, funcname=None):
        if funcname is None:
            funcname = self.funcname

        r  = '%s() {\n' % funcname
        r += '%s\n'     % utils.indent(self.code, 2).rstrip()
        r += '}'
        return r

class FishFunction():
    def __init__(self, funcname, code):
        self.funcname = funcname
        self.code = code.strip()

    def get(self, funcname=None):
        if funcname is None:
            funcname = self.funcname

        r  = 'function %s\n' % funcname
        r += '%s\n'     % utils.indent(self.code, 2).rstrip()
        r += 'end'
        return r

class GeneralHelpers():
    def __init__(self, function_prefix):
        self.function_prefix = function_prefix
        self.functions = dict()
        self.used_functions = dict()

    def add_function(self, function):
        self.functions[function.funcname] = function

    def use(self, function_name, prefix=False):
        if function_name not in self.functions:
            raise KeyError('No such function: %r' % function_name)

        # Code deduplication. If we saw a function with the same code,
        # return its funcname.
        # (Currently only used for zsh completion generator)
        for function in self.used_functions.keys():
            if self.functions[function_name].code == self.functions[function].code:
                return self.used_functions[function]

        new_function_name = function_name
        if prefix == True:
            new_function_name = '_%s_%s' % (self.function_prefix, function_name)

        if function_name in self.used_functions:
            return self.used_functions[function_name]

        self.used_functions[function_name] = new_function_name
        return new_function_name

    def get_code(self):
        r = []
        for funcname, real_funcname in self.used_functions.items():
            r.append(self.functions[funcname].get(real_funcname))
        return r
