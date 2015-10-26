# python-modeled.netconf
#
# Extremely Pythonized NETCONF and YANG
#
# Copyright (C) 2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# python-modeled.netconf is free software:
# you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-modeled.netconf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python-modeled.netconf.
# If not, see <http://www.gnu.org/licenses/>.

"""modeled.netconf.yang.rpc

Provides ``@modeled.netconf.rpc`` method decorator
for ``modeled.netconf.YANG`` adapted ``modeled.object`` classes.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

import modeled

__all__ = ['rpc']


def rpc(func=None, argtypes=None, returntype=None):
    if func is None:
        def rpc(func):
            global rpc
            return rpc(func, argtypes, returntype)

        return rpc

    method = modeled.typed(func, argtypes, returntype)
    method.__isnetconfrpc__ = True
    return method
