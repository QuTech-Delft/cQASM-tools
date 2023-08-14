# KAK decomposition with cirq

import cirq
import numpy as np
import math, cmath
from fractions import Fraction

atol = 0.00000000001

X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])

def Can1(angle, axis):
    nx = axis[0]
    ny = axis[1]
    nz = axis[2]

    norm = math.sqrt(nx**2 + ny**2 + nz**2)

    nx /= norm
    ny /= norm
    nz /= norm

    return math.cos(angle / 2) * np.identity(2) - 1j * math.sin(angle / 2) * (nx * X + ny * Y + nz * Z)

def Can2(tx, ty, tz):
    ax = 1j * math.pi * tx / 2
    result = cmath.cosh(ax) * np.identity(4) - cmath.sinh(ax) * np.kron(X, X)
    ay = 1j * math.pi * ty / 2
    result = result @ (cmath.cosh(ay) * np.identity(4) - cmath.sinh(ay) * np.kron(Y, Y))
    az = 1j * math.pi * tz / 2
    result = result @ (cmath.cosh(az) * np.identity(4) - cmath.sinh(az) * np.kron(Z, Z))

    return result


def cartesianToSphericalCoordinates(axis: (float, float, float)):
    assert(abs(axis[0]**2 + axis[1]**2 + axis[2]**2 - 1) < atol)

    theta = math.acos(axis[2])

    phi = math.atan2(axis[1], axis[0])

    thetaFraction = Fraction(theta / math.pi).limit_denominator()
    phiFraction = Fraction(phi / math.pi).limit_denominator()

    return {"theta / π": thetaFraction, "phi / π": phiFraction}


def getNiceRotation(matrix: np.ndarray):
    axisAngle = cirq.axis_angle(matrix).canonicalize()
    axis, angle = axisAngle.axis, axisAngle.angle

    sph = cartesianToSphericalCoordinates(axis)

    return {"theta / π": sph["theta / π"], "phi / π": sph["phi / π"], "rotationAngle / π": Fraction(angle / math.pi).limit_denominator()}


def niceKAK(gate: np.ndarray):
    assert(gate.shape == (4, 4))

    cirqDec = cirq.kak_decomposition(gate)
    
    globalPhase = Fraction(cmath.phase(cirqDec.global_phase) / math.pi).limit_denominator()

    niceCoeffs = map(lambda x: Fraction(x / math.pi * 2).limit_denominator(), cirqDec.interaction_coefficients)

    print(f"""
Global phase: {globalPhase} * π
Before: {getNiceRotation(cirqDec.single_qubit_operations_before[0])} ⊗ {getNiceRotation(cirqDec.single_qubit_operations_before[1])}
Can2({', '.join(map(str, niceCoeffs))})
After: {getNiceRotation(cirqDec.single_qubit_operations_after[0])} ⊗ {getNiceRotation(cirqDec.single_qubit_operations_after[1])}
    """)



cnot = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1],
                 [0, 0, 1, 0]])

swap = np.array([[1, 0, 0, 0],
                 [0, 0, 1, 0],
                 [0, 1, 0, 0],
                 [0, 0, 0, 1]])

sqrtswap = np.array([[1, 0, 0, 0],
                     [0, (1 - 1j) / 2, (1 + 1j) / 2, 0],
                     [0, (1 + 1j) / 2, (1 - 1j) / 2, 0],
                     [0, 0, 0, 1]])

niceKAK(swap)


# tr = result.global_phase * np.kron(Can1(b0.angle, b0.axis), Can1(b1.angle, b1.axis))
# tr = Can2(-1/2, 0, 0) @ tr
# tr = np.kron(Can1(a0.angle, a0.axis), Can1(a1.angle, a1.axis)) @ tr


# np.set_printoptions(precision=2)

# tr[np.abs(tr) < 0.0000001] = 0

# print(tr)