from pathlib import Path


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

    return n, m, costs, supply, demand


def display_cost_matrix(costs, supply, demand):
    n = len(costs)
    m = len(costs[0])

    print("\nCOST MATRIX")
    header = "      " + "".join(f"C{j+1:>8}" for j in range(m)) + f"{'Supply':>10}"
    print(header)

    for i in range(n):
        row = f"P{i+1:<4} "
        for j in range(m):
            row += f"{costs[i][j]:>8}"
        row += f"{supply[i]:>10}"
        print(row)

    bottom = "Demand"
    for j in range(m):
        bottom += f"{demand[j]:>8}"
    print(bottom)


def display_transport(alloc, supply, demand, title="TRANSPORT PROPOSAL"):
    n = len(alloc)
    m = len(alloc[0])

    print(f"\n{title}")
    header = "      " + "".join(f"C{j+1:>8}" for j in range(m)) + f"{'Supply':>10}"
    print(header)

    for i in range(n):
        row = f"P{i+1:<4} "
        for j in range(m):
            row += f"{alloc[i][j]:>8}"
        row += f"{supply[i]:>10}"
        print(row)

    bottom = "Demand"
    for j in range(m):
        bottom += f"{demand[j]:>8}"
    print(bottom)


def total_cost(costs, alloc):
    total = 0
    for i in range(len(costs)):
        for j in range(len(costs[0])):
            total += costs[i][j] * alloc[i][j]
    return total


def north_west(costs, supply, demand):
    n = len(costs)
    m = len(costs[0])

    s = supply[:]
    d = demand[:]
    alloc = [[0] * m for _ in range(n)]

    i = 0
    j = 0

    while i < n and j < m:
        x = min(s[i], d[j])
        alloc[i][j] = x

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

    while any(active_rows) and any(active_cols):
        penalties = []

        for i in range(n):
            if active_rows[i]:
                penalties.append((row_penalty(costs, active_cols, i), "row", i))

        for j in range(m):
            if active_cols[j]:
                penalties.append((col_penalty(costs, active_rows, j), "col", j))

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

        x = min(s[i], d[j])
        alloc[i][j] = x

        s[i] -= x
        d[j] -= x

        if s[i] == 0:
            active_rows[i] = False
        if d[j] == 0:
            active_cols[j] = False

    return alloc


def main():
    print("Transportation project")
    print("Files must be in the data folder: problem1.txt ... problem12.txt")

    number = input("Choose problem number: ").strip()
    method = input("Choose method (nw or bh): ").strip().lower()

    file_path = Path("data") / f"problem{number}.txt"

    if not file_path.exists():
        print("File not found:", file_path)
        return

    n, m, costs, supply, demand = read_problem(file_path)

    print(f"\nProblem loaded: {file_path.name}")
    print(f"n = {n}, m = {m}")

    display_cost_matrix(costs, supply, demand)

    if method == "nw":
        alloc = north_west(costs, supply, demand)
        display_transport(alloc, supply, demand, "TRANSPORT PROPOSAL - NORTH WEST")
    elif method == "bh":
        alloc = balas_hammer(costs, supply, demand)
        display_transport(alloc, supply, demand, "TRANSPORT PROPOSAL - BALAS HAMMER")
    else:
        print("Unknown method. Use 'nw' or 'bh'.")
        return

    print("\nTOTAL COST =", total_cost(costs, alloc))


if __name__ == "__main__":
    main()