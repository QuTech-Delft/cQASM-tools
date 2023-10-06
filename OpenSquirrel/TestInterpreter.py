from GeneratedParsingCode import CQasm3Visitor
from Common import GATES, ExprType, ArgType, Parameter, getBigMatrix
import antlr4
from GeneratedParsingCode import CQasm3Parser
from GeneratedParsingCode import CQasm3Lexer
import numpy as np

class TestInterpreter(CQasm3Visitor.CQasm3Visitor):
  def __init__(self):
    self.qubitRegisterName = None
    self.nQubits = 0
    self.totalUnitary = None

  def visitProg(self, ctx):
      self.qubitRegisterName, self.nQubits = self.visit(ctx.qubitRegisterDeclaration())

      self.totalUnitary = np.eye(1 << self.nQubits, dtype=np.complex128)

      for gApp in ctx.gateApplication():
        self.visit(gApp)

      return self.totalUnitary
  
  def visitQubitRegisterDeclaration(self, ctx):
    return (str(ctx.ID()), int(str(ctx.INT())))

  def visitGateApplication(self, ctx):
      gateName = str(ctx.ID())
      signatureQubitIndices = [i for i in range(len(GATES[gateName]["signature"])) if GATES[gateName]["signature"][i] == ArgType.QUBIT]
      numberOfGateApplications = len(next(self.visit(ctx.expr(i)) for i in signatureQubitIndices))

      args = list(map(self.visit, ctx.expr()))

      for i in range(numberOfGateApplications):
        thoseArgs = [x[i] if isinstance(x, list) else x for x in args]
      
        bigMatrix = getBigMatrix(gateName = gateName, *thoseArgs, nQubits = self.nQubits)
        self.totalUnitary = bigMatrix @ self.totalUnitary

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

def getCircuitMatrix(cqasm3_string):
  input_stream = antlr4.InputStream(cqasm3_string)
  lexer = CQasm3Lexer.CQasm3Lexer(input_stream)
  stream = antlr4.CommonTokenStream(lexer)
  parser = CQasm3Parser.CQasm3Parser(stream)
  tree = parser.prog()

  testInterpreter = TestInterpreter()
  circuitMatrix = testInterpreter.visit(tree)

  return circuitMatrix