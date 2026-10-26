"""Ejercicio 4: Recocido Simulado (2-opt) con distintos esquemas de enfriamiento."""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import (FIG_DIR, RES_DIR, dist_matrix, random_instance,
                    simulated_annealing, temperature)

SCHEDULES = ["lineal", "exponencial", "logaritmico"]
COLORS = {"lineal": "tab:blue", "exponencial": "tab:red", "logaritmico": "tab:green"}


def main(n=40, seed=3, T0=50.0, Tf=0.05, n_runs=8):
    rng = np.random.default_rng(seed)
    D = dist_matrix(random_instance(n, rng)).tolist()

    # 1) Curvas de convergencia (una corrida representativa)
    iters = 100_000
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    for s in SCHEDULES:
        _, _, (hi, hc, hb, hT) = simulated_annealing(D, s, iters, T0, Tf, seed=1, log_every=200)
        ax[0].plot(hi, hc, color=COLORS[s], alpha=0.7, label=s)
        ax[1].plot(hi, hb, color=COLORS[s], label=s)
        ax[2].plot(hT, hc, color=COLORS[s], alpha=0.7, label=s)
    ax[0].set_title("Costo actual vs. iteraciones"); ax[0].set_xlabel("iteración")
    ax[1].set_title("Mejor costo vs. iteraciones"); ax[1].set_xlabel("iteración")
    ax[2].set_title("Costo actual vs. temperatura"); ax[2].set_xlabel("temperatura (eje invertido)")
    ax[2].set_xscale("log"); ax[2].invert_xaxis()
    for a in ax:
        a.set_ylabel("costo"); a.grid(alpha=0.3); a.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "ej4_convergencia.png"), dpi=150)
    plt.close(fig)

    plt.figure(figsize=(5.5, 4))
    for s in SCHEDULES:
        plt.plot(range(0, iters, 200), [temperature(s, i, iters, T0, Tf) for i in range(0, iters, 200)],
                 color=COLORS[s], label=s)
    plt.yscale("log"); plt.xlabel("iteración"); plt.ylabel("T"); plt.title("Esquemas de enfriamiento")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "ej4_esquemas.png"), dpi=150)
    plt.close()

    # 2) Tiempo vs. calidad con distintos presupuestos de iteraciones
    budgets = [5_000, 20_000, 50_000, 100_000, 200_000]
    stats = {s: [] for s in SCHEDULES}
    with open(os.path.join(RES_DIR, "ej4_sa.csv"), "w") as f:
        f.write("esquema,iteraciones,tiempo_medio_s,costo_medio,costo_std,costo_min\n")
        for s in SCHEDULES:
            for b in budgets:
                costs, times = [], []
                for r in range(n_runs):
                    t0 = time.perf_counter()
                    _, best, _ = simulated_annealing(D, s, b, T0, Tf, seed=100 + r)
                    times.append(time.perf_counter() - t0)
                    costs.append(best)
                stats[s].append((np.mean(times), np.mean(costs), np.std(costs)))
                f.write(f"{s},{b},{np.mean(times):.3f},{np.mean(costs):.2f},{np.std(costs):.2f},{np.min(costs):.2f}\n")
                print(f"{s:<12} it={b:<7} t={np.mean(times):.2f}s costo={np.mean(costs):.1f}±{np.std(costs):.1f}")

    plt.figure(figsize=(7, 4.8))
    for s in SCHEDULES:
        t = [x[0] for x in stats[s]]; c = [x[1] for x in stats[s]]; e = [x[2] for x in stats[s]]
        plt.errorbar(t, c, yerr=e, fmt="o-", color=COLORS[s], capsize=3, label=s)
    plt.xlabel("Tiempo de ejecución promedio (s)")
    plt.ylabel("Costo final promedio (menor = mejor)")
    plt.title(f"SA: tiempo vs. calidad (n={n}, {n_runs} corridas)")
    plt.grid(alpha=0.3); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "ej4_tiempo_vs_calidad.png"), dpi=150)


if __name__ == "__main__":
    main()
