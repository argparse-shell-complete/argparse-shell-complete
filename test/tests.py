tests = [

{'generate-scripts': []},

{
 'number': 1,
 'description': 'No arguments, check if all commands are listed',
 'send': 'argparse-shell-complete-test ',
 'bash_expected': '''\
> argparse-shell-complete-test
argparse-actions  subcommand        when
complete          test
> argparse-shell-complete-test\
''',
 'fish_expected': '''\
> argparse-shell-complete-test
argparse-actions  (argparse tool actions)  test  (For testing the completer)
complete         (Test complete commands)  when    (Test the "when"-feature)
subcommand      (Test nested subcommands)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test
argparse-actions  -- argparse tool actions
complete          -- Test complete commands
subcommand        -- Test nested subcommands
test              -- For testing the completer
when              -- Test the "when"-feature\
'''
},

{
 'number': 2,
 'description': 'Check if subcommand is completed',
 'send': 'argparse-shell-complete-test a',
 'bash_expected': '''\
> argparse-shell-complete-test argparse-actions\
''',
 'fish_expected': '''\
> argparse-shell-complete-test argparse-actions\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test argparse-actions\
'''
},

{
 'number': 3,
 'description': 'Check if all options are listed',
 'send': 'argparse-shell-complete-test test -',
 'bash_expected': '''\
> argparse-shell-complete-test test -
-c                              --help
--choices                       --multiple-option
-choices                        --multiple-option-with-arg
--exclusive-1                   -o
--exclusive-2                   --optional
-f                              -optional
--flag                          --special-chars-in-description
-h
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
--arg                           -A
-arg                                -- Option with arg
--flag                          -F
-flag                               -- A option flag
--help                          -h  -- show this help message and exit
--optional                      -O
-optional                           -- Option with optional arg
--special-chars-in-description      -- Here are some special chars: $"'\\[]*`)\
'''
},

{
 'number': 4,
 'description': 'Check long option with argument (with space)',
 'send': 'argparse-shell-complete-test test --arg ',
 'bash_expected': '''\
> argparse-shell-complete-test test --arg
first1  first2  first3
> argparse-shell-complete-test test --arg first\
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
> argparse-shell-complete-test test --arg=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test --arg=argparse-shell-complete-test
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
first1  first2  first3
> argparse-shell-complete-test test -A first\
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
first1  first2  first3
> argparse-shell-complete-test test -arg first\
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
> argparse-shell-complete-test test -arg=\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -arg=argparse-shell-complete-test
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
> argparse-shell-complete-test test --optional=argparse-shell-complete-test
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
> argparse-shell-complete-test test -optional=argparse-shell-complete-test
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
--multiple-option           --multiple-option-with-arg
> argparse-shell-complete-test test --multiple-flag --multiple-option\
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
 'comment': 'ZSH does not provide an argument for -A',
 'send': 'argparse-shell-complete-test test -FA ',
 'bash_expected': '''\
> argparse-shell-complete-test test -FA
first1  first2  first3
> argparse-shell-complete-test test -FA first\
''',
 'fish_expected': '''\
> argparse-shell-complete-test test -FA
1  (Option with arg)  2  (Option with arg)  3  (Option with arg)\
''',
 'zsh_expected': '''\
> argparse-shell-complete-test test -FA
first1  first2  first3\
'''
},

{
 'number': 18,
 'description': 'Check option stacking (with optional argument)',
 'comment': 'FISH produces a bit of a wrong output',
 'send': 'argparse-shell-complete-test test -FO',
 'bash_expected': '''\
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
-h          -o          -optional   --var
--help      --optional  -v          -var
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
> argparse-shell-complete-test when -V value --if-\
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
> argparse-shell-complete-test when -V foo --if-\
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
> argparse-shell-complete-test when -Vfoo --if-optional\
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
> argparse-shell-complete-test when -O --if-\
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

]
