"""modeled

Just a develop mode proxy to the ``modeled`` base package,
which is used as namespace package for ``modeled.netconf``.

- This file will not be installed.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys
from path import Path
# search sys.path for other packages using modeled namespace
for path in (Path(p) / 'modeled' for p in sys.path):
    if path.isdir():
        __path__.append(path.realpath())
del sys, path, Path


from modeled.api import *
