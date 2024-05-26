argparse-shell-complete
======================

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
  makepkg && sudo pacman -U python-argparse-shell-complete*.pkg.*
  ```

Synopsis
========

```
argparse-shell-complete [OPTIONS] {bash,fish,zsh} <PARSER_FILE>
```

Options
=======

**--abbreviate-commands={True,False}**

> Sets whether commands can be abbreviated.

**--abbreviate-options={True,False}**

> Sets whether options can be abbreviated.
> Note: abbreviated options are not supported by ZSH.

**--multiple-options={True,False}**

> Sets whether options are suggested multiple times during completion.

**--inherit-options={True,False}**

> Sets whether parent options are visible to subcommands.

**-vim-modeline={True,False}**

> Sets whether a vim modeline comment shall be appended to the generated code.

**--include-file=FILE**

> Include contents of FILE in output.

Questions or problems
=====================

Don't hesitate to open an issue on GitHub.
