"""conftest

``pytest`` fixtures for ``modeled.netconf`` tests.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from imp import find_module, load_module

from path import Path
import yaml

import pytest


TEST_PATH = Path(__file__).realpath().dirname()


# load python module containing a modeled TuringMachine example class
# from this directory
TURING_MACHINE_MODULE = load_module('turing_machine', *find_module(
    'turing_machine', [TEST_PATH]))


@pytest.fixture(scope='module')
def turing_machine_cls(request):
    """The modeled ``TuringMachine`` example class.
    """
    return TURING_MACHINE_MODULE.TuringMachine


@pytest.fixture(scope='module')
def turing_machine_netconf_namespace(request):
    """The NETCONF namespace to use for creating a YANG definition
       for the modeled ``TuringMachine`` example class.
    """
    return 'https://netconf.modeled.io/turing-machine'


@pytest.fixture(scope='module')
def turing_machine_program(request):
    """A unary number addition program
       for the ``TuringMachine`` example class.
    """
    with open(TEST_PATH / 'turing_machine-program.yaml') as f:
        return yaml.load(f)
