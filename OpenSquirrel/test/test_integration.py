# This integration test also serves as example and code documentation.

import unittest
from src.Circuit import Circuit
from test.TestGates import TEST_GATES


class IntegrationTest(unittest.TestCase):
    def test_simple(self):
        myCircuit = Circuit(TEST_GATES, """
                version 3.0

                qubit[3] qreg

                ry qreg[0], 1.23
                RY qreg[1], 2.34           // Aliases for gates can be defined, here ry == RY
                cnot qreg[0], qreg[1]
                rx qreg[0], -2.3
                ry qreg[1], -3.14
            """)
        
        #    Decompose CNOT as
        #
        #    -----•-----        ------- Z -------
        #         |        ==           |
        #    -----⊕----        --- H --•-- H ---
        #

        myCircuit.replace("cnot", lambda control, target: [("h", (target,)), ("cz", (control, target)), ("h", (target,))])
        
        # Do 1q-gate fusion and decompose with McKay decomposition.

        myCircuit.decompose_mckay()

        # Write the transformed circuit as a cQasm3 string.

        output = str(myCircuit)

        assert output == """version 3.0

qubit[3] qreg

rz qreg[0], 3.141592653589793
x90 qreg[0]
rz qreg[0], 1.9115926535897927
x90 qreg[0]
rz qreg[1], 3.141592653589793
x90 qreg[1]
rz qreg[1], 2.37238898038469
x90 qreg[1]
rz qreg[1], 3.141592653589793
cz qreg[0], qreg[1]
rz qreg[1], 3.141592653589793
x90 qreg[1]
rz qreg[1], 1.57238898038469
x90 qreg[1]
rz qreg[1], 3.141592653589793
rz qreg[0], 1.5707963267948966
x90 qreg[0]
rz qreg[0], 0.8415926535897933
x90 qreg[0]
rz qreg[0], 1.5707963267948966
"""

