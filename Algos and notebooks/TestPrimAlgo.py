from PrimAlgo import Graph, prims_mst

import math
g = Graph(representation='matrix', nfverts=6)
lst = [
    [math.inf, 3, 4, math.inf, 1],
    [3, math.inf, 5, math.inf, math.inf],
    [4, 5, math.inf, 2, 6],
    [math.inf, math.inf, 2, math.inf, 7],
    [1, math.inf, 6,  7, math.inf]
]
# lst = [
# [0, 4, 0, 0, 6, 5],
# [4, 0, 1, 0, 0, 4],
# [0, 1, 0, 6, 0, 4],
# [0, 0, 6, 0, 8, 5],
# [6, 0, 0, 8, 0, 2],
# [5, 4, 4, 5, 2, 0]
# ]
g.graph = lst
g.matrix_to_lists()
ans = prims_mst(g)
print(ans)

# print(lst)
# print(g.graph.items())