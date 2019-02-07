# Contributors

The contributors are listed here in alphabetical order

* Gregor von Laszewski (primary contact, laszewski@gmial.com) and
* Fugang Wang

put your names here (put your real names here and sort by lastname

* Vafa Andalibi,
  David Michael Demeulenaere,
  Bo Feng,
  Yu Luo,
  Rui Li, 
  Sachith Danushka Withana,
  Kimball Wu

Code Contributions can be seen at

* <https://github.com/cloudmesh-community/cm/graphs/contributors>

## Code Management

At this time we recommend and require that you use `pyCharm` community edition or profesional to edit your code. Before
committing we like that you run `Inspect Code ` on all files that you commit and fix as many errors as possible
including PEP8 format suggestions. It also notifies you of issues you may not think about while doing other code
inspection.

THe reason we ask you to do so is that pycharms code inspection is very good, and that if
everyone uses pycharm the format of the code is uinform and we do not run in to formatting issues.

This will make the review of any code contributed much easier.

Naturally you can use a different editor for your work, but we still ask you to use pycharm to fix formatting and 
code inspection before you commit.

Typically we run a code inspection every week.

## Documentation Management

To increase readability of the documentation we ask you to try to use 80 character line limits if possible. THis is
important for better editing experience in github. A good editor to do this with is emacs withe its `ESc-q` command and
pycharm with its `Edit-Wrap LIne to` column or paragraph features. ON macOS this can be called with
`CONTROL-SHIFT-COMMNAD-W` or `CONTROL-SHIFT-COMMNAD-P`

## Security Management (needs further investigation if useful and secure)

Some security risks can be shown with

```bash
$ pip install bandit
$ bandit -r ./cloudmesh 
```

