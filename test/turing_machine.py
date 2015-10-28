"""turing_machine

A modeled ``TuringMachine`` example class for ``modeled.netconf`` tests.

- Modeled after the Turing Machine example from the ``pyang`` `tutorial
  <https://github.com/mbj4668/pyang/wiki/Tutorial>`_

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from __future__ import print_function

import modeled
from modeled import member

__all__ = ['TuringMachine']


class Input(modeled.object):
    """The input part of a Turing Machine program rule.
    """
    state = member[int]()
    symbol = member[str]()


class Output(modeled.object):
    """The output part of a Turing Machine program rule.
    """
    state = member[int]()
    symbol = member[str]()
    head_move = member[str]['L', 'R']('R')


class Rule(modeled.object):
    """A Turing Machine program rule.
    """
    input = member[Input]()
    output = member[Output]()

    def __init__(self, input, output):
        """Expects `input` as `output` as mappings.
        """
        self.input = Input(
            # modeled.object.__init__ supports **kwargs
            # for initializing modeled.member values
            **dict(input))
        self.output = Output(**dict(output))


class TuringMachine(modeled.object):
    state = member[int]()
    head_position = member[int]()

    # the list of symbols on the input/output tape
    tape = member.list[str](indexname='cell', itemname='symbol')

    # the machine program as named rules
    program = member.dict[str, Rule](keyname='name')

    def __init__(self, program):
        """Create a Turing Machine with the given `program`.
        """
        modeled.object.__init__(self, program={})
        program = dict(program)
        for name, (input, output) in program.items():
            self.program[name] = Rule(input, output)

    def run(self):
        """Start the Turing Machine.

        - Runs until no matching input part for current state and tape symbol
          can be found in the program rules.
        """
        print(" %s  %d" % (''.join(self.tape), self.state))
        while True:
            pos = self.head_position
            if 0 <= pos < len(self.tape):
                symbol = self.tape[pos]
            else:
                symbol = None
            for name, rule in self.program.items():
                if (self.state, symbol) == (rule.input.state, rule.input.symbol):
                    print("%s^%s --> %s" % (
                        ' ' * (pos + 1),
                        ' ' * (len(self.tape) - pos),
                        name))
                    if rule.output.state is not None:
                        self.state = rule.output.state
                    if rule.output.symbol is not None:
                        self.tape[pos] = rule.output.symbol
                    self.head_position += {'L': -1, 'R': 1}[rule.output.head_move]
                    print(" %s  %d" % (''.join(self.tape), self.state))
                    break
            else:
                break
