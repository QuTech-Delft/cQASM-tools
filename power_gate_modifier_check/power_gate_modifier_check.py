from sympy import cos, sin, exp, simplify, N, conjugate
from sympy.physics.quantum import Dagger, TensorProduct

import numpy as np

from clifford_gates import *


class Gate:

    def __init__(
            self,
            name: str = "",
            params: tuple = None,
            matrix: Matrix = None,
    ) -> None:
        self.name = name
        self.params = params
        self._matrix = matrix

    @property
    def matrix(self) -> Matrix:
        return self._matrix

    @matrix.setter
    def matrix(self, value: Matrix) -> None:
        self._matrix = value

    def pow(self, power: float) -> Matrix:
        P, D = self._matrix.diagonalize(normalize=True)
        D_raised = D.applyfunc(lambda e: e**power)
        return P * D_raised * Dagger(P)

    def pow_check(self, power: float) -> bool:
        pow_matrix = np.asarray(N(simplify(self.pow(power))), dtype=complex)
        n, theta, phi = self.params
        theta *= power
        phi *= power
        rn_pow_matrix = np.asarray(N(simplify(Gate.rn(n, theta, phi))), dtype=complex)
        return np.allclose(rn_pow_matrix, pow_matrix, atol=1E-8)

    def rn_matrix(self) -> Matrix:
        return Gate.rn(*self.params)

    @staticmethod
    def rn(n: tuple[int, int, int], theta: float, phi: float):
        phase = exp(1j * phi)
        nx, ny, nz = n
        Im = Matrix([[1, 0], [0, 1]])
        Xm = Matrix([[0, 1], [1, 0]])
        Ym = Matrix([[0, -1j], [1j, 0]])
        Zm = Matrix([[1, 0], [0, -1]])
        Can1 = (cos(theta / 2) * Im - 1j * sin(theta / 2) * (nx * Xm + ny * Ym + nz * Zm))
        return phase * Can1

    def ctrl_pow(self, power: float) -> Matrix:
        outer_0 = Matrix([[1, 0], [0, 0]])
        outer_1 = Matrix([[0, 0], [0, 1]])
        Im = Matrix([[1, 0], [0, 1]])
        return TensorProduct(outer_0, Im) + TensorProduct(outer_1, self.pow(power))


if __name__ == '__main__':

    def result_check(result: Matrix):
        print(result)
        amplitudes = result.tolist()
        probabilities = [simplify(amplitude[0] * conjugate(amplitude[0])) for amplitude in amplitudes]
        for i, probability in enumerate(probabilities):
            print(f'{i:02b}: {probability}')
        print("Born rule check: ", abs(sum(probabilities) - 1) <= 1e-8)
        print()

    result = N(Z.pow(1 / 2) * Matrix([[1], [0]]))
    result_check(result)

    result = N(X.pow(1 / 2) * Matrix([[1], [0]]))
    result_check(result)

    result = N(X.pow(1 / 4) * Matrix([[1], [0]]))
    result_check(result)

    result = N(H1.pow(1) * Matrix([[1], [0]]))
    result_check(result)

    result = N(H1.pow(1 / 2) * Matrix([[1], [0]]))
    result_check(result)

    result = N(H1.pow(1 / 4) * Matrix([[1], [0]]))
    result_check(result)

    result = N(H1.pow(pi / 10) * Matrix([[1], [0]]))
    result_check(result)

    result = N(X.pow(pi / 4) * H1.pow(1 / 2) * Matrix([[1], [0]]))
    result_check(result)

    result = N(H1.ctrl_pow(1/3)) * Matrix([[0], [0], [0], [1]])
    result_check(result)

    Rx = Gate(
        name="Rx(pi)",
        params=((1, 0, 0), pi, 0),
        matrix=Gate.rn((1, 0, 0), pi, 0)
    )

    result = N(TensorProduct(X.pow(1/2), I.matrix) * X.ctrl_pow(1)) * TensorProduct(I.matrix, H1.matrix) * Matrix([[0], [0], [1], [0]])
    result_check(result)

    result = N(TensorProduct(X.pow(1/2), I.matrix) * Rx.ctrl_pow(1)) * TensorProduct(I.matrix, H1.matrix) * Matrix([[0], [0], [1], [0]])
    result_check(result)
