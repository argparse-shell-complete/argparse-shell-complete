#!/usr/bin/python3

from setuptools import setup

setup(
    name='argparse-shell-complete',
    version='0.0.0',
    author='Benjamin Abendroth',
    author_email='braph93@gmx.de',
    packages=['argparse_shell_complete'],
    scripts=['argparse-shell-complete'],
    description='Create shell completion scripts from pythons argument parser',
    url='https://github.com/argparse-shell-complete/argparse-shell-complete',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
    ],
    license='GPL-3.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
