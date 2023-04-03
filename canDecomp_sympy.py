from sympy import Matrix, log, sqrt, det  # , cos, sin, exp
from sympy.physics.quantum import TensorProduct, Dagger
import itertools


# Calculating the decomposition of U = K1 * A * K2

# A = Matrix([
#     [cos(alpha - beta) * exp(1j * gamma), 0, 0, 1j * sin(alpha - beta) * exp(1j * gamma)],
#     [0, cos(alpha + beta) * exp(-1j * gamma), 1j * sin(alpha + beta) * exp(-1j * gamma), 0],
#     [0, 1j * sin(alpha + beta) * exp(-1j * gamma), cos(alpha + beta) * exp(-1j * gamma), 0],
#     [1j * sin(alpha - beta) * exp(1j * gamma), 0, 0, cos(alpha - beta) * exp(1j * gamma)]]
#     )

# Matrix Q transforms the standard basis into the magic basis.
Q = Matrix([
    [1, 0, 0, 1j],
    [0, 1j, 1, 0],
    [0, 1j, -1, 0],
    [1, 0, 0, -1j]]
    ) / sqrt(2)

Q_dag = Dagger(Q)

# Pauli single-qubit operator matrices
Id = Matrix([  # Keyword I is reserved for imaginary numbers.
    [1, 0],
    [0, 1]]
    )
X = Matrix([
    [0, 1],
    [1, 0]]
    )
Y = Matrix([
    [0, -1j,],
    [1j, 0]]
    )
Z = Matrix([
    [1, 0],
    [0, -1]]
    )

XX = TensorProduct(X, X)
YY = TensorProduct(Y, Y)
ZZ = TensorProduct(Z, Z)


def _U_2_Umb(U: Matrix) -> Matrix:
    return Q_dag @ U @ Q


def _Umb_2_U(Umb: Matrix) -> Matrix:
    return Q @ Umb @ Q_dag


def _vectors_2_matrix(vectors: list) -> Matrix:
    M = vectors[0]
    for vec in vectors[1:]:
        M = M.row_join(vec)
    return M


if __name__ == '__main__':

    U_test = Matrix([
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 1, -1, 0],
        [1, 0, 0, -1]]
        ) / sqrt(2)

    Umb = _U_2_Umb(U_test)

    M = Umb.T @ Umb

    eigs = [(eigval, eigvec[0]) for (eigval, _, eigvec) in
        M.eigenvects()]

    for permutation in itertools.permutations(eigs):
        eigvals = [eig[0] for eig in permutation]
        eigvecs = [eig[1] for eig in permutation]
        O2 = _vectors_2_matrix(eigvecs).T
        if int(det(O2)) == 1:
            break

    l1, l2, l3, l4 = eigvals
    alpha = 1j / 4 * log(l1 * l2 / (l3 * l4))
    beta = 1j / 4 * log(l2 * l4 / (l1 * l3))
    gamma = 1j / 4 * log(l1 * l4 / (l2 * l3))
