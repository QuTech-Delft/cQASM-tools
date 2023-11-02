from src.Common import ArgType
from src.Gates import querySignature
from src.SquirrelAST import SquirrelAST

class Replacer:
    def __init__(self, gates):
        self.gates = gates
    
    def process(self, squirrelAST: SquirrelAST, gateName: str, f):
        result = SquirrelAST(self.gates, squirrelAST.nQubits, squirrelAST.qubitRegisterName)

        signature = querySignature(self.gates, gateName)

        for otherGateName, otherArgs in squirrelAST.operations:
            if otherGateName != gateName:
                result.addGate(otherGateName, otherArgs)
            
            # FIXME: handle case where if f is not a function but directly a list.

            replacement = f(*otherArgs)

            # TODO: Here, check that the semantic of the replacement is the same!
            # For this, need to update the simulation capabilities.

            # TODO: Do we allow skipping the replacement, based on arguments?

            assert isinstance(replacement, list), "Substitution needs to be a list"

            for replacementGate in replacement:
                replacementGateName, replacementGateArgs = replacementGate

                result.addGate(replacementGateName, replacementGateArgs)
        
        return result
