import typing
from parsing import CQASMParser

def longestCommonPrefix(s1, s2):
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            return i
    return min(len(s1), len(s2))

class SublistViewIterator:
    def __init__(self, sublistView):
        self.sublistView = sublistView
        self.current = 0

    def __next__(self):
        if self.current < len(self.sublistView):
            resultIndex = self.current
            self.current += 1
            return self.sublistView.data[resultIndex]
        
        raise StopIteration


class SublistView:
    def __init__(self, data, start, end):
        assert end is None or start <= end
        assert end is None or end < len(data)

        self.data = data
        self.start = start
        self.stop = end
        self.currentIndex = start
    
    def __len__(self):
        if self.stop is not None and self.start is not None:
            return self.stop - self.start
        elif self.start is not None:
            return len(self.data) - self.start
        elif self.stop is not None:
            return self.stop
        else:
            assert False
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            assert key.step is None, "Unimplemented: non-1 step"
            assert key.stop is None or key.stop < len(self)
            assert key.start is None or key.start < len(self)

            if self.start is None and key.start is None:
                subStart = None
            elif self.start is None and key.start is not None:
                subStart = key.start
            elif self.start is not None and key.start is None:
                subStart = self.start
            else:
                subStart = self.start + key.start
            
            assert subStart is None or subStart < len(self.data)

            if key.stop is None:
                subStop = self.stop
            else:
                assert key.stop < len(self)
                subStop = (0 if self.start is None else self.start) + key.stop

            assert subStop is None or subStop < len(self.data)

            return SublistView(self.data, subStart, subStop)

        assert key < len(self)
        return self.data[self.start + key]   

    def __iter__(self):
        return SublistViewIterator(self)

    def __list__(self):
        return self.data[slice(self.start, self.stop, 1)]


class SuffixTree:
    def __init__(self):
        self.instructions = []
        self.position = -1
        self.children = []
    
    def __repr__(self):
        return "{ " + repr(self.instructions) + ("(" + str(self.position) + ")" if self.position != -1 else "") + " - " + ", ".join(map(repr, self.children)) + "}"

    def add(self, instr: SublistView, position: int):
        for child in self.children:
            if child is not None:
                cp = longestCommonPrefix(instr, child.instructions)
                if cp == len(child.instructions):
                    child.add(instr[len(child.instructions):], position)
                    return
                
                if cp > 0:
                    newChild1 = SuffixTree()
                    newChild1.instructions = child.instructions[cp:]
                    newChild1.children = child.children
                    newChild1.position = child.position

                    newChild2 = SuffixTree()
                    newChild2.instructions = instr[cp:]
                    newChild2.position = position
                    
                    child.instructions = child.instructions[:cp]
                    child.position = -1
                    child.children = [newChild1, newChild2]
                    return


        
        newChild1 = SuffixTree()
        newChild1.instructions = instr
        newChild1.position = position

        if (self.children == []):
            self.children = [newChild1, None]
        else:
            self.children += [newChild1]

    def deepestInternalNode(self) -> (list[CQASMParser.Instruction], int):
        if self.children == []:
            return ([], 0)
        
        subresults = map(lambda c: c.deepestInternalNode(), filter(lambda c: c is not None, self.children))

        m = max(subresults, key = lambda x: len(x[0]))
        
        if len(m[0]) == 0:
            return (list(self.instructions), len(self.children))
        
        return (list(self.instructions) + m[0], m[1])



# naive construction of suffix tree
def longestRepeatingSubcircuit(c: list[CQASMParser.Instruction]):
    t = SuffixTree()
    for i in range(len(c)):
        start = len(c) - i - 1
        t.add(instr=SublistView(c, start, None), position=start)

    deepestInternalNode = t.deepestInternalNode()
    return { "LongestRepeatingSubcircuit": deepestInternalNode[0], "NumberOfRepetitionsOfLongestRepeatingSubcircuit": deepestInternalNode[1] if deepestInternalNode[0] != [] else 0 }

