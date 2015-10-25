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

"""modeled.netconf.adapters.module

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass
from inspect import getmembers, getargspec
from datetime import date

from moretools import decamelize

import modeled

from netconf.server import \
    NetconfSSHServer, SSHUserPassController, NetconfMethods

from pyang.statements import Statement

from .common import TYPES
from .container import YANGContainer, YANGContainerMeta

__all__ = ['YANGModule', 'rpc']


def rpc(func=None, returntype=None, argtypes=None):
    if func is None:
        def rpc(func):
            global rpc
            return rpc(func, returntype, argtypes)

        return rpc

    method = modeled.typed(func, returntype, argtypes)
    method.__isnetconfrpc__ = True
    return method


class YANGModuleMeta(YANGContainerMeta):
    """Metaclass for :class:`modeled.netconf.YANGModule`,
       which wraps a :class:`modeled.object` as YANG module.
    """
    def to_statement(cls, namespace=None, prefix=None, revision=None):
        """Get YANG module as :class:`pyang.statement.Statement` instance,
           ready for feeding to a pyang output plugin.
        """
        # adapted modeled class is used as YANG module and main container
        module = Statement(None, None, None, 'module', cls.yangname)
        if not prefix:
            prefix = decamelize(cls.__name__, joiner='-')
        if namespace:
            namespace = Statement(None, module, None, 'namespace', namespace)
            module.substmts.append(namespace)
        prefix = Statement(None, module, None, 'prefix', prefix)
        module.substmts.append(prefix)
        if not revision:
            revision = str(date.today())
        revision = Statement(None, module, None, 'revision', revision)
        module.substmts.append(revision)
        container = super(YANGModuleMeta, cls).to_statement(parent=module)
        module.substmts.append(container)
        # add defined @rpc methods
        for name, obj in getmembers(cls):
            if getattr(obj, '__isnetconfrpc__', False):
                method = obj
                yangname = name.replace('_', '-')
                rpc = Statement(None, module, None, 'rpc', yangname)
                module.substmts.append(rpc)
                if method.__doc__:
                    description = Statement(
                        None, rpc, None, 'description',
                        method.__doc__.strip())
                    rpc.substmts.append(description)
                # if the rpc method has args then add an input statement,
                # containing a leaf statement for every arg
                argspec = getargspec(method)
                if len(argspec.args) > 1:  # ignore 'self'
                    input_ = Statement(None, rpc, None, 'input', None)
                    rpc.substmts.append(input_)
                    for name in argspec.args[1:]:
                        yangname = name.replace('_', '-')
                        mtype = method.mtypes[name]
                        statement = cls.member_to_statement(
                            mtype, yangname=yangname, parent=input_)
                        input_.substmts.append(statement)
        return module

    def __getattr__(cls, name):
        """Dynamically provide ``to_<format>()`` serializer methods.
        """
        # get method from YANGContainerMeta base
        method = super(YANGModuleMeta, cls).__getattr__(name)
        # and change method doc string (container-->module)
        format = name[3:]
        method.__doc__ \
            = "Serialize YANG module to %s format." % repr(format)
        return method

    def rpc_to_server_method(cls, method, minstance):
        def server_method(self, unused_session, rpc, *unused_params):
            method(minstance)

        server_method.__name__ = 'rpc_' + method.__name__
        return server_method


class YANGModule(with_metaclass(YANGModuleMeta, YANGContainer)):
    """Wraps a :class:`modeled.object` as YANG module.

    - Also uses wrapped class for main container definition.
    """
    def serve(self, port, host_key, username, password):
        cls = type(self)
        server_methods_clsattrs = {}
        for name, obj in getmembers(type(self)):
            if getattr(obj, '__isnetconfrpc__', False):
                method = obj
                server_method = cls.rpc_to_server_method(
                    method, minstance=self)
                server_methods_clsattrs[server_method.__name__] \
                    = server_method
        server_methods = type(
            'Methods', (NetconfMethods, ), server_methods_clsattrs
        )()
        auth = SSHUserPassController(username=username, password=password)
        return NetconfSSHServer(
            server_ctl=auth, server_methods=server_methods,
            port=port, host_key=host_key)
