import random
import time
import csv
from pathlib import Path
import matplotlib.pyplot as plt

from main import north_west, balas_hammer, stepping_stone


def generate_random_problem(n):
    costs = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(random.randint(1, 100))
        costs.append(row)

    temp = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(random.randint(1, 100))
        temp.append(row)

    supply = []
    for i in range(n):
        supply.append(sum(temp[i]))

    demand = []
    for j in range(n):
        total = 0
        for i in range(n):
            total += temp[i][j]
        demand.append(total)

    return costs, supply, demand


def measure_once(n):
    costs, supply, demand = generate_random_problem(n)

    start = time.perf_counter()
    alloc_nw = north_west(costs, supply, demand)
    basis_nw = get_basis(alloc_nw)
    end = time.perf_counter()
    theta_nw = end - start

    start = time.perf_counter()
    alloc_bh = balas_hammer(costs, supply, demand)
    basis_bh = get_basis(alloc_bh)
    end = time.perf_counter()
    theta_bh = end - start

    start = time.perf_counter()
    stepping_stone(costs, supply, demand, alloc_nw)
    end = time.perf_counter()
    t_nw = end - start

    start = time.perf_counter()
    stepping_stone(costs, supply, demand, alloc_bh)
    end = time.perf_counter()
    t_bh = end - start

    return theta_nw, theta_bh, t_nw, t_bh

def get_basis(alloc):
    basis = set()
    for i in range(len(alloc)):
        for j in range(len(alloc[0])):
            if alloc[i][j] > 0:
                basis.add((i, j))
    return basis


def save_results(results):
    with open("complexity_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n",
            "theta_nw",
            "theta_bh",
            "t_nw",
            "t_bh",
            "theta_nw_plus_t_nw",
            "theta_bh_plus_t_bh",
            "ratio"
        ])

        for row in results:
            n, theta_nw, theta_bh, t_nw, t_bh = row
            total_nw = theta_nw + t_nw
            total_bh = theta_bh + t_bh

            if total_bh != 0:
                ratio = total_nw / total_bh
            else:
                ratio = 0

            writer.writerow([
                n,
                theta_nw,
                theta_bh,
                t_nw,
                t_bh,
                total_nw,
                total_bh,
                ratio
            ])


def scatter_plot(results, column_index, title, filename):
    x = []
    y = []

    for row in results:
        x.append(row[0])
        y.append(row[column_index])

    plt.figure()
    plt.scatter(x, y)
    plt.xlabel("n")
    plt.ylabel("time in seconds")
    plt.title(title)
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def worst_case_plot(results, column_index, title, filename):
    grouped = {}

    for row in results:
        n = row[0]
        value = row[column_index]

        if n not in grouped:
            grouped[n] = []

        grouped[n].append(value)

    x = []
    y = []

    for n in sorted(grouped.keys()):
        x.append(n)
        y.append(max(grouped[n]))

    plt.figure()
    plt.plot(x, y, marker="o")
    plt.xlabel("n")
    plt.ylabel("maximum time in seconds")
    plt.title(title)
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def main():
    Path("plots").mkdir(exist_ok=True)

    # Start small. Later you can try [10, 40, 100, 400]
    sizes = [10, 40, 10**2, 4*10**2, 10**3, 4*10**3, 10**4]

    # For the final project, the PDF says 100.
    # For testing, use 3 or 5 first.
    repetitions = 100

    results = []

    for n in sizes:
        print(f"\nTesting n = {n}")

        for k in range(repetitions):
            print(f"Run {k + 1}/{repetitions}")

            theta_nw, theta_bh, t_nw, t_bh = measure_once(n)

            results.append((n, theta_nw, theta_bh, t_nw, t_bh))

    save_results(results)

    scatter_plot(results, 1, "Scatter plot theta_NW(n)", "plots/scatter_theta_nw.png")
    scatter_plot(results, 2, "Scatter plot theta_BH(n)", "plots/scatter_theta_bh.png")
    scatter_plot(results, 3, "Scatter plot t_NW(n)", "plots/scatter_t_nw.png")
    scatter_plot(results, 4, "Scatter plot t_BH(n)", "plots/scatter_t_bh.png")

    total_nw_results = []
    total_bh_results = []
    ratio_results = []

    for row in results:
        n, theta_nw, theta_bh, t_nw, t_bh = row
        total_nw_results.append((n, theta_nw + t_nw))
        total_bh_results.append((n, theta_bh + t_bh))

        if theta_bh + t_bh != 0:
            ratio_results.append((n, (theta_nw + t_nw) / (theta_bh + t_bh)))
        else:
            ratio_results.append((n, 0))

    # Convert simple two-column results to compatible format
    scatter_plot([(n, v, 0, 0, 0) for n, v in total_nw_results], 1,
                 "Scatter plot theta_NW + t_NW", "plots/scatter_total_nw.png")

    scatter_plot([(n, v, 0, 0, 0) for n, v in total_bh_results], 1,
                 "Scatter plot theta_BH + t_BH", "plots/scatter_total_bh.png")

    scatter_plot([(n, v, 0, 0, 0) for n, v in ratio_results], 1,
                 "Comparison ratio NW / BH", "plots/scatter_ratio.png")

    worst_case_plot(results, 1, "Worst case theta_NW(n)", "plots/worst_theta_nw.png")
    worst_case_plot(results, 2, "Worst case theta_BH(n)", "plots/worst_theta_bh.png")
    worst_case_plot(results, 3, "Worst case t_NW(n)", "plots/worst_t_nw.png")
    worst_case_plot(results, 4, "Worst case t_BH(n)", "plots/worst_t_bh.png")

    print("\nComplexity study finished.")
    print("Results saved in complexity_results.csv")
    print("Plots saved in the plots folder.")


if __name__ == "__main__":
    main()