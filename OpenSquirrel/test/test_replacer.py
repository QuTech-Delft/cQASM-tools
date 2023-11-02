import unittest
from test.TestGates import TEST_GATES
from src.SquirrelAST import SquirrelAST
from src.Replacer import Replacer

def hadamard_decomposition(q):
    return [
        ("y90", (q,)),
        ("x", (q,)),
    ]

class ReplacerTest(unittest.TestCase):
    def test_replace(self):
        squirrelAST = SquirrelAST(TEST_GATES, 3, "test")

        replacer = Replacer(TEST_GATES)

        squirrelAST.addGate("h", 0)

        replaced = replacer.process(squirrelAST, "h", hadamard_decomposition)

        assert replaced.nQubits == 3
        assert replaced.qubitRegisterName == "test"
        assert len(replaced.operations) == 2
        assert replaced.operations[0] == ("y90", (0,))
        assert replaced.operations[1] == ("x", (0,))