from math import acos, cos, sin, atan2, pi, sqrt
from GeneratedParsingCode import CQasm3Visitor
from Common import GATES, ExprType, ArgType, Parameter
import numpy as np

ATOL = 0.000001

def normalizeAngle(x):
      t = x - 2 * pi * (x // (2 * pi) + 1)
      if t < -pi + ATOL:
        t += 2 * pi
      elif t > pi:
        t -= 2 * pi
      return t

def normalize(axis):
  norm = np.linalg.norm(axis)
  axis /= norm

class Decomposer(CQasm3Visitor.CQasm3Visitor):
  def __init__(self):
    self.oneQubitGates = {}
    self.output = ""

  def decomposeAndAdd(self, qubit, angle, axis):
    if abs(angle) < ATOL:
      return
    
    # McKay decomposition

    zaMod = sqrt(cos(angle / 2) ** 2 + (axis[2] * sin(angle / 2)) ** 2)
    zbMod = abs(sin(angle / 2)) * sqrt(axis[0] ** 2 + axis[1] ** 2)

    theta = pi - 2 * atan2(zbMod, zaMod)

    alpha = atan2(- sin(angle / 2) * axis[2], cos(angle / 2))
    beta = atan2(- sin(angle / 2) * axis[0], - sin(angle / 2) * axis[1])

    lam = beta - alpha
    phi = -beta - alpha - pi

    lam = normalizeAngle(lam)
    phi = normalizeAngle(phi)
    theta = normalizeAngle(theta)

    if abs(lam) > ATOL:
      self.output += f'''rz q[{qubit}], {lam}\n'''

    self.output += f'''x90 q[{qubit}]\n'''
    
    if abs(theta) > ATOL:
      self.output += f'''rz q[{qubit}], {theta}\n'''
    
    self.output += f'''x90 q[{qubit}]\n'''

    if abs(phi) > ATOL:
      self.output += f'''rz q[{qubit}], {phi}\n'''


  def flush(self, q):
    if q not in self.oneQubitGates:
      return
    p = self.oneQubitGates.pop(q)
    self.decomposeAndAdd(q, p['angle'], p['axis'])

  def flushAll(self):
    for q, p in self.oneQubitGates.items():
      self.decomposeAndAdd(q, p['angle'], p['axis'])

    self.oneQubitGates = {}

  def acc(self, qubit, angle, axis, phase):
    axis = np.array(axis).astype(np.float64)
    normalize(axis)

    if qubit not in self.oneQubitGates:
      self.oneQubitGates[qubit] = {"angle": angle, "axis": axis, "phase": phase}
      return

    existing = self.oneQubitGates[qubit]
    combinedPhase = phase + existing["phase"]

    a = angle
    l = axis
    b = existing["angle"]
    m = existing["axis"]

    combinedAngle = 2 * acos(cos(a / 2) * cos(b / 2) - sin(a / 2) * sin(b / 2) * np.dot(l, m))

    if abs(sin(combinedAngle / 2)) < ATOL:
      self.oneQubitGates.pop(qubit)
      return

    combinedAxis = 1 / sin(combinedAngle / 2) * (sin(a / 2) * cos(b / 2) * l + cos(a / 2) * sin(b / 2) * m
                                                        + sin(a / 2) * sin(b / 2) * np.cross(l, m))

    self.oneQubitGates[qubit] = {"angle": combinedAngle, "axis": combinedAxis, "phase": combinedPhase}

  def visitProg(self, ctx):
      qubitRegisterName, nQubits = self.visit(ctx.qubitRegisterDeclaration())
      self.output += f'''version 3.0\n\nqubit[{nQubits}] {qubitRegisterName}\n\n'''

      for gApp in ctx.gateApplication():
        self.visit(gApp)

      self.flushAll()

      return self.output
  
  def visitQubitRegisterDeclaration(self, ctx):
    return (str(ctx.ID()), int(str(ctx.INT())))

  def extract_original_text(self, ctx):
      token_source = ctx.start.getTokenSource()
      input_stream = token_source.inputStream
      start, stop  = ctx.start.start, ctx.stop.stop
      return input_stream.getText(start, stop)

  def visitGateApplication(self, ctx):
      gateName = str(ctx.ID())
      signatureQubitIndices = [i for i in range(len(GATES[gateName]["signature"])) if GATES[gateName]["signature"][i] == ArgType.QUBIT]
      gateQubits = [self.visit(ctx.expr(i)) for i in signatureQubitIndices]

      assert(all(len(l) == len(gateQubits[0]) for l in gateQubits))

      if len(gateQubits) >= 2:
        s = set([q for l in gateQubits for q in l])
        [self.flush(q) for q in s]
        self.output += f"{self.extract_original_text(ctx)}\n"
        return

      if len(gateQubits) == 0:
        self.output += f"{self.extract_original_text(ctx)}\n"
        return
        
      if isinstance(GATES[gateName]["angle"], Parameter):
        angle = self.visit(ctx.expr(GATES[gateName]["angle"].value))
      else:
        angle = GATES[gateName]["angle"]

      qubitArguments = zip(*gateQubits)
      for qubitArgument in qubitArguments:
        assert(len(qubitArgument) == 1)
        self.acc(qubitArgument[0], angle, GATES[gateName]["axis"], GATES[gateName]["phase"])

  def visitQubit(self, ctx):
      return [int(str(ctx.INT()))]

  def visitQubits(self, ctx):
      return list(map(int, map(str, ctx.INT())))

  def visitQubitRange(self, ctx):
      qubitIndex1 = int(str(ctx.INT(0)))
      qubitIndex2 = int(str(ctx.INT(1)))
      return list(range(qubitIndex1, qubitIndex2 + 1))

  def visitFloatLiteral(self, ctx):
    return float(str(ctx.FLOAT()))

  def visitNegatedFloatLiteral(self, ctx):
    return - float(str(ctx.FLOAT()))

  def visitIntLiteral(self, ctx):
    return int(str(ctx.INT()))

  def visitNegatedIntLiteral(self, ctx):
    return - int(str(ctx.INT()))