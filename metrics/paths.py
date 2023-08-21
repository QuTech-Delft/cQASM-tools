import typing
from parsing import CQASMParser
import networkx
import statistics
import numpy as np
import math
from timeit import default_timer as timer

def buildDDG(c: list[CQASMParser.Instruction]):
    start = timer()
    graph = networkx.DiGraph()
    graph.add_node("SOURCE")

    qubitsToNode = {}

    i = 0
    for instruction in c:
        if not isinstance(instruction, CQASMParser.Gate):
            raise Exception("Not a gate")
        
        node = (i, instruction)
        graph.add_node(node)

        for q in instruction.operands:
            if not isinstance(q, CQASMParser.Qubit):
                continue
            
            if q.index in qubitsToNode:
                graph.add_edge(qubitsToNode[q.index], node)
            
            qubitsToNode[q.index] = node
        
        try:
            next(graph.predecessors(node))
        except StopIteration:
            graph.add_edge("SOURCE", node)

        i += 1
    
    graph.add_node("SINK")

    for n in networkx.nodes(graph):
        try:
            next(graph.successors(n))
        except StopIteration:
            if n != "SINK":
                graph.add_edge(n, "SINK")

    assert(networkx.number_of_nodes(graph) == len(c) + 2)
    assert(networkx.is_directed_acyclic_graph(graph))

    return graph

def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values - average)**2, weights=weights)
    return (average, math.sqrt(variance))

def getPathStats(c: list[CQASMParser.Instruction]):
    graph = buildDDG(c)

    allSimplePaths = lambda: networkx.all_simple_paths(graph, "SOURCE", "SINK")

    distro = {}
    n = 0
    for p in allSimplePaths():
        n += 1
        if n % 1000 == 0:
            print(f"Processed {n} paths")
        l = len(p) - 2
        if l in distro:
            distro[l] += 1
        else:
            distro[l] = 1
    
    criticalPathLengthInGates = networkx.dag_longest_path_length(graph) - 1 # This is in number of gates. dag_longest_path_length returns number of edges.

    criticalPaths = lambda: filter(lambda path: len(path) - 2 == criticalPathLengthInGates, allSimplePaths())

    def numberOfTwoQubitsGates(path):
        result = 0
        for node in path:
            if isinstance(node, str):
                continue
            gate = node[1]
            assert(isinstance(gate, CQASMParser.Gate))
            if len(list(filter(lambda op: isinstance(op, CQASMParser.Qubit), gate.operands))) == 2:
                result += 1
        return result

    maxNumberOfTwoQubitGatesInCriticalPaths = max(numberOfTwoQubitsGates(path) for path in criticalPaths())
    numberOfCriticalPaths = sum(1 for _ in criticalPaths())
    numberOfCriticalPathsWithMaxTwoQubitsGates = sum(1 for _ in filter(lambda path: numberOfTwoQubitsGates(path) == maxNumberOfTwoQubitGatesInCriticalPaths, criticalPaths()))

    mean, std = weighted_avg_and_std(list(distro.keys()), list(distro.values()))

    return {
        "NumberOfGatesInCriticalPath": criticalPathLengthInGates, # This removes SOURCE and SINK
        "MaxNumberOfTwoQubitGatesInCriticalPath": maxNumberOfTwoQubitGatesInCriticalPaths,
        "NumberOfCriticalPaths": numberOfCriticalPaths,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": numberOfCriticalPathsWithMaxTwoQubitsGates,
        "PathLengthMean": mean,
        "PathLengthStandardDeviation": std,
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
        "PathLengthStandardDeviation": 0.5,
    }
    print(output)
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
        "PathLengthStandardDeviation": 0.5,
    }

    checkSame(output, expected)


def test4(): # This illustrates that computing the path statistics is difficult this way: this relatively small circuit already has 53000+ paths from source to sink.
    cq = """ 
    version 1.0

qubits 3

.testCircuit
  h q[1]
  t q[3]
  t q[4]
  t q[1]
  cnot q[4], q[3]
  cnot q[1], q[4]
  cnot q[3], q[1]
  tdag q[4]
  cnot q[3], q[4]
  tdag q[3]
  tdag q[4]
  t q[1]
  cnot q[1], q[4]
  cnot q[3], q[1]
  cnot q[4], q[3]
  h q[1]
  h q[4]
  t q[0]
  t q[2]
  t q[4]
  cnot q[2], q[0]
  cnot q[4], q[2]
  cnot q[0], q[4]
  tdag q[2]
  cnot q[0], q[2]
  tdag q[0]
  tdag q[2]
  t q[4]
  cnot q[4], q[2]
  cnot q[0], q[4]
  cnot q[2], q[0]
  h q[4]
  h q[1]
  t q[3]
  t q[4]
  t q[1]
  cnot q[4], q[3]
  cnot q[1], q[4]
  cnot q[3], q[1]
  tdag q[4]
  cnot q[3], q[4]
  tdag q[3]
  tdag q[4]
  t q[1]
  cnot q[1], q[4]
  cnot q[3], q[1]
  cnot q[4], q[3]
  h q[1]
  h q[4]
  t q[0]
  t q[2]
  t q[4]
  cnot q[2], q[0]
  cnot q[4], q[2]
  cnot q[0], q[4]
  tdag q[2]
  cnot q[0], q[2]
  tdag q[0]
  tdag q[2]
  t q[4]
  cnot q[4], q[2]
  cnot q[0], q[4]
  cnot q[2], q[0]
  h q[4]
  cnot q[2], q[0]
"""

    print(getPathStats(CQASMParser.parseCQASMString(cq).subcircuits[0].instructions))


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
