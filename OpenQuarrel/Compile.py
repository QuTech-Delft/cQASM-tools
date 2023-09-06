from GeneratedParsingCode import CQasm3Parser
from GeneratedParsingCode import CQasm3Lexer
from TypeChecker import TypeChecker
from Decomposer import Decomposer
from antlr4.error.ErrorListener import ErrorListener
import antlr4

### Stuff to report syntax/parsing errors.
class ErrorHandler(ErrorListener) :
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        stack = recognizer.getRuleInvocationStack()
        stack.reverse()
        print("rule stack: ", str(stack))
        print("line", line, ":", column, "at", offendingSymbol, ":", msg)



def compile(input: str) -> str:
    """Entrypoint.

input: a cQasm 3.0 string, as parsed by CQasm3.g4
output: a cQasm 3.0 string, corresponding to the compiled circuit
         * comments are removed
         * type-checking is performed, eliminating qubit indices errors and incoherences
         * checks that used gates are supported and mentioned in Common.py
         * does not support map or variables
         * all one-qubit gates are merged together, without attempting to commute any gate
         * two-or-more-qubit gates are left as-is
         * merged one-qubit gates are decomposed according to Kay decomposition, that is:
                   gate   ---->    Rz.Rx(pi/2).Rz.Rx(pi/2).Rz
         * _global phase is deemed irrelevant_, therefore a simulator backend might produce different output
            for the input and output circuit - those outputs should be equivalent modulo global phase.
"""
    input_stream = antlr4.InputStream(input)
    lexer = CQasm3Lexer.CQasm3Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = CQasm3Parser.CQasm3Parser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(ErrorHandler())
    tree = parser.prog()

    typeChecker = TypeChecker()
    typeChecker.visit(tree)

    decomposer = Decomposer()
    decomposed = decomposer.visit(tree)

    return decomposed