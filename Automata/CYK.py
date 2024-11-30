def cartesian_product(a: set, b: set):
    for i in a:
        for j in b:
            yield i, j


def cyk(grammar, w):
    V: list[list[set]] = [[set() for y in range(len(w))] for x in range(len(w))]
    for i in range(w):
        V[i][i] = {x for x in grammar.keys() if w[i] in grammar[x]}
    for d in range(1, len(w)):
        for i in range(1, len(w) - d):
            j = i + d
            for k in range(i, j):
                V[i][j] = V[i][j].union({x for x in grammar.keys() for y in cartesian_product(V[i][k], V[k + 1][j]) if ''.join(y) in grammar[x]})
    for i in V:
        print(i)
    return "S" in V[0][-1]


grammar = {
    "S": ["AC", "b"],
    "A": ["a"],
    "B": ["b"],
    "C": ["SB"]
}

print(cyk(grammar, "aaabbbb"))