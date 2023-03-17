# KAK decomposition with cirq

import cirq
import numpy as np

gate = np.array([[1, 0, 0, 0],
                 [0, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1]])

result = cirq.kak_decomposition(gate)

print(result)