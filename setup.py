#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='argparse-shell-complete',
    version='0.0.0',
    author='Benjamin Abendroth',
    author_email='braph93@gmx.de',
    packages=['argparse_shell_complete'], #find_packages(), 
    scripts=['argparse-shell-complete'],
    description='Create shell completion scripts from pythons argument parser',
    url='https://github.com/argparse-shell-complete/argparse-shell-complete',
    #license='LICENSE.txt',
    #long_description=open('README.txt').read(),
)
