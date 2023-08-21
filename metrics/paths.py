import typing
from parsing import CQASMParser
import rustworkx
import statistics

def buildDDG(c: list[CQASMParser.Instruction]):
    graph = rustworkx.PyDAG(check_cycle=True, multigraph=False)
    source = graph.add_node("SOURCE")

    qubitsToNode = {}

    i = 0
    for instruction in c:
        if not isinstance(instruction, CQASMParser.Gate):
            raise Exception("Not a gate")
        
        node = graph.add_node((i, instruction))

        for q in instruction.operands:
            if not isinstance(q, CQASMParser.Qubit):
                continue
            
            if q.index in qubitsToNode:
                graph.add_edge(qubitsToNode[q.index], node, (graph[qubitsToNode[q.index]][0], graph[node][0]))
            
            qubitsToNode[q.index] = node

        if (graph.predecessors(node) == []):
            graph.add_edge(source, node, (graph[source], graph[node][0]))

        i += 1
    
    sink = graph.add_node("SINK")

    for n in graph.node_indices():
        if (graph.successors(n) == [] and graph[n] != "SINK"):
            graph.add_edge(n, sink, (graph[n][0], graph[sink]))

    assert(graph.num_nodes() == len(c) + 2)
    assert(rustworkx.is_directed_acyclic_graph(graph))

    return (source, sink, graph)


def getPathStats(c: list[CQASMParser.Instruction]):
    source, sink, graph = buildDDG(c)

    allSimplePaths = rustworkx.all_simple_paths(graph, source, sink)
    simplePathsLengthsInGates = list(map(lambda x: len(x) - 2, allSimplePaths)) # This removes SOURCE and SINK

    criticalPathLengthInGates = rustworkx.dag_longest_path_length(graph) - 1 # This is in number of gates. dag_longest_path_length returns number of edges.

    criticalPaths = lambda: filter(lambda path: len(path) - 2 == criticalPathLengthInGates, allSimplePaths)

    def numberOfTwoQubitsGates(path):
        result = 0
        for nodeIndex in path:
            gate = graph[nodeIndex][1]
            if isinstance(gate, str):
                continue
            
            assert(isinstance(gate, CQASMParser.Gate))
            if len(list(filter(lambda op: isinstance(op, CQASMParser.Qubit), gate.operands))) == 2:
                result += 1
        return result

    maxNumberOfTwoQubitGatesInCriticalPaths = max(numberOfTwoQubitsGates(path) for path in criticalPaths())
    numberOfCriticalPaths = sum(1 for _ in criticalPaths())
    numberOfCriticalPathsWithMaxTwoQubitsGates = sum(1 for _ in filter(lambda path: numberOfTwoQubitsGates(path) == maxNumberOfTwoQubitGatesInCriticalPaths, criticalPaths()))

    return {
        "NumberOfGatesInCriticalPath": criticalPathLengthInGates, # This removes SOURCE and SINK
        "MaxNumberOfTwoQubitGatesInCriticalPath": maxNumberOfTwoQubitGatesInCriticalPaths,
        "NumberOfCriticalPaths": numberOfCriticalPaths,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": numberOfCriticalPathsWithMaxTwoQubitsGates,
        "PathLengthMean": statistics.mean(simplePathsLengthsInGates),
        "PathLengthStandardDeviation": statistics.stdev(simplePathsLengthsInGates) if len(simplePathsLengthsInGates) >= 2 else 0.,
    }


def checkSame(a, b):
    floatKeys = {"PathLengthMean", "PathLengthStandardDeviation"}
    for k in floatKeys:
        assert(abs(a[k] - b[k]) < 0.00000001)

    assert(list(v for k, v in a.items() if k not in floatKeys) == list(v for k, v in b.items() if k not in floatKeys)) 

def test1():
    cq = """
    version 1.0

qubits 3

.testCircuit
  x q[2]
  cnot q[0], q[2]
  cnot q[2], q[1]
  h q[0]
  t q[1]
"""

    output = getPathStats(CQASMParser.parseCQASMString(cq).subcircuits[0].instructions)

    expected = {
        "NumberOfGatesInCriticalPath": 4,
        "MaxNumberOfTwoQubitGatesInCriticalPath": 2,
        "NumberOfCriticalPaths": 1,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": 1,
        "PathLengthMean": 3.5,
        "PathLengthStandardDeviation": 0.7071067811865476,
    }

    checkSame(output, expected)

def test2():
    cq = """
    version 1.0

qubits 4

.testCircuit
  cnot q[0], q[2]
  cnot q[0], q[1]
  cnot q[1], q[3]
"""

    output = getPathStats(CQASMParser.parseCQASMString(cq).subcircuits[0].instructions)

    expected = {
        "NumberOfGatesInCriticalPath": 3,
        "MaxNumberOfTwoQubitGatesInCriticalPath": 3,
        "NumberOfCriticalPaths": 1,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": 1,
        "PathLengthMean": 3,
        "PathLengthStandardDeviation": 0,
    }

    checkSame(output, expected)

def test3():
    cq = """
    version 1.0

qubits 4

.testCircuit
  h q[0]
  h q[0]
  h q[1]
"""

    output = getPathStats(CQASMParser.parseCQASMString(cq).subcircuits[0].instructions)

    expected = {
        "NumberOfGatesInCriticalPath": 2,
        "MaxNumberOfTwoQubitGatesInCriticalPath": 0,
        "NumberOfCriticalPaths": 1,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": 1, # There are no paths with 2q gates.
        "PathLengthMean": 1.5,
        "PathLengthStandardDeviation": 0.7071067811865476,
    }

    checkSame(output, expected)

if __name__ == "__main__":
    test1()
    test2()
    test3()
