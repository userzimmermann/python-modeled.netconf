"""turing_machine

A modeled ``TuringMachine`` example class for ``modeled.netconf`` tests.

- Modeled after the Turing Machine example from the ``pyang`` `tutorial
  <https://github.com/mbj4668/pyang/wiki/Tutorial>`_

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import print_function

import modeled

__all__ = ['TuringMachine']


class Input(modeled.object):
    state = modeled.member[int]()
    symbol = modeled.member[str]()


class Output(modeled.object):
    state = modeled.member[int]()
    symbol = modeled.member[str]()
    head_move = modeled.member[str]['L', 'R']('R')


class Transition(modeled.object):
    input = modeled.member[Input]()
    output = modeled.member[Output]()

    def __init__(self, input, output):
        """Expects `input` as `output` as mappings.
        """
        self.input = Input(
            # modeled.object.__init__ supports **kwargs
            # for initializing modeled.member values
            **dict(input))
        self.output = Output(**dict(output))


class TuringMachine(modeled.object):
    state = modeled.member[int]()
    head_position = modeled.member[int]()
    tape = modeled.member.list[str]()
    transitions = modeled.member.dict[str, Transition]()

    def __init__(self, transitions):
        modeled.object.__init__(self, transitions={})
        transitions = dict(transitions)
        for name, (input, output) in transitions.items():
            self.transitions[name] = Transition(input, output)

    def run(self):
        while True:
            if 0 <= self.head_position < len(self.tape):
                symbol = self.tape[self.head_position]
            else:
                symbol = None
            for name, trans in self.transitions.items():
                if self.state == trans.input.state \
                        and symbol == trans.input.symbol:
                    print(self.tape, end=" ")
                    if trans.output.state is not None:
                        self.state = trans.output.state
                    if trans.output.symbol is not None:
                        self.tape[self.head_position] \
                            = trans.output.symbol
                    self.head_position \
                        += {'L': -1, 'R': 1}[trans.output.head_move]
                    print("-->", self.tape)
                    break
            else:
                break
