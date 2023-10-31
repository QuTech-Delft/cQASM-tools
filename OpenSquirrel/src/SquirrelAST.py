
class SquirrelAST:
    # This is just a list of gates (for now?)
    def __init__(self, gates, nQubits, qubitRegisterName):
        self.gates = gates
        self.nQubits = nQubits
        self.operations = []
        self.qubitRegisterName = qubitRegisterName
    
    def addGate(self, gateName, *interpretedArgs):
        assert gateName in self.gates, f"Unknown gate: {gateName}"
        self.operations.append((gateName, interpretedArgs))
    