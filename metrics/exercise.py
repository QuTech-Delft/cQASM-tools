import networkx, math

def getParentMean(children, nodesData, parentCount):
    acc = 0.
    for n in children:
        acc += nodesData[n][0] * (nodesData[n][1] + 1)
    return acc / parentCount

def getParentVariance(children, nodesData, parentCount, parentMean):
    acc = 0.
    for n in children:
        acc += nodesData[n][0] * (nodesData[n][2] + ((nodesData[n][1] + 1) - parentMean)**2)
    return acc / parentCount

def pathLengthsStatistics(graph, source, target):
    # (count, mean, variance)

    reversedGraphView = graph.reverse(copy=False)

    nodesData = { target: (1, 0., 0.) }

    for node in networkx.topological_sort(reversedGraphView):
        if node == target:
            continue

        assert(node not in nodesData)

        parentCount = sum(nodesData[s][0] for s in graph.successors(node))
        parentMean = getParentMean(graph.successors(node), nodesData, parentCount)
        parentVariance = getParentVariance(graph.successors(node), nodesData, parentCount, parentMean)

        nodesData[node] = (parentCount, parentMean, parentVariance)

    count, mean, var = nodesData[source]
    return (count, mean, math.sqrt(var))

if __name__ == "__main__":
    g = networkx.DiGraph()
    g.add_edges_from([('a', 'b'), ('a', 'c'), ('a', 'd'), ('a', 'e'), ('b', 'd'), ('c', 'd'), ('c', 'e'), ('d', 'e')])
    st = pathLengthsStatistics(g, 'a', 'e')
    print(f"Number of paths: {st[0]}, mean length: {st[1]}, stdev of the path length: {st[2]}")