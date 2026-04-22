from pathlib import Path
from collections import deque


# =========================================================
# 1) READ PROBLEM
# =========================================================
def read_problem(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    n, m = map(int, lines[0].split())

    costs = []
    supply = []

    for i in range(1, n + 1):
        row = list(map(int, lines[i].split()))
        costs.append(row[:m])
        supply.append(row[m])

    demand = list(map(int, lines[n + 1].split()))

    if sum(supply) != sum(demand):
        raise ValueError("Problem is not balanced.")

    return n, m, costs, supply, demand


# =========================================================
# 2) DISPLAY FUNCTIONS
# =========================================================
def display_cost_matrix(costs, supply, demand):
    n = len(costs)
    m = len(costs[0])

    print("\nCOST MATRIX")
    header = "      " + "".join(f"C{j+1:>10}" for j in range(m)) + f"{'Supply':>10}"
    print(header)

    for i in range(n):
        row = f"P{i+1:<4} "
        for j in range(m):
            row += f"{costs[i][j]:>10}"
        row += f"{supply[i]:>10}"
        print(row)

    bottom = f"{'Demand':<6}"
    for j in range(m):
        bottom += f"{demand[j]:>10}"
    print(bottom)


def display_transport(alloc, supply, demand, title="TRANSPORT PROPOSAL"):
    n = len(alloc)
    m = len(alloc[0])

    print(f"\n{title}")
    header = "      " + "".join(f"C{j+1:>10}" for j in range(m)) + f"{'Supply':>10}"
    print(header)

    for i in range(n):
        row = f"P{i+1:<4} "
        for j in range(m):
            value = alloc[i][j]
            shown = "." if value == 0 else str(value)
            row += f"{shown:>10}"
        row += f"{supply[i]:>10}"
        print(row)

    bottom = f"{'Demand':<6}"
    for j in range(m):
        bottom += f"{demand[j]:>10}"
    print(bottom)


def display_table(matrix, title):
    n = len(matrix)
    m = len(matrix[0])

    print(f"\n{title}")
    header = "      " + "".join(f"C{j+1:>10}" for j in range(m))
    print(header)

    for i in range(n):
        row = f"P{i+1:<4} "
        for j in range(m):
            row += f"{matrix[i][j]:>10}"
        print(row)


# =========================================================
# 3) BASIC COST FUNCTION
# =========================================================
def total_cost(costs, alloc):
    total = 0
    for i in range(len(costs)):
        for j in range(len(costs[0])):
            total += costs[i][j] * alloc[i][j]
    return total


# =========================================================
# 4) INITIAL SOLUTION: NORTH-WEST
# =========================================================
def north_west(costs, supply, demand):
    n = len(costs)
    m = len(costs[0])

    s = supply[:]
    d = demand[:]
    alloc = [[0] * m for _ in range(n)]

    i = 0
    j = 0

    print("\n===== NORTH-WEST METHOD =====")

    while i < n and j < m:
        x = min(s[i], d[j])
        alloc[i][j] = x

        print(f"Allocate {x} to (P{i+1}, C{j+1})")

        s[i] -= x
        d[j] -= x

        if s[i] == 0 and d[j] == 0:
            i += 1
            j += 1
        elif s[i] == 0:
            i += 1
        else:
            j += 1

    return alloc


# =========================================================
# 5) INITIAL SOLUTION: BALAS-HAMMER
# =========================================================
def row_penalty(costs, active_cols, i):
    values = [costs[i][j] for j in range(len(costs[0])) if active_cols[j]]
    values.sort()
    if len(values) == 1:
        return values[0]
    return values[1] - values[0]


def col_penalty(costs, active_rows, j):
    values = [costs[i][j] for i in range(len(costs)) if active_rows[i]]
    values.sort()
    if len(values) == 1:
        return values[0]
    return values[1] - values[0]


def balas_hammer(costs, supply, demand):
    n = len(costs)
    m = len(costs[0])

    s = supply[:]
    d = demand[:]
    alloc = [[0] * m for _ in range(n)]

    active_rows = [True] * n
    active_cols = [True] * m

    print("\n===== BALAS-HAMMER METHOD =====")

    while any(active_rows) and any(active_cols):
        penalties = []

        for i in range(n):
            if active_rows[i]:
                penalties.append((row_penalty(costs, active_cols, i), "row", i))

        for j in range(m):
            if active_cols[j]:
                penalties.append((col_penalty(costs, active_rows, j), "col", j))

        max_pen = max(p[0] for p in penalties)
        print(f"\nMaximum penalty = {max_pen}")

        best_penalties = [p for p in penalties if p[0] == max_pen]
        for p in best_penalties:
            if p[1] == "row":
                print(f"Row with max penalty: P{p[2] + 1}")
            else:
                print(f"Column with max penalty: C{p[2] + 1}")

        penalties.sort(reverse=True)
        _, kind, index = penalties[0]

        if kind == "row":
            i = index
            candidates = [(costs[i][j], j) for j in range(m) if active_cols[j]]
            candidates.sort()
            j = candidates[0][1]
        else:
            j = index
            candidates = [(costs[i][j], i) for i in range(n) if active_rows[i]]
            candidates.sort()
            i = candidates[0][1]

        print(f"Chosen cell: (P{i+1}, C{j+1}) with cost {costs[i][j]}")

        x = min(s[i], d[j])
        alloc[i][j] = x
        print(f"Allocate {x}")

        s[i] -= x
        d[j] -= x

        if s[i] == 0:
            active_rows[i] = False
        if d[j] == 0:
            active_cols[j] = False

    return alloc


# =========================================================
# 6) BASIS / GRAPH TOOLS
# =========================================================
def get_basis(alloc):
    basis = []
    for i in range(len(alloc)):
        for j in range(len(alloc[0])):
            if alloc[i][j] > 0:
                basis.append((i, j))
    return basis


def build_graph_from_basis(n, m, basis):
    graph = {}

    for i in range(n):
        graph[("P", i)] = []
    for j in range(m):
        graph[("C", j)] = []

    for i, j in basis:
        graph[("P", i)].append(("C", j))
        graph[("C", j)].append(("P", i))

    return graph


def bfs_connected_components(n, m, basis):
    graph = build_graph_from_basis(n, m, basis)
    visited = set()
    components = []

    for node in graph:
        if node not in visited:
            comp = []
            q = deque([node])
            visited.add(node)

            while q:
                current = q.popleft()
                comp.append(current)

                for nxt in graph[current]:
                    if nxt not in visited:
                        visited.add(nxt)
                        q.append(nxt)

            components.append(comp)

    return components


def is_connected(n, m, basis):
    components = bfs_connected_components(n, m, basis)
    return len(components) == 1


def find_path_bfs(graph, start, end):
    q = deque([start])
    parent = {start: None}

    while q:
        current = q.popleft()

        if current == end:
            break

        for nxt in graph[current]:
            if nxt not in parent:
                parent[nxt] = current
                q.append(nxt)

    if end not in parent:
        return None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def path_nodes_to_cells(path):
    cells = []
    for k in range(len(path) - 1):
        a = path[k]
        b = path[k + 1]
        if a[0] == "P":
            cells.append((a[1], b[1]))
        else:
            cells.append((b[1], a[1]))
    return cells


# =========================================================
# 7) DEGENERACY / TREE REPAIR
# =========================================================
def make_non_degenerate(costs, alloc):
    n = len(costs)
    m = len(costs[0])

    while len(get_basis(alloc)) < n + m - 1:
        basis = get_basis(alloc)
        graph = build_graph_from_basis(n, m, basis)

        best_cell = None
        best_cost = float("inf")

        for i in range(n):
            for j in range(m):
                if alloc[i][j] == 0:
                    path = find_path_bfs(graph, ("P", i), ("C", j))
                    if path is None:
                        if costs[i][j] < best_cost:
                            best_cost = costs[i][j]
                            best_cell = (i, j)

        if best_cell is None:
            break

        i, j = best_cell
        alloc[i][j] = 0.000001
        print(f"Added epsilon edge to make tree: (P{i+1}, C{j+1})")

    return alloc


# =========================================================
# 8) POTENTIALS
# =========================================================
def compute_potentials(costs, alloc):
    n = len(costs)
    m = len(costs[0])
    basis = get_basis(alloc)

    u = [None] * n
    v = [None] * m

    u[0] = 0
    changed = True

    while changed:
        changed = False
        for i, j in basis:
            if u[i] is not None and v[j] is None:
                v[j] = costs[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = costs[i][j] - v[j]
                changed = True

    for i in range(n):
        if u[i] is None:
            u[i] = 0
    for j in range(m):
        if v[j] is None:
            v[j] = 0

    return u, v


def potential_cost_table(u, v):
    n = len(u)
    m = len(v)
    table = [[0] * m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            table[i][j] = u[i] + v[j]

    return table


def marginal_cost_table(costs, u, v):
    n = len(costs)
    m = len(costs[0])
    table = [[0] * m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            table[i][j] = costs[i][j] - (u[i] + v[j])

    return table


# =========================================================
# 9) IMPROVING EDGE
# =========================================================
def best_improving_edge(alloc, marginals):
    best_value = 0
    best_cell = None

    for i in range(len(alloc)):
        for j in range(len(alloc[0])):
            if alloc[i][j] == 0 and marginals[i][j] < best_value:
                best_value = marginals[i][j]
                best_cell = (i, j)

    return best_cell, best_value


# =========================================================
# 10) CYCLE DETECTION FOR ENTERING EDGE
# =========================================================
def find_cycle_for_entering_edge(alloc, entering_cell):
    n = len(alloc)
    m = len(alloc[0])

    basis = get_basis(alloc)
    graph = build_graph_from_basis(n, m, basis)

    i, j = entering_cell
    path = find_path_bfs(graph, ("P", i), ("C", j))

    if path is None:
        return None

    path_cells = path_nodes_to_cells(path)
    cycle = [entering_cell] + list(reversed(path_cells))
    return cycle


def display_cycle(cycle):
    s = " -> ".join([f"(P{i+1},C{j+1})" for i, j in cycle])
    print("Cycle:", s)


# =========================================================
# 11) MAXIMIZATION ON CYCLE
# =========================================================
def maximize_on_cycle(alloc, cycle):
    plus_cells = cycle[0::2]
    minus_cells = cycle[1::2]

    print("Plus cells:", [f"(P{i+1},C{j+1})" for i, j in plus_cells])
    print("Minus cells:", [f"(P{i+1},C{j+1})" for i, j in minus_cells])

    theta = min(alloc[i][j] for i, j in minus_cells)
    print("theta =", theta)

    for i, j in plus_cells:
        alloc[i][j] += theta

    for i, j in minus_cells:
        alloc[i][j] -= theta

    deleted = []
    for i, j in minus_cells:
        if abs(alloc[i][j]) < 1e-12:
            alloc[i][j] = 0
            deleted.append((i, j))

    if deleted:
        print("Deleted edge(s):", [f"(P{i+1},C{j+1})" for i, j in deleted])

    return alloc


# =========================================================
# 12) STEPPING-STONE METHOD WITH POTENTIALS
# =========================================================
def stepping_stone(costs, supply, demand, alloc):
    n = len(costs)
    m = len(costs[0])

    print("\n===== STEPPING-STONE METHOD WITH POTENTIALS =====")

    iteration = 1

    while True:
        print(f"\n========== ITERATION {iteration} ==========")
        display_transport(alloc, supply, demand, "CURRENT TRANSPORT PROPOSAL")
        print("Current total cost =", total_cost(costs, alloc))

        # Degeneracy test
        basis = get_basis(alloc)
        print("\nNumber of basic edges =", len(basis))
        print("Expected for a tree =", n + m - 1)

        if len(basis) < n + m - 1:
            print("Proposition is degenerate or not a tree.")
            alloc = make_non_degenerate(costs, alloc)
        else:
            print("Proposition is non-degenerate.")

        # Connectivity test with BFS
        basis = get_basis(alloc)
        components = bfs_connected_components(n, m, basis)

        if len(components) == 1:
            print("Graph is connected.")
        else:
            print("Graph is NOT connected.")
            print("Connected subgraphs:")
            for k, comp in enumerate(components, start=1):
                pretty = []
                for node in comp:
                    if node[0] == "P":
                        pretty.append(f"P{node[1]+1}")
                    else:
                        pretty.append(f"C{node[1]+1}")
                print(f"Subgraph {k}: {pretty}")

            alloc = make_non_degenerate(costs, alloc)

        # Potentials
        u, v = compute_potentials(costs, alloc)
        print("\nPotentials:")
        print("u =", u)
        print("v =", v)

        pot_table = potential_cost_table(u, v)
        marg_table = marginal_cost_table(costs, u, v)

        display_table(pot_table, "POTENTIAL COSTS TABLE")
        display_table(marg_table, "MARGINAL COSTS TABLE")

        # Best improving edge
        entering_cell, value = best_improving_edge(alloc, marg_table)

        if entering_cell is None:
            print("\nNo negative marginal cost.")
            print("The current solution is optimal.")
            break

        i, j = entering_cell
        print(f"\nBest improving edge: (P{i+1}, C{j+1}) with marginal cost {value}")

        cycle = find_cycle_for_entering_edge(alloc, entering_cell)
        if cycle is None:
            print("No cycle found. Stop.")
            break

        display_cycle(cycle)

        alloc = maximize_on_cycle(alloc, cycle)
        iteration += 1

    return alloc


# =========================================================
# 13) MAIN LOOP
# =========================================================
def main():
    while True:
        print("\n=====================================")
        print("TRANSPORTATION PROBLEM PROJECT")
        print("=====================================")

        number = input("Choose problem number (1 to 12): ").strip()
        if number.lower() == "q":
            print("Goodbye.")
            break

        method = input("Choose initial method (nw or bh): ").strip().lower()

        file_path = Path("data") / f"problem{number}.txt"

        if not file_path.exists():
            print("File not found:", file_path)
            continue

        try:
            n, m, costs, supply, demand = read_problem(file_path)
        except Exception as e:
            print("Error while reading file:", e)
            continue

        print(f"\nProblem loaded: {file_path.name}")
        print(f"n = {n}, m = {m}")

        display_cost_matrix(costs, supply, demand)

        if method == "nw":
            alloc = north_west(costs, supply, demand)
            display_transport(alloc, supply, demand, "INITIAL PROPOSAL - NORTH-WEST")
        elif method == "bh":
            alloc = balas_hammer(costs, supply, demand)
            display_transport(alloc, supply, demand, "INITIAL PROPOSAL - BALAS-HAMMER")
        else:
            print("Unknown method. Use 'nw' or 'bh'.")
            continue

        print("\nInitial total cost =", total_cost(costs, alloc))

        alloc = stepping_stone(costs, supply, demand, alloc)

        print("\n========== FINAL MINIMAL PROPOSAL ==========")
        display_transport(alloc, supply, demand, "FINAL TRANSPORT PROPOSAL")
        print("Final minimal cost =", total_cost(costs, alloc))

        again = input("\nDo you want to test another transportation problem? (y/n): ").strip().lower()
        if again != "y":
            print("End of program.")
            break


if __name__ == "__main__":
    main()