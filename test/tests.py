tests = [

{'generate-scripts': []},

{
 'number': 1,
 'description': 'No arguments, check if all commands are listed',
 'send': 'argparse-shell-complete-test ',
 'bash_expected': '''\
> argparse-shell-complete-test
alias1            argparse-actions  subcommand        when
alias2            complete          test
> argparse-shell-complete-test\
''',
 'fish_expected': '''\
> argparse-shell-complete-test
alias1        (For testing the completer)  subcommand  (Test nested subcommands)
alias2        (For testing the completer)  test      (For testing the completer)
argparse-actions  (argparse tool actions)  when        (Test the "when"-feature)
complete         (Test complete commands)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test
alias2            alias1  test  -- For testing the completer
argparse-actions                -- argparse tool actions
complete                        -- Test complete commands
subcommand                      -- Test nested subcommands
when                            -- Test the "when"-feature\
'''
},

{
 'number': 2,
 'description': 'Check if subcommand is completed',
 'send': 'argparse-shell-complete-test t',
 'bash_expected': '''\
> argparse-shell-complete-test test\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test\
'''
},

{
 'number': 3,
 'description': 'Check if all options are listed',
 'send': 'argparse-shell-complete-test test -',
 'bash_expected': '''\
> argparse-shell-complete-test test -
-A                              -h
--arg                           --help
-arg                            --multiple-arg
--exclusive-1                   --multiple-flag
--exclusive-2                   -O
-F                              --optional
--flag                          -optional
-flag                           --special-chars-in-description
> argparse-shell-complete-test test -\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -
-A  -arg  --arg                                        (Option with arg)
-F  -flag  --flag                                        (A option flag)
-h  --help                             (show this help message and exit)
-O  -optional  --optional  --optional=        (Option with optional arg)
--exclusive-1
--exclusive-2
--multiple-arg
--multiple-flag
--special-chars-in-description  (Here are some special chars: $"'\\[]*`))\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -
--exclusive-1      --exclusive-2      --multiple-arg     --multiple-flag
--arg
-arg                            -A  -- Option with arg
--flag
-flag                           -F  -- A option flag
--help                          -h  -- show this help message and exit
--optional
-optional                       -O  -- Option with optional arg
--special-chars-in-description      -- Here are some special chars: $"'\\[]*`)\
'''
},

{
 'number': 4,
 'description': 'Check long option with argument (with space)',
 'send': 'argparse-shell-complete-test test --arg ',
 'bash_expected': '''\
> argparse-shell-complete-test test --arg
1  2  3
> argparse-shell-complete-test test --arg\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --arg
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test --arg
1  2  3\
'''
},

{
 'number': 5,
 'description': 'Check long option with argument (with equal sign)',
 'send': 'argparse-shell-complete-test test --arg=',
 'bash_expected': '''\
> argparse-shell-complete-test test --arg=
1  2  3
> argparse-shell-complete-test test --arg=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --arg=
--arg=1  (Option with arg)  --arg=3  (Option with arg)
--arg=2  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test --arg=
1  2  3\
'''
},

{
 'number': 6,
 'description': 'Check short option with argument (without space)',
 'send': 'argparse-shell-complete-test test -A',
 'bash_expected': '''\
> argparse-shell-complete-test test -A
-A1  -A2  -A3
> argparse-shell-complete-test test -A\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -A
-A1  (Option with arg)  -A2  (Option with arg)  -A3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -A
1  2  3\
'''
},

{
 'number': 7,
 'description': 'Check short option with argument (with space)',
 'send': 'argparse-shell-complete-test test -A ',
 'bash_expected': '''\
> argparse-shell-complete-test test -A
1  2  3
> argparse-shell-complete-test test -A\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -A
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -A
1  2  3\
'''
},

{
 'number': 8,
 'description': 'Check old-style option with argument (with space)',
 'send': 'argparse-shell-complete-test test -arg ',
 'bash_expected': '''\
> argparse-shell-complete-test test -arg
1  2  3
> argparse-shell-complete-test test -arg\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -arg
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -arg
1  2  3\
'''
},

{
 'number': 9,
 'description': 'Check old-style option with argument (with equal sign)',
 'send': 'argparse-shell-complete-test test -arg=',
 'bash_expected': '''\
> argparse-shell-complete-test test -arg=
1  2  3
> argparse-shell-complete-test test -arg=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -arg=
-arg=1  (Option with arg)  -arg=2  (Option with arg)  -arg=3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -arg=
1  2  3\
'''
},

{
 'number': 10,
 'description': 'Check long option with optional argument',
 'send': 'argparse-shell-complete-test test --optional=',
 'bash_expected': '''\
> argparse-shell-complete-test test --optional=
1  2  3
> argparse-shell-complete-test test --optional=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --optional=
…optional=1  (Option with optional arg)  …optional=3  (Option with optional arg)
…optional=2  (Option with optional arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test --optional=
1  2  3\
'''
},

{
 'number': 11,
 'description': 'Check short option with optional argument',
 'comment': 'FISH has a slightly wrong output',
 'send': 'argparse-shell-complete-test test -O',
 'bash_expected': '''\
> argparse-shell-complete-test test -O
-O1  -O2  -O3
> argparse-shell-complete-test test -O\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -O
-O1  (Option with optional arg)  -OA                  (Option with arg)
-O2  (Option with optional arg)  -OF                    (A option flag)
-O3  (Option with optional arg)  -Oh  (show this help message and exit)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -O
1  2  3\
'''
},

{
 'number': 12,
 'description': 'Check old-style option with optional argument',
 'send': 'argparse-shell-complete-test test -optional=',
 'bash_expected': '''\
> argparse-shell-complete-test test -optional=
1  2  3
> argparse-shell-complete-test test -optional=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -optional=
…optional=1  (Option with optional arg)  …optional=3  (Option with optional arg)
…optional=2  (Option with optional arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -optional=
1  2  3\
'''
},

{
 'number': 13,
 'description': 'Check if mutually exclusive options work',
 'send': 'argparse-shell-complete-test test --exclusive-1 --exclusive',
 'bash_expected': '''\
> argparse-shell-complete-test test --exclusive-1 --exclusive\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --exclusive-1 --exclusive\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test --exclusive-1 --exclusive\
'''
},

{
 'number': 14,
 'description': 'Check if multiple options work',
 'send': 'argparse-shell-complete-test test --multiple-flag --multiple-',
 'bash_expected': '''\
> argparse-shell-complete-test test --multiple-flag --multiple-
--multiple-arg   --multiple-flag
> argparse-shell-complete-test test --multiple-flag --multiple-\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --multiple-flag --multiple-
…multiple-arg  …multiple-flag\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test --multiple-flag --multiple-
--multiple-arg   --multiple-flag\
'''
},

{
 'number': 15,
 'description': 'Check option stacking',
 'comment': 'Does not work for BASH yet',
 'send': 'argparse-shell-complete-test test -F',
 'bash_expected': '''\
> argparse-shell-complete-test test -F\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -F
-FA                  (Option with arg)  -FO  (Option with optional arg)
-Fh  (show this help message and exit)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -F
-A  -- Option with arg
-h  -- show this help message and exit
-O  -- Option with optional arg\
'''
},

{
 'number': 16,
 'description': 'Check option stacking (with required argument and no space)',
 'send': 'argparse-shell-complete-test test -FA',
 'bash_expected': '''\
> argparse-shell-complete-test test -FA
-FA1  -FA2  -FA3
> argparse-shell-complete-test test -FA\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -FA
-FA1  (Option with arg)  -FA2  (Option with arg)  -FA3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -FA
1  2  3\
'''
},

{
 'number': 17,
 'description': 'Check option stacking (with required argument and space)',
 'send': 'argparse-shell-complete-test test -FA ',
 'bash_expected': '''\
> argparse-shell-complete-test test -FA
1  2  3
> argparse-shell-complete-test test -FA\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -FA
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -FA
1  2  3\
'''
},

{
 'number': 18,
 'description': 'Check option stacking (with optional argument)',
 'comment': 'FISH produces a bit of a wrong output',
 'send': 'argparse-shell-complete-test test -FO',
 'bash_expected': '''\
> argparse-shell-complete-test test -FO
-FO1  -FO2  -FO3
> argparse-shell-complete-test test -FO\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -FO
-FO1  (Option with optional arg)  -FOA                  (Option with arg)
-FO2  (Option with optional arg)  -FOh  (show this help message and exit)
-FO3  (Option with optional arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -FO
1  2  3\
'''
},

{
 'number': 19,
 'description': 'when: Check if none of --if-* options are listed',
 'send': 'argparse-shell-complete-test when -',
 'bash_expected': '''\
> argparse-shell-complete-test when -
-h          -O          -optional   --var
--help      --optional  -V          -var
> argparse-shell-complete-test when -\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -
-h  --help                       (show this help message and exit)
-O  -optional  -V  -var  --optional  --var  (Conditional variable)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when -
--help      -h                   -- show this help message and exit
--optional  --var  -var  -O  -V
-optional                        -- Conditional variable\
'''
},

{
 'number': 20,
 'description': 'when: Check if --if-var appears (with --var)',
 'send': 'argparse-shell-complete-test when --var value --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --var value --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --var value --if-var\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when --var value --if-var=\
'''
},

{
 'number': 21,
 'description': 'when: Check if --if-var appears (with -V)',
 'send': 'argparse-shell-complete-test when -V value --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -V value --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -V value --if-var\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when -V value --if-var=\
'''
},

{
 'number': 22,
 'description': 'when: Check if --if-var appears (with -var)',
 'send': 'argparse-shell-complete-test when -var value --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -var value --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -var value --if-var\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when -var value --if-var=\
'''
},

{
 'number': 23,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with -V foo)',
 'send': 'argparse-shell-complete-test when -V foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -V foo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when -V foo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -V foo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -V foo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 24,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with -Vfoo)',
 'send': 'argparse-shell-complete-test when -Vfoo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -Vfoo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when -Vfoo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -Vfoo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -Vfoo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 25,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with --var foo)',
 'send': 'argparse-shell-complete-test when --var foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --var foo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when --var foo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --var foo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when --var foo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 26,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with --var=foo)',
 'send': 'argparse-shell-complete-test when --var=foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --var=foo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when --var=foo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --var=foo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when --var=foo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 27,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with -var foo)',
 'send': 'argparse-shell-complete-test when -var foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -var foo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when -var foo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -var foo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -var foo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 28,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with -var=foo)',
 'send': 'argparse-shell-complete-test when -var=foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -var=foo --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when -var=foo --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -var=foo --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -var=foo --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 29,
 'description': 'when: Check if --if-var and --if-var-is-foo appears (with --var bar)',
 'send': 'argparse-shell-complete-test when --var bar --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --var bar --if-
--if-var         --if-var-is-foo
> argparse-shell-complete-test when --var bar --if-var\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --var bar --if-var
--if-var              (Only show option if --var is given)
--if-var-is-foo  (Only show option if --var is foo or bar)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when --var bar --if-var
--if-var-is-foo  -- Only show option if --var is foo or bar
--if-var         -- Only show option if --var is given\
'''
},

{
 'number': 30,
 'description': 'when: Check if --if-optional appears (with -O)',
 'send': 'argparse-shell-complete-test when -O --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -O --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -O --if-optional\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when -O --if-optional=\
'''
},

{
 'number': 31,
 'description': 'when: Check if --if-optional appears (with --optional)',
 'send': 'argparse-shell-complete-test when --optional --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --optional --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --optional --if-optional\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when --optional --if-optional=\
'''
},

{
 'number': 32,
 'description': 'when: Check if --if-optional appears (with -optional)',
 'send': 'argparse-shell-complete-test when -optional --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -optional --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -optional --if-optional\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test when -optional --if-optional=\
'''
},

{
 'number': 33,
 'description': 'when: Check if --if-optional and --if-optional-is-foo appears (with -Ofoo)',
 'send': 'argparse-shell-complete-test when -Ofoo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -Ofoo --if-
--if-optional         --if-optional-is-foo
> argparse-shell-complete-test when -Ofoo --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -Ofoo --if-optional
…-optional       (Only show option if --optional is given)
…-optional-is-foo  (Only show option if --optional is foo)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -Ofoo --if-optional
--if-optional-is-foo  -- Only show option if --optional is foo
--if-optional         -- Only show option if --optional is given\
'''
},

{
 'number': 34,
 'description': 'when: Check if --if-optional and --if-optional-is-foo appears (with --optional=foo)',
 'send': 'argparse-shell-complete-test when --optional=foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when --optional=foo --if-
--if-optional         --if-optional-is-foo
> argparse-shell-complete-test when --optional=foo --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when --optional=foo --if-optional
…-optional       (Only show option if --optional is given)
…-optional-is-foo  (Only show option if --optional is foo)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when --optional=foo --if-optional
--if-optional-is-foo  -- Only show option if --optional is foo
--if-optional         -- Only show option if --optional is given\
'''
},

{
 'number': 35,
 'description': 'when: Check if --if-optional and --if-optional-is-foo appears (with -optional=foo)',
 'send': 'argparse-shell-complete-test when -optional=foo --if-',
 'bash_expected': '''\
> argparse-shell-complete-test when -optional=foo --if-
--if-optional         --if-optional-is-foo
> argparse-shell-complete-test when -optional=foo --if-optional\
''',
 'fish_expected': '''\
> argparse-shell-complete-test when -optional=foo --if-optional
…-optional       (Only show option if --optional is given)
…-optional-is-foo  (Only show option if --optional is foo)\
''',
 'zsh_tabs': 2,
 'zsh_expected': '''\
> argparse-shell-complete-test when -optional=foo --if-optional
--if-optional-is-foo  -- Only show option if --optional is foo
--if-optional         -- Only show option if --optional is given\
'''
},

{
 'number': 36,
 'description': 'complete: Check --exec',
 'send': 'argparse-shell-complete-test complete --exec ',
 'bash_expected': '''\
> argparse-shell-complete-test complete --exec
Item\\ 1  Item\\ 2
> argparse-shell-complete-test complete --exec Item\\\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --exec Item\\
Item 1  (Description 1)  Item 2  (Description 2)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --exec Item\\\
'''
},

{
 'number': 37,
 'description': 'complete: Check --choices',
 'send': 'argparse-shell-complete-test complete --choices ',
 'bash_expected': '''\
> argparse-shell-complete-test complete --choices
1        2        foo:bar
> argparse-shell-complete-test complete --choices\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --choices
1  (one)  2  (two)  foo:bar  (Description for foo:bar)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --choices
1        -- one
2        -- two
foo:bar  -- Description for foo:bar\
'''
},

