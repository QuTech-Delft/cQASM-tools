from Compile import compile
import unittest

### TODO: add more tests, possibly with randomized unitaries and circuits, and simulate to check equivalence modulo global phase?


class DecomposeTests(unittest.TestCase):
    def test_random(self):
        cqasm = r"""
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

rz q[0], -0.20000000000000018
x90 q[0]
rz q[0], 1.5707963267948957
x90 q[0]
rz q[0], 1.5707963267949
x90 q[1]
rz q[1], 1.5707963267948966
x90 q[1]
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

        output = compile(cqasm)

        assert(output == expected)

if __name__ == '__main__':
    unittest.main()