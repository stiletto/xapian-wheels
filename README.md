# xapian-wheels

This project is a lazy attempt at wrapping xapian's autotools-based build system in setuptools
to allow installing xapian and its bindings via pip, poetry and setup.py.

When you attempt to build it, this package downloads xapian and xapian-bindings and compiles them
making it possible to build a wheel containing both bindings and xapian-core not requiring any external dependencies.

I also provide binary wheels for Python 3.5 to 3.8 via [GitHub releases](https://github.com/stiletto/xapian-wheels/releases).

These scripts are distributed on the terms of [Do What The Fuck You Want To Public License version 2](./COPYING)