{
 'number': 38,
 'description': 'complete: Check --value-list #1',
 'send': 'argparse-shell-complete-test complete --value-list ',
 'bash_expected': '''\
> argparse-shell-complete-test complete --value-list
bar  baz  foo
> argparse-shell-complete-test complete --value-list\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --value-list
bar  (Complete a list)  baz  (Complete a list)  foo  (Complete a list)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --value-list
bar  baz  foo\
'''
},

{
 'number': 39,
 'description': 'complete: Check --value-list #2',
 'send': 'argparse-shell-complete-test complete --value-list f',
 'bash_expected': '''\
> argparse-shell-complete-test complete --value-list foo\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --value-list foo\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --value-list foo,\
'''
},

{
 'number': 40,
 'description': 'complete: Check --value-list #3',
 'send': 'argparse-shell-complete-test complete --value-list foo',
 'bash_expected': '''\
> argparse-shell-complete-test complete --value-list foo\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --value-list foo\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --value-list foo,\
'''
},

{
 'number': 41,
 'description': 'complete: Check --value-list #4',
 'send': 'argparse-shell-complete-test complete --value-list foo,baz,',
 'bash_expected': '''\
> argparse-shell-complete-test complete --value-list foo,baz,bar\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --value-list foo,baz,
foo,baz,bar  (Complete a list)  foo,baz,foo  (Complete a list)
foo,baz,baz  (Complete a list)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --value-list foo,baz,bar,\
'''
},

{
 'number': 42,
 'description': 'complete: Check --range-1',
 'send': 'argparse-shell-complete-test complete --range-1 ',
 'bash_expected': '''\
> argparse-shell-complete-test complete --range-1
1  2  3  4  5  6  7  8  9
> argparse-shell-complete-test complete --range-1\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --range-1
1  (Complete a range)  4  (Complete a range)  7  (Complete a range)
2  (Complete a range)  5  (Complete a range)  8  (Complete a range)
3  (Complete a range)  6  (Complete a range)  9  (Complete a range)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --range-1
1  2  3  4  5  6  7  8  9\
'''
},

{
 'number': 43,
 'description': 'complete: Check --range-2',
 'send': 'argparse-shell-complete-test complete --range-2 ',
 'bash_expected': '''\
> argparse-shell-complete-test complete --range-2
1  3  5  7  9
> argparse-shell-complete-test complete --range-2\
''',
 'fish_expected': '''\
> argparse-shell-complete-test complete --range-2
1  (Complete a range)  5  (Complete a range)  9  (Complete a range)
3  (Complete a range)  7  (Complete a range)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test complete --range-2
1  3  5  7  9\
'''
},

{
 'number': 44,
 'description': 'Check if positionals are working (1st positional)',
 'send': 'argparse-shell-complete-test test ',
 'bash_expected': '''\
> argparse-shell-complete-test test
first1  first2  first3
> argparse-shell-complete-test test first\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test first
first1  (First positional)  first3  (First positional)
first2  (First positional)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test first\
'''
},

{
 'number': 45,
 'description': 'Check if positionals are working (2nd positional)',
 'send': 'argparse-shell-complete-test test first1 ',
 'bash_expected': '''\
> argparse-shell-complete-test test first1
second1  second2
> argparse-shell-complete-test test first1 second\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test first1 second
second1  (Second positional)  second2  (Second positional)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test first1 second\
'''
},

{
 'number': 46,
 'description': 'Check if positionals are working (3rd positional)',
 'send': 'argparse-shell-complete-test test first1 second1 ',
 'bash_expected': '''\
> argparse-shell-complete-test test first1 second1
repeated1  repeated2
> argparse-shell-complete-test test first1 second1 repeated\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test first1 second1 repeated
repeated1  (Repeated positional)  repeated2  (Repeated positional)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test first1 second1 repeated\
'''
},

{
 'number': 47,
 'description': 'Check if positionals are working (repeated positional)',
 'send': 'argparse-shell-complete-test test first1 second1 repeated1 ',
 'bash_expected': '''\
> argparse-shell-complete-test test first1 second1 repeated1
repeated1  repeated2
> argparse-shell-complete-test test first1 second1 repeated1 repeated\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test first1 second1 repeated1 repeated
repeated1  (Repeated positional)  repeated2  (Repeated positional)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test first1 second1 repeated1 repeated\
'''
},

{
 'number': 48,
 'description': 'Check if aliases are working (alias1)',
 'send': 'argparse-shell-complete-test alias1 --arg ',
 'bash_expected': '''\
> argparse-shell-complete-test alias1 --arg
1  2  3
> argparse-shell-complete-test alias1 --arg\
''',
 'fish_expected': '''\
> argparse-shell-complete-test alias1 --arg
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test alias1 --arg
1  2  3\
'''
},

{
 'number': 49,
 'description': 'Check if aliases are working (alias2)',
 'send': 'argparse-shell-complete-test alias2 --arg ',
 'bash_expected': '''\
> argparse-shell-complete-test alias2 --arg
1  2  3
> argparse-shell-complete-test alias2 --arg\
''',
 'fish_expected': '''\
> argparse-shell-complete-test alias2 --arg
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test alias2 --arg
1  2  3\
'''
},

]