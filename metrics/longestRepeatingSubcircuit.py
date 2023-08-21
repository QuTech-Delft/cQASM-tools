import typing
from parsing import CQASMParser

def longestCommonPrefix(s1, s2):
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            return i
    return min(len(s1), len(s2))

class SuffixTree:
    def __init__(self):
        self.instructions = []
        self.position = -1
        self.children = []
    
    def __repr__(self):
        return "{ " + repr(self.instructions) + ("(" + str(self.position) + ")" if self.position != -1 else "") + " - " + ", ".join(map(repr, self.children)) + "}"

    def add(self, instr: list[CQASMParser.Instruction], position: int):
        for c in self.children:
            if c is not None:
                cp = longestCommonPrefix(instr, c.instructions)
                if cp == len(c.instructions):
                    c.add(instr[len(c.instructions):], position)
                    return
                
                if cp > 0:
                    newChild1 = SuffixTree()
                    newChild1.instructions = c.instructions[cp:]
                    newChild1.children = c.children
                    newChild1.position = c.position

                    newChild2 = SuffixTree()
                    newChild2.instructions = instr[cp:]
                    newChild2.position = position
                    
                    c.instructions = c.instructions[:cp]
                    c.position = -1
                    c.children = [newChild1, newChild2]
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

        if m[0] == []:
            return (self.instructions, len(self.children))
        
        return (self.instructions + m[0], m[1])


# naive construction of suffix tree
def longestRepeatingSubcircuit(c: list[CQASMParser.Instruction]):
    t = SuffixTree()
    for i in range(len(c)):
        start = len(c) - i - 1
        t.add(instr=c[start:], position=start)

    deepestInternalNode = t.deepestInternalNode()
    return { "LongestRepeatingSubcircuit": deepestInternalNode[0], "NumberOfRepetitionsOfLongestRepeatingSubcircuit": deepestInternalNode[1] }

