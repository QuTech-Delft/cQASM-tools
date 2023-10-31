from antlr4.error.ErrorListener import ErrorListener as Antlr4ErrorListener

class SquirrelErrorHandler(Antlr4ErrorListener) :
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        stack = recognizer.getRuleInvocationStack()
        stack.reverse()
        print("rule stack: ", str(stack))
        print("line", line, ":", column, "at", offendingSymbol, ":", msg)