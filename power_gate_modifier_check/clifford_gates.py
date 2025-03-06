from sympy import Matrix, pi, sqrt

from power_gate_modifier_check import Gate

# Pauli gates: Half turns around primary axes

I = Gate(
    name="I",
    params=((0, 0, 1), 0, 0),
    matrix=Matrix([
        [1, 0],
        [0, 1]]
    )
)

X = Gate(
    name="X",
    params=((1, 0, 0), pi, pi / 2),
    matrix=Matrix([
        [0, 1],
        [1, 0]]
    )
)

Y = Gate(
    name="Y",
    params=((0, 1, 0), pi, pi / 2),
    matrix=Matrix([
        [0, -1j],
        [1j, 0]]
    )
)

Z = Gate(
    name="Z",
    params=((0, 0, 1), pi, pi / 2),
    matrix=Matrix([
        [1, 0],
        [0, -1]]
    )
)

# Quarter turns around primary axes

X90 = Gate(
    name="X90",
    params=((1, 0, 0), pi / 2, pi / 4),
    matrix=1 / 2 * Matrix([
        [1 + 1j, 1 - 1j],
        [1 - 1j, 1 + 1j]]
    )
)

mX90 = Gate(
    name="mX90",
    params=((1, 0, 0), -pi / 2, -pi / 4),
    matrix=1 / 2 * Matrix([
        [1 - 1j, 1 + 1j],
        [1 + 1j, 1 - 1j]]
    )
)

Y90 = Gate(
    name="Y90",
    params=((0, 1, 0), pi / 2, pi / 4),
    matrix=1 / 2 * Matrix([
        [1 + 1j, -1 - 1j],
        [1 + 1j, 1 + 1j]]
    )
)

mY90 = Gate(
    name="mY90",
    params=((0, 1, 0), -pi / 2, -pi / 4),
    matrix=1 / 2 * Matrix([
        [1 - 1j, 1 - 1j],
        [-1 + 1j, 1 - 1j]]
    )
)

Z90 = Gate(
    name="Z90",
    params=((0, 0, 1), pi / 2, pi / 4),
    matrix=Matrix([
        [1, 0],
        [0, 1j]]
    )
)

mZ90 = Gate(
    name="mZ90",
    params=((0, 0, 1), -pi / 2, -pi / 4),
    matrix=Matrix([
        [1, 0],
        [0, -1j]]
    )
)

# Eighth turn around Z and -Z axis

T = Gate(
    name="T",
    params=((0, 0, 1), pi / 4, pi / 8),
    matrix=Matrix([
        [1, 0],
        [0, (1 + 1j) / sqrt(2)]]
    )
)

Tdag = Gate(
    name="Tdag",
    params=((0, 0, 1), -pi / 4, -pi / 8),
    matrix=Matrix([
        [1, 0],
        [0, (1 - 1j) / sqrt(2)]]
    )
)

# Hadamard-like gates: Half turns around combined axes

H1 = Gate(
    name="H1",
    params=((1 / sqrt(2), 0, 1 / sqrt(2)), pi, pi / 2),
    matrix=Matrix([
        [1 / sqrt(2), 1 / sqrt(2)],
        [1 / sqrt(2), -1 / sqrt(2)]]
    )
)

H2 = Gate(
    name="H2",
    params=((1 / sqrt(2), 1 / sqrt(2), 0), pi, pi / 2),
    matrix=1 / sqrt(2) * Matrix([
        [0, 1 - 1j],
        [1 + 1j, 0]]
    )
)

H3 = Gate(
    name="H3",
    params=((0, 1 / sqrt(2), 1 / sqrt(2)), pi, pi / 2),
    matrix=1 / sqrt(2) * Matrix([
        [1, -1j],
        [1j, -1]]
    )
)

H4 = Gate(
    name="H4",
    params=((-1 / sqrt(2), 1 / sqrt(2), 0), pi, pi / 2),
    matrix=1 / sqrt(2) * Matrix([
        [0, -1 - 1j],
        [-1 + 1j, 0]]
    )
)

H5 = Gate(
    name="H5",
    params=((1 / sqrt(2), 0, -1 / sqrt(2)), pi, pi / 2),
    matrix=1 / sqrt(2) * Matrix([
        [-1, 1],
        [1, 1]]
    )
)

H6 = Gate(
    name="H6",
    params=((0, -1 / sqrt(2), 1 / sqrt(2)), pi, pi / 2),
    matrix=1 / sqrt(2) * Matrix([
        [1, 1j],
        [-1j, -1]]
    )
)

# Cycling gates: A third turns around triple axes

C1 = Gate(
    name="C1",
    params=((1 / sqrt(3), 1 / sqrt(3), 1 / sqrt(3)), 2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 - 1j, -1 - 1j],
        [1 - 1j, 1 + 1j]]
    )
)

C2 = Gate(
    name="C2",
    params=((1 / sqrt(3), 1 / sqrt(3), 1 / sqrt(3)), -2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 + 1j, 1 + 1j],
        [-1 + 1j, 1 - 1j]]
    )
)

C3 = Gate(
    name="C3",
    params=((-1 / sqrt(3), 1 / sqrt(3), 1 / sqrt(3)), 2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 - 1j, -1 + 1j],
        [1 + 1j, 1 + 1j]]
    )
)

C4 = Gate(
    name="C4",
    params=((-1 / sqrt(3), 1 / sqrt(3), 1 / sqrt(3)), -2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 + 1j, 1 - 1j],
        [-1 - 1j, 1 - 1j]]
    )
)

C5 = Gate(
    name="C5",
    params=((1 / sqrt(3), -1 / sqrt(3), 1 / sqrt(3)), 2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 - 1j, 1 - 1j],
        [-1 - 1j, 1 + 1j]]
    )
)

C6 = Gate(
    name="C6",
    params=((1 / sqrt(3), -1 / sqrt(3), 1 / sqrt(3)), -2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 + 1j, -1 + 1j],
        [1 + 1j, 1 - 1j]]
    )
)

C7 = Gate(
    name="C7",
    params=((1 / sqrt(3), 1 / sqrt(3), -1 / sqrt(3)), 2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 + 1j, -1 - 1j],
        [1 - 1j, 1 - 1j]]
    )
)

C8 = Gate(
    name="C8",
    params=((1 / sqrt(3), 1 / sqrt(3), -1 / sqrt(3)), -2 * pi / 3, 0),
    matrix=1 / 2 * Matrix([
        [1 - 1j, 1 + 1j],
        [-1 + 1j, 1 + 1j]]
    )
)

gates = [I, X, Y, Z, X90, mX90, mY90, Y90, Z90, mZ90, T, Tdag, H1, H2, H3, H4, H5, H6, C1, C2, C3, C4, C5, C6, C7, C8]
