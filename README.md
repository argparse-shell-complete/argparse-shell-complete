argparse-shell-complete
=======================

Generate shell completion files using pythons argparse module.

Status
======

This is a very new project.

Works for: bash, fish, zsh.

Installation
============

- Using Arch Linux:
  ```
  git clone https://github.com/argparse-shell-complete/argparse-shell-complete
  cd argparse-shell-complete
  makepkg -c && sudo pacman -U python-argparse-shell-complete*.pkg.*
  ```

- For other Linux distributions:
  ```
  git clone https://github.com/argparse-shell-complete/argparse-shell-complete
  cd argparse-shell-complete
  sudo ./setup.py install
  ```

Synopsis
========

> `argparse-shell-complete [OPTIONS] {bash,fish,zsh} <PARSER_FILE>`

Options
=======

**--abbreviate-commands={True,False}**

> Sets whether commands can be abbreviated.

**--abbreviate-options={True,False}**

> Sets whether options can be abbreviated.
> Note: abbreviated options are not supported by FISH and ZSH.

**--multiple-options={True,False}**

> Sets whether options are suggested multiple times during completion.

**--inherit-options={True,False}**

> Sets whether parent options are visible to subcommands.

**-vim-modeline={True,False}**

> Sets whether a vim modeline comment shall be appended to the generated code.

**--include-file=FILE**

> Include contents of FILE in output.

**-o|--output=FILE**

> Write output to destination file [default: stdout].

**-i|--install-system-wide**

> Write output to the system wide completions dir of shell.

**-u|--uninstall-system-wide**

> Uninstall the system wide completion file for program.

Completions
===========

To install system wide completion files for argparse-shell-complete, execute the following:

```
sudo argparse-shell-complete -i bash "$(which argparse-shell-complete)"
sudo argparse-shell-complete -i fish "$(which argparse-shell-complete)"
sudo argparse-shell-complete -i zsh  "$(which argparse-shell-complete)"
```

If you want to uninstall the completion files, pass `-u` to argparse-shell-complete:

```
sudo argparse-shell-complete -u bash "$(which argparse-shell-complete)"
sudo argparse-shell-complete -u fish "$(which argparse-shell-complete)"
sudo argparse-shell-complete -u zsh  "$(which argparse-shell-complete)"
```

Questions or problems
=====================

Don't hesitate to open an issue on GitHub.
