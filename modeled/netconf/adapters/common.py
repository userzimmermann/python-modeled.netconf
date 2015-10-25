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

"""modeled.netconf.adapters.common

Common definitions for ``modeled.netconf`` YANG adapter classes.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

import pyang.plugin

__all__ = ['TYPES', 'PYANG_PLUGINS']


# gets filled with all availabe pyang output format plugins
PYANG_PLUGINS = {}

# register pyang plugins according to code in pyang script
pyang.plugin.init([])
for plugin in pyang.plugin.plugins:
    plugin.add_output_format(PYANG_PLUGINS)
del plugin


# map Python types to YANG types
TYPES = {
    int: 'int64',
    str: 'string'
}
