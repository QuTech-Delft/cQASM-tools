from TestInterpreter import getCircuitMatrix
import unittest
import numpy as np
import math

# Careful: getCircuitMatrix doesn't run type-checking

class TestInterpreterTest(unittest.TestCase):
    def test_hadamard(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[1] q

h q[0]
""")
        self.assertTrue(np.allclose(m, math.sqrt(.5) * np.array([
                [1, 1],
                [1, -1],
        ])))
    
    def test_doublehadamard(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[1] q

h q[0]
h q[0]
""")
        self.assertTrue(np.allclose(m, np.eye(2)))

    def test_triplehadamard(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[1] q

h q[0]
h q[0]
h q[0]
""")
        self.assertTrue(np.allclose(m, math.sqrt(.5) * np.array([
                [1, 1],
                [1, -1],
        ])))

    def test_hadamardx(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[2] q

h q[0]
x q[1]
""")
        self.assertTrue(np.allclose(m, math.sqrt(.5) * np.array([
                [0, 0, 1, 1],
                [0, 0, 1, -1],
                [1, 1, 0, 0],
                [1, -1, 0, 0],
        ])))

    def test_xhadamard(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[2] q

h q[1]
x q[0]
""")
        self.assertTrue(np.allclose(m, math.sqrt(.5) * np.array([
                [0, 1, 0, 1],
                [1, 0, 1, 0],
                [0, 1, 0, -1],
                [1, 0, -1, 0],
        ])))

    def test_cnot(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[2] q

cnot q[1], q[0]
""")

        self.assertTrue(np.allclose(m, np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
        ])))

    def test_cnot_reversed(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[2] q

cnot q[0], q[1]
""")

        self.assertTrue(np.allclose(m, np.array([
                [1, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
        ])))

    def test_hadamard_cnot(self):
        m = getCircuitMatrix(r"""
version 3.0
qubit[2] q

h q[0]
cnot q[0], q[1]
""")

        self.assertTrue(np.allclose(m, math.sqrt(.5) * np.array([
                [1, 1, 0, 0],
                [0, 0, 1, -1],
                [0, 0, 1, 1],
                [1, -1, 0, 0],
        ])))


if __name__ == '__main__':
    unittest.main()