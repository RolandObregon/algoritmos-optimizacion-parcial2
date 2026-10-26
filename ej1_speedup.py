"""Ejercicio 1: speedup paralelo de estimate_pi (Monte Carlo) con 1, 2, 4 y 8 procesos."""
import os
import statistics
import time
from multiprocessing import Pool

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import FIG_DIR, RES_DIR, ROOT

BLOCK = 1_000_000


def _count_inside(args):
    n, seed_seq = args
    rng = np.random.default_rng(seed_seq)
    inside, done = 0, 0
    while done < n:
        m = min(BLOCK, n - done)
        x, y = rng.random(m), rng.random(m)
        inside += int(np.count_nonzero(x * x + y * y <= 1.0))
        done += m
    return inside


def estimate_pi(total, procs, seed=0):
    seeds = np.random.SeedSequence(seed).spawn(procs)
    base, extra = divmod(total, procs)
    tasks = [(base + (1 if k < extra else 0), seeds[k]) for k in range(procs)]
    if procs == 1:
        inside = _count_inside(tasks[0])
    else:
        with Pool(procs) as pool:
            inside = sum(pool.map(_count_inside, tasks))
    return 4.0 * inside / total


def main(total=40_000_000, reps=5):
    procs_list = [1, 2, 4, 8]
    times = {}
    for p in procs_list:
        runs = []
        for r in range(reps):
            t0 = time.perf_counter()
            pi = estimate_pi(total, p, seed=r)
            runs.append(time.perf_counter() - t0)
        times[p] = statistics.median(runs)
        print(f"procesos={p}: mediana={times[p]:.3f}s  pi~{pi:.6f}")
    speedup = [times[1] / times[p] for p in procs_list]
    eff = [s / p for s, p in zip(speedup, procs_list)]

    with open(os.path.join(RES_DIR, "ej1_speedup.csv"), "w") as f:
        f.write("procesos,tiempo_s,speedup,eficiencia\n")
        for p, s, e in zip(procs_list, speedup, eff):
            f.write(f"{p},{times[p]:.4f},{s:.3f},{e:.3f}\n")

    plt.figure(figsize=(6, 4.5))
    plt.plot(procs_list, procs_list, "k--", label="Speedup ideal (S = p)")
    plt.plot(procs_list, speedup, "o-", color="tab:blue", label="Speedup medido")
    plt.xticks(procs_list)
    plt.xlabel("Número de procesos")
    plt.ylabel("Speedup  T(1) / T(p)")
    plt.title(f"estimate_pi: speedup (N={total:,}, CPUs={os.cpu_count()})")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "ej1_speedup.png"), dpi=150)
    print("Speedups:", [round(s, 2) for s in speedup])
    update_readme(procs_list, times, speedup, eff)


def update_readme(procs_list, times, speedup, eff, readme=None):
    """Escribe en el README (entre marcadores) los núcleos y speedups reales medidos."""
    readme = readme or os.path.join(ROOT, "README.md")
    if not os.path.exists(readme):
        return
    lines = [f"Mi equipo tiene **{os.cpu_count()} procesadores lógicos** (`os.cpu_count()`). "
             "Resultados medidos (mediana de varias corridas):", "",
             "| Procesos | Tiempo (s) | Speedup | Ideal | Eficiencia |", "|---|---|---|---|---|"]
    for p, s, e in zip(procs_list, speedup, eff):
        lines.append(f"| {p} | {times[p]:.3f} | {s:.2f} | {p} | {e*100:.0f} % |")
    block = "<!--EJ1_START-->\n" + "\n".join(lines) + "\n<!--EJ1_END-->"
    text = open(readme, encoding="utf-8").read()
    a, b = text.find("<!--EJ1_START-->"), text.find("<!--EJ1_END-->")
    if a != -1 and b != -1:
        text = text[:a] + block + text[b + len("<!--EJ1_END-->"):]
        open(readme, "w", encoding="utf-8").write(text)
        print("README actualizado con tus speedups.")


if __name__ == "__main__":
    main()
