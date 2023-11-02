from src.Circuit import Circuit
from src.Common import ATOL
from test.TestGates import TEST_GATES
from test.TestHelpers import areMatricesEqualUpToGlobalPhase
import unittest
import numpy as np

class DecomposeMcKayTests(unittest.TestCase):
    def checkMcKayDecomposition(self, cqasm3_string):
        """
            Check whether the mcKay decomposition transformation applied to the input string preserves the
            circuit matrix up to an irrelevant global phase factor.
        """

        circuit = Circuit(TEST_GATES, cqasm3_string)

        # Store matrix before decompositions.
        expectedMatrix = circuit.test_get_circuit_matrix()

        circuit.decompose_mckay()
        
        # Get matrix after decompositions.
        actualMatrix = circuit.test_get_circuit_matrix()

        self.assertTrue(areMatricesEqualUpToGlobalPhase(actualMatrix, expectedMatrix))

    def test_one(self):
        cqasm = r"""
version 3.0

qubit[2] squirrel

// iuwhefjwn

/* This is a multi-
        line comment block */

ry squirrel[0], 23847628349.123
rx squirrel[0], 29384672.234
rz squirrel[0], 9877.87634
"""

        self.checkMcKayDecomposition(cqasm)

    def test_two(self):
        cqasm = r"""
version 3.0

qubit[2] squirrel

ry squirrel[0], 23847628349.123
cnot squirrel[0], squirrel[1]
rx squirrel[1], 29384672.234
rz squirrel[0], 9877.87634
cnot squirrel[0], squirrel[1]
rx squirrel[1], 29384672.234
rz squirrel[0], 9877.87634
"""

        self.checkMcKayDecomposition(cqasm)

    def test_smallrandom(self):
        cqasm3 = r"""
        version 3.0
        qubit[4] q

        H q[2]
        cr q[2], q[3], 2.123
        H q[1]
        H q[0]
        H q[2]
        H q[1]
        H q[0]
        cr q[2], q[3], 2.123
    
"""

        expected = """version 3.0

qubit[4] q

x90 q[2]
rz q[2], 1.5707963267948966
x90 q[2]
cr q[2], q[3], 2.123
x90 q[2]
rz q[2], 1.5707963267948966
x90 q[2]
cr q[2], q[3], 2.123
"""

        circuit = Circuit(TEST_GATES, cqasm3)

        circuit.decompose_mckay()

        output = str(circuit)

        self.assertEqual(output, expected)

    def test_random(self):
        cqasm3 = r"""
        version 3.0

        // This is a single line comment which ends on the newline.
        // The cQASM string must begin with the version instruction even before any comments.

        /* This is a multi-
        line comment block */


        qubit[4] q   //declaration

        //let us create a Bell state on 2 qubits and a |+> state on the third qubit

        H q[2]
        H q[1]
        H q[0]
        RZ q[0], 1.5707963267949
        RY q[0], -0.2
        cnot q[1], q[0]
        RZ q[0], 1.5789
        cnot q[1], q[0]
        cnot q[1], q[2]
        RZ q[1], 2.5707963267949
        cr q[2], q[3], 2.123
        RY q[1], -1.5707963267949

        """

        expected = """version 3.0

qubit[4] q

x90 q[1]
rz q[1], 1.5707963267948966
x90 q[1]
rz q[0], -0.20000000000000018
x90 q[0]
rz q[0], 1.5707963267948957
x90 q[0]
rz q[0], 1.5707963267949
cnot q[1], q[0]
rz q[0], -2.352142653589793
x90 q[0]
rz q[0], 3.141592653589793
x90 q[0]
rz q[0], 0.7894500000000004
cnot q[1], q[0]
x90 q[2]
rz q[2], 1.5707963267948966
x90 q[2]
cnot q[1], q[2]
cr q[2], q[3], 2.123
rz q[1], 2.5707963267949
x90 q[1]
rz q[1], 1.570796326794893
x90 q[1]
rz q[1], 3.141592653589793
"""

        circuit = Circuit(TEST_GATES, cqasm3)

        circuit.decompose_mckay()

        output = str(circuit)

        print(output)
        self.assertEqual(output, expected)

if __name__ == '__main__':
    unittest.main()