import math
from enum import Enum
import numpy as np

ATOL = 0.0000001

class ExprType(Enum):
    QUBITREFS = 1
    FLOAT = 2
    INT = 3

class ArgType(Enum):
    QUBIT = 0
    FLOAT = 1
    INT = 2

def exprTypeToArgType(t):
  if t == ExprType.QUBITREFS:
    return ArgType.QUBIT
  if t == ExprType.FLOAT:
    return ArgType.FLOAT
  if t == ExprType.INT:
    return ArgType.INT

class Parameter:
  def __init__(self, n):
    self.value = n

GATES = {
    "h": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 1),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "H": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 1),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "x": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "X": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "y": {
        "signature": (ArgType.QUBIT,),
        "axis": (0, 1, 0),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "Y": {
        "signature": (ArgType.QUBIT,),
        "axis": (0, 1, 0),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "z": {
        "signature": (ArgType.QUBIT,),
        "axis": (0, 0, 1),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "Z": {
        "signature": (ArgType.QUBIT,),
        "axis": (0, 0, 1),
        "angle": math.pi,
        "phase": math.pi / 2,
    },
    "rx": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (1, 0, 0),
        "angle": Parameter(1),
        "phase": 0.
    },
    "RX": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (1, 0, 0),
        "angle": Parameter(1),
        "phase": 0.
    },
    "x90": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": math.pi / 2,
        "phase": 0.
    },
    "X90": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": math.pi / 2,
        "phase": 0.
    },
    "mx90": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": - math.pi / 2,
        "phase": 0.
    },
    "MX90": {
        "signature": (ArgType.QUBIT,),
        "axis": (1, 0, 0),
        "angle": - math.pi / 2,
        "phase": 0.
    },
    "ry": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (0, 1, 0),
        "angle": Parameter(1),
        "phase": 0.
    },
    "RY": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (0, 1, 0),
        "angle": Parameter(1),
        "phase": 0.
    },
    "rz": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (0, 0, 1),
        "angle": Parameter(1),
        "phase": 0.
    },
    "RZ": {
        "signature": (ArgType.QUBIT, ArgType.FLOAT),
        "axis": (0, 0, 1),
        "angle": Parameter(1),
        "phase": 0.
    },
    "cnot": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT),
        "matrix": lambda: np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ])
    },
    "CNOT": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT),
        "matrix": lambda: np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ])
    },
    "cr": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT, ArgType.FLOAT),
    },
    "CR": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT, ArgType.FLOAT),
    },
}

import numpy as np
import unittest
import math, cmath, scipy

X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])

def Can1(axis, angle, phase = 0):
    nx, ny, nz = axis
    norm = math.sqrt(nx**2 + ny**2 + nz**2)
    assert(norm > 0.00000001)

    nx /= norm
    ny /= norm
    nz /= norm

    result = cmath.rect(1, phase) * (math.cos(angle / 2) * np.identity(2) - 1j * math.sin(angle / 2) * (nx * X + ny * Y + nz * Z))

    return result

# This should only be used for testing and on circuits with low number of qubits.
def getBigMatrix(*args, gateName, nQubits):
    # Assumes signature matches arg list
    entry = GATES[gateName]
    qubitArgs = [args[i] for i in range(len(entry["signature"])) if entry["signature"][i] == ArgType.QUBIT]

    if len(qubitArgs) == 1:
        whichQubit = qubitArgs[0]
        angle = entry["angle"] if not isinstance(entry["angle"], Parameter) else args[entry["angle"].value]
        result = np.kron(np.kron(np.eye(1 << (nQubits - whichQubit - 1)), Can1(entry["axis"], angle, entry["phase"])), np.eye(1 << whichQubit))
        assert(result.shape == (1 << nQubits, 1 << nQubits))
        return result

    m = GATES[gateName]["matrix"](*[args[i] for i in range(len(entry["signature"])) if entry["signature"][i] != ArgType.QUBIT])

    assert(m.shape[0] == 1 << len(qubitArgs))

    result = np.zeros((1 << nQubits, 1 << nQubits), dtype=np.complex128)

    for input in range(1 << nQubits):
        smallMatrixCol = 0
        for i in range(len(qubitArgs)):
            smallMatrixCol |= ((input & (1 << qubitArgs[i])) >> qubitArgs[i]) << (len(qubitArgs) - 1 - i)
        
        col = m[:, smallMatrixCol]
        
        for output in range(len(col)):
            coeff = col[output]

            largeOutput = 0
            for i in range(len(qubitArgs)):
                index = len(qubitArgs) - i - 1
                largeOutput |= ((output & (1 << index)) >> index) << qubitArgs[i]
            
            result[largeOutput][input] = coeff
    
    return result

