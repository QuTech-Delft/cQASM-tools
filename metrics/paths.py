import typing
from parsing import CQASMParser
import networkx
import statistics
import numpy as np
import math
from timeit import default_timer as timer
from dataclasses import dataclass
from decimal import Decimal

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

@dataclass
class PropagatedData:
    numberOfPaths: int
    meanLengthOfPath: Decimal
    varianceLengthOfPath: Decimal
    maxLengthOfPath: int
    numberOfPathsWithMaxLength: int
    maxNumberOfTwoQubitGatesInPathsWithMaxLength: int
    numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates: int

def getParentMean(graph, parent, nodesData, parentPathCount):
    acc = 0
    for n in graph.successors(parent):
        acc += nodesData[n].numberOfPaths * (nodesData[n].meanLengthOfPath + 1)
    return Decimal(acc) / Decimal(parentPathCount)

def getParentVariance(graph, parent, nodesData, parentPathCount, parentMean):
    acc = 0
    for n in graph.successors(parent):
        acc += nodesData[n].numberOfPaths * (nodesData[n].varianceLengthOfPath + ((nodesData[n].meanLengthOfPath + 1) - parentMean)**2)
    return Decimal(acc) / Decimal(parentPathCount)

def getParentMaxLengthOfPath(graph, parent, nodesData):
    maxLengthOfChildrenPath = max(nodesData[n].maxLengthOfPath for n in graph.successors(parent))
    parentNumberOfPathsWithMaxLength = sum(nodesData[n].numberOfPathsWithMaxLength for n in graph.successors(parent) if nodesData[n].maxLengthOfPath == maxLengthOfChildrenPath)

    return (maxLengthOfChildrenPath + 1, parentNumberOfPathsWithMaxLength)

def twoQubitGates(graph, parent, nodesData, parentMaxLengthOfPath):
    maxNumberOfTwoQubitGatesInPathsWithMaxLength = max(nodesData[n].maxNumberOfTwoQubitGatesInPathsWithMaxLength for n in graph.successors(parent))

    numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates = sum(nodesData[n].numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates for n in graph.successors(parent) if nodesData[n].maxLengthOfPath == (parentMaxLengthOfPath - 1) and nodesData[n].maxNumberOfTwoQubitGatesInPathsWithMaxLength == maxNumberOfTwoQubitGatesInPathsWithMaxLength)

    numberOfQubitOperands = 0 if isinstance(parent, str) else sum(1 for op in parent[1].operands if isinstance(op, CQASMParser.Qubit))
    assert numberOfQubitOperands <= 2, "contains a 3+ qubits gate"
    if numberOfQubitOperands == 2:
        maxNumberOfTwoQubitGatesInPathsWithMaxLength += 1
    
    return (maxNumberOfTwoQubitGatesInPathsWithMaxLength, numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates)
    

def pathStatistics(graph):
    reversedGraphView = graph.reverse(copy=False)

    nodesData = { "SINK": PropagatedData(
                numberOfPaths = 1,
                meanLengthOfPath = Decimal(-1),
                varianceLengthOfPath = Decimal(0),
                maxLengthOfPath = 0,
                numberOfPathsWithMaxLength = 1,
                maxNumberOfTwoQubitGatesInPathsWithMaxLength = 0,
                numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates = 1,
            )
        }

    for node in networkx.topological_sort(reversedGraphView):
        if node == "SINK":
            continue

        assert(node not in nodesData)

        numberOfPaths = sum(nodesData[s].numberOfPaths for s in graph.successors(node))
        meanLengthOfPath = getParentMean(graph, node, nodesData, numberOfPaths)
        varianceLengthOfPath = getParentVariance(graph, node, nodesData, numberOfPaths, meanLengthOfPath)
        maxLengthOfPath, numberOfPathsWithMaxLength = getParentMaxLengthOfPath(graph, node, nodesData)

        (maxNumberOfTwoQubitGatesInPathsWithMaxLength, numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates) = twoQubitGates(graph, node, nodesData, maxLengthOfPath)

        assert(numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates <= numberOfPathsWithMaxLength)

        nodesData[node] = PropagatedData(
                numberOfPaths = numberOfPaths,
                meanLengthOfPath = meanLengthOfPath,
                varianceLengthOfPath = varianceLengthOfPath,
                maxLengthOfPath = maxLengthOfPath,
                numberOfPathsWithMaxLength = numberOfPathsWithMaxLength,
                maxNumberOfTwoQubitGatesInPathsWithMaxLength = maxNumberOfTwoQubitGatesInPathsWithMaxLength,
                numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates = numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates,
            )

    return nodesData["SOURCE"]



def getPathStats(c: list[CQASMParser.Instruction]):
    graph = buildDDG(c)

    stats = pathStatistics(graph)

    return {
        "NumberOfGatesInCriticalPath": stats.maxLengthOfPath - 1,
        "MaxNumberOfTwoQubitGatesInCriticalPath": stats.maxNumberOfTwoQubitGatesInPathsWithMaxLength,
        "NumberOfCriticalPaths": stats.numberOfPathsWithMaxLength,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": stats.numberOfPathsWithMaxLengthWithMaxNumberOfTwoQubitGates,
        "PathLengthMean": stats.meanLengthOfPath,
        "PathLengthStandardDeviation": stats.varianceLengthOfPath.sqrt(),
    }


def checkSame(a, b):
    decimalKeys = {"PathLengthMean", "PathLengthStandardDeviation"}
    for k in decimalKeys:
        assert(abs(a[k] - b[k]) < Decimal(0.00000001))

    assert(list(v for k, v in a.items() if k not in decimalKeys) == list(v for k, v in b.items() if k not in decimalKeys)) 

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
        "PathLengthMean": Decimal(3.5),
        "PathLengthStandardDeviation": Decimal(0.5),
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
        "PathLengthMean": Decimal(3),
        "PathLengthStandardDeviation": Decimal(0),
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
        "PathLengthMean": Decimal(1.5),
        "PathLengthStandardDeviation": Decimal(0.5),
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


def test5():
    cq = """
    version 1.0

qubits 3

.testCircuit
  h q[0]
  h q[1]
  h q[2]
  cnot q[0], q[1]
  cnot q[1], q[2]
  h q[0]
"""

    output = getPathStats(CQASMParser.parseCQASMString(cq).subcircuits[0].instructions)

    expected = {
        "NumberOfGatesInCriticalPath": 3,
        "MaxNumberOfTwoQubitGatesInCriticalPath": 2,
        "NumberOfCriticalPaths": 4,
        "NumberOfCriticalPathsWithMaxTwoQubitsGates": 2,
        "PathLengthMean": Decimal(2.8),
        "PathLengthStandardDeviation": Decimal(0.4),
    }

    checkSame(output, expected)


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
