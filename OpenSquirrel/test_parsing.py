import unittest
from TestGates import TEST_GATES
from SquirrelASTCreator import SquirrelASTCreator
from GeneratedParsingCode import CQasm3Parser
from GeneratedParsingCode import CQasm3Lexer
from GeneratedParsingCode import CQasm3Visitor
from TypeChecker import TypeChecker
from SquirrelErrorHandler import SquirrelErrorHandler, SquirrelParseException
import antlr4

class ParsingTest(unittest.TestCase):
    def setUp(self):
        self.gates = TEST_GATES
        self.astCreator = SquirrelASTCreator(TEST_GATES)
    
    def typeCheck(self, cQasm3String):
        input_stream = antlr4.InputStream(cQasm3String)

        lexer = CQasm3Lexer.CQasm3Lexer(input_stream)

        stream = antlr4.CommonTokenStream(lexer)

        parser = CQasm3Parser.CQasm3Parser(stream)

        parser.removeErrorListeners()
        parser.addErrorListener(SquirrelErrorHandler())

        tree = parser.prog()

        typeChecker = TypeChecker(self.gates)
        typeChecker.visit(tree)

        return tree

    def getAST(self, cQasm3String):
        tree = self.typeCheck(cQasm3String)
        return self.astCreator.visit(tree)

    def test_empty(self):
        with self.assertRaisesRegex(SquirrelParseException, "Parsing error at 1:0: mismatched input '<EOF>' expecting"):
            self.typeCheck("")
    
    def test_illegal(self):
        with self.assertRaisesRegex(SquirrelParseException, "Parsing error at 1:0: mismatched input 'illegal' expecting"):
            self.typeCheck("illegal")
        
    def test_noqubits(self):
        with self.assertRaisesRegex(SquirrelParseException, "Parsing error at 1:14: mismatched input 'h' expecting 'qubit"):
            self.typeCheck("version 3.0;  h q[0]")
    
    def test_wrongversion(self):
        with self.assertRaisesRegex(SquirrelParseException, "Parsing error at 1:8: mismatched input '3.1' expecting '3.0'"):
            self.typeCheck("version 3.1; qubit[1] q; h q[0]")

    def test_unknowngate(self):
        with self.assertRaisesRegex(Exception, "Unknown gate unknowngate"):
            self.typeCheck("version 3.0; qubit[1] q; unknowngate q[0]")

    def test_wrongargumenttype(self):
        with self.assertRaisesRegex(Exception, "Argument #1 passed to gate rx is of type ArgType.INT but should be ArgType.FLOAT"):
            self.typeCheck("version 3.0; qubit[1] q; rx q[0], 42")
    
    def test_wrongargumenttype2(self):
        with self.assertRaisesRegex(Exception, "Argument #0 passed to gate rx is of type ArgType.FLOAT but should be ArgType.QUBIT"):
            self.typeCheck("version 3.0; qubit[1] q; rx 42., q[0]")

    def test_simple(self):
        ast = self.getAST("""
version 3.0
  qubit[1] qu
  
  h qu[0]
        """)

        assert ast.nQubits == 1
        assert ast.qubitRegisterName == "qu"
        assert len(ast.operations) == 1
        assert ast.operations[0] == ("h", (0,))

    def test_rxyz(self):
        ast = self.getAST("""
version 3.0
  qubit[2] squirrel
  
  h squirrel[0];
  rx squirrel[1], 1.23;;;;;
  ry squirrel[0], -42.;;;;;
        """)

        assert ast.nQubits == 2
        assert ast.qubitRegisterName == "squirrel"
        assert len(ast.operations) == 3
        assert ast.operations[0] == ("h", (0,))
        assert ast.operations[1] == ("rx", (1, 1.23))
        assert ast.operations[2] == ("ry", (0, -42))

    def test_multiplequbits(self):
        ast = self.getAST("""
version 3.0
  qubit[10] large
  
  h large[0,3,6];
  x90 large[4:5];
        """)

        assert ast.nQubits == 10
        assert ast.qubitRegisterName == "large"
        assert len(ast.operations) == 5
        assert ast.operations[0] == ("h", (0,))
        assert ast.operations[1] == ("h", (3,))
        assert ast.operations[2] == ("h", (6,))
        assert ast.operations[3] == ("x90", (4,))
        assert ast.operations[4] == ("x90", (5,))

    def test_aliases(self):
        ast = self.getAST("""
version 3.0
  qubit[2] q;
  
  H q[1]
        """)

        assert ast.operations[0] == ("H", (1,))

if __name__ == '__main__':
    unittest.main()