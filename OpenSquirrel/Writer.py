from Common import ArgType
from Gates import querySignature

class Writer:
    def __init__(self, gates):
        self.gates = gates

    def _formatArg(self, x):
        arg, argType = x
        if argType == ArgType.QUBIT:
            return f"q[{arg}]"
        
        return f"{arg}"

    def process(self, squirrelAST):
        output = ""
        output += f'''version 3.0\n\nqubit[{squirrelAST.nQubits}] {squirrelAST.qubitRegisterName}\n\n'''

        for gateName, gateArgs in squirrelAST.operations:
            signature = querySignature(self.gates, gateName)

            output += f"{gateName} {', '.join(map(self._formatArg, zip(gateArgs, signature)))}\n" # FIXME: q[]
        
        return output
