import math
from enum import Enum

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
    },
    "CNOT": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT),
    },
    "cr": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT, ArgType.FLOAT),
    },
    "CR": {
        "signature": (ArgType.QUBIT, ArgType.QUBIT, ArgType.FLOAT),
    },
}