"""test_adapters

Test ``modeled.netconf`` YANG adapters.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from datetime import date

from path import Path

import modeled
from modeled.netconf import YANGContainer, YANGModule, rpc

import pyang
import pyang.plugin


TEST_PATH = Path(__file__).realpath().dirname()


# gets filled with all availabe pyang output format plugins
PYANG_PLUGINS = {}

# register plugins according to pyang script
pyang.plugin.init([])
for plugin in pyang.plugin.plugins:
    plugin.add_output_format(PYANG_PLUGINS)
del plugin


def test_container_class():
    """Check ``modeled.netconf.YANGContainer`` adapter class.
    """
    assert issubclass(YANGContainer, modeled.Adapter)

    for name in PYANG_PLUGINS:
        methodname = 'to_' + name
        assert methodname in dir(YANGContainer)
        assert callable(getattr(YANGContainer, methodname))


def test_module_class():
    """Check ``modeled.netconf.YANGModule`` adapter class.
    """
    assert issubclass(YANGModule, YANGContainer)

    for name in PYANG_PLUGINS:
        methodname = 'to_' + name
        assert methodname in dir(YANGModule)
        assert callable(getattr(YANGModule, methodname))


def test_module(turing_machine_cls, turing_machine_netconf_namespace):
    """Test ``modeled.netconf.YANGModule`` adapter
       with the modeled `turing_machine_cls` fixture.
    """
    class TM(YANGModule[turing_machine_cls]):

        @rpc(argtypes={'tape_content': str})
        def initialize(self, tape_content):
            """Initialize the Turing Machine.
            """
            self.state = 0
            self.head_position = 0
            self.tape = tape_content

        @rpc(argtypes={})
        def run(self):
            """Start the Turing Machine operation.
            """
            TuringMachine.run(self)

    assert issubclass(TM, turing_machine_cls)
    assert issubclass(TM, YANGModule)

    with open(TEST_PATH / 'turing-machine.yang') as f:
        assert f.read() == TM.to_yang(
            namespace=turing_machine_netconf_namespace,
            revision=str(date(2015, 10, 24)))
