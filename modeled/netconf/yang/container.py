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

"""modeled.netconf.yang.container

Provides ``modeled.netconf.YANGContainer`` adapter class,
which wraps ``modeled.object`` classes as YANG containers.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass
from itertools import chain
from six.moves import StringIO
from optparse import OptionParser

from moretools import decamelize

import modeled
from modeled import ismodeledclass

import pyang
from pyang.statements import Statement

from .common import TYPES, PYANG_PLUGINS

__all__ = ['YANGContainer']


class DummyRepository(pyang.Repository):
    """Dummy implementation of abstract :class:`pyang.Repository`
       for :class:`pyang.Context` instantiations
       created by :meth:`modeled.netconf.YANGContainerMeta.to`.
    """
    def get_modules_and_revisions(self, ctx):
        """Just a must-have dummy method, returning empty ``tuple``.

        - Modules are always explicitly given to pyang output plugins
          by :meth:`modeled.netconf.YANGContainerMeta.to`.
        """
        return ()


class YANGContainerMeta(modeled.AdapterMeta):
    """Metaclass for :class:`modeled.netconf.YANGContainer`,
       which wraps a :class:`modeled.object` as YANG container.
    """
    @property
    def yangname(cls):
        """Generate YANG container name
           by decamelizing modeled class name with hyphen separators.
        """
        return decamelize(cls.mclass.model.name, joiner='-')

    def mtype_to_statement(cls, mtype, yangname, parent=None):
        if ismodeledclass(mtype):
            return YANGContainer[mtype].to_statement(
                yangname=yangname, parent=parent)

        leaf = Statement(None, parent, None, 'leaf', yangname)
        # if member.title:
        #     description = Statement(
        #         None, leaf, None, 'description', member.title)
        #     leaf.substmts.append(description)
        type_ = Statement(None, leaf, None, 'type', TYPES[mtype])
        leaf.substmts.append(type_)
        return leaf

    def member_to_statement(cls, member, yangname, parent=None):
        if ismodeledclass(member.mtype):
            return YANGContainer[member.mtype].to_statement(
                yangname=yangname, parent=parent)

        if member.islist():
            list_ = Statement(None, parent, None, 'list', yangname)
            yangindexname = member.indexname.replace('_', '-')
            key = Statement(None, list_, None, 'key', yangindexname)
            list_.substmts.append(key)
            leaf = Statement(None, list_, None, 'leaf', yangindexname)
            list_.substmts.append(leaf)
            type_ = Statement(None, leaf, None, 'type', TYPES[int])
            leaf.substmts.append(type_)
            yangitemname = member.itemname.replace('_', '-')
            statement = cls.mtype_to_statement(
                member.itemtype, yangname=yangitemname, parent=list_)
            list_.substmts.append(statement)
            return list_

        if member.isdict():
            list_ = Statement(None, parent, None, 'list', yangname)
            yangkeyname = member.keyname.replace('_', '-')
            key = Statement(None, list_, None, 'key', yangkeyname)
            list_.substmts.append(key)
            leaf = Statement(None, list_, None, 'leaf', yangkeyname)
            list_.substmts.append(leaf)
            type_ = Statement(
                None, leaf, None, 'type', TYPES[member.keytype])
            leaf.substmts.append(type_)
            yangvaluename = member.valuename.replace('_', '-')
            statement = cls.mtype_to_statement(
                member.valuetype, yangname=yangvaluename, parent=list_)
            list_.substmts.append(statement)
            return list_

        return cls.mtype_to_statement(
            member.mtype, yangname=yangname, parent=parent)

    def to_statement(cls, yangname=None, parent=None):
        """Get YANG container as :class:`pyang.statement.Statement` instance,
           ready for feeding to a pyang output plugin.

        - If no `yangname` is given,
          a decamelized modeled class name joined by hyphens will be used.
        - Optionally binds statement to `parent` statement,
          like a module or a parent container.
        """
        container = Statement(
            None, parent, None, 'container', yangname or cls.yangname)
        # add modeled members as leafs or subcontainers to the main container
        for name, member in cls.mclass.model.members:
            yangname = name.replace('_', '-')
            statement = cls.member_to_statement(
                member, yangname=yangname, parent=container)
            container.substmts.append(statement)
        return container

    def to(cls, format, **options):
        """Serialize YANG container to the given output `format`.
        """
        # pyang output plugins need an output stream
        stream = StringIO()
        plugin = PYANG_PLUGINS[format]
        # register plugin options according to pyang script
        optparser = OptionParser()
        plugin.add_opts(optparser)
        # pyang output plugins also need a pyang.Context
        ctx = pyang.Context(DummyRepository())
        # which offers plugin-specific options (just take defaults)
        ctx.opts = optparser.parse_args([])[0]
        # ready to serialize!
        plugin.emit(ctx, [cls.to_statement(**options)], stream)
        # and return the resulting data
        stream.seek(0)
        return stream.read()

    def __getattr__(cls, name):
        """Dynamically provide ``to_<format>()`` serializer methods.
        """
        if name.startswith('to_'):
            format = name[3:]
            if format in PYANG_PLUGINS:
                def to_format(**options):
                    return cls.to(format, **options)

                to_format.__name__ = name
                to_format.__doc__ \
                    = "Serialize YANG container to %s format." % repr(format)
                return to_format
        raise AttributeError("%s has no attribute %s"
                             % (repr(cls), repr(name)))

    def __dir__(cls):
        """Additionally return all valid ``to_<format>()``
           serializer method names for dynamic creation
           via :meth:`__getattr__`.
        """
        return list(chain(super(YANGContainerMeta, cls).__dir__(),
                          ('to_%s' % format for format in PYANG_PLUGINS)))


class YANGContainer(with_metaclass(YANGContainerMeta, modeled.Adapter)):
    """Wraps a :class:`modeled.object` as YANG container.
    """
    pass
