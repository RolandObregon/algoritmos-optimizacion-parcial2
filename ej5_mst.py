"""Ejercicio 5: razón de aproximación del algoritmo MST (100 instancias de 9 ciudades)."""
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import (FIG_DIR, RES_DIR, dist_matrix, held_karp, mst_tour,
                    random_instance, simulated_annealing, tour_cost, two_opt)


def main(n=9, n_inst=100, seed=11):
    rng = np.random.default_rng(seed)
    rnd = random.Random(seed)
    opt, mst, mst2, ls, sa = [], [], [], [], []
    for k in range(n_inst):
        D = dist_matrix(random_instance(n, rng)).tolist()
        opt.append(held_karp(D))
        t = mst_tour(D)
        mst.append(tour_cost(t, D))
        mst2.append(two_opt(t, D)[1])
        r = list(range(n)); rnd.shuffle(r)
        ls.append(two_opt(r, D)[1])
        sa.append(simulated_annealing(D, "exponencial", 20_000, 20.0, 0.05, seed=k)[1])
    opt, mst, mst2, ls, sa = map(np.array, (opt, mst, mst2, ls, sa))
    ratios = {"MST puro": mst / opt, "MST + 2-opt": mst2 / opt,
              "Búsqueda local\n(2-opt aleatorio)": ls / opt, "Recocido simulado": sa / opt}

    with open(os.path.join(RES_DIR, "ej5_mst.csv"), "w") as f:
        f.write("instancia,optimo,mst,mst_2opt,2opt_aleatorio,sa\n")
        for i in range(n_inst):
            f.write(f"{i},{opt[i]:.2f},{mst[i]:.2f},{mst2[i]:.2f},{ls[i]:.2f},{sa[i]:.2f}\n")

    r = ratios["MST puro"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    ax[0].hist(r, bins=15, color="tab:blue", edgecolor="k", alpha=0.8)
    ax[0].axvline(2, color="r", ls="--", label="límite teórico = 2")
    ax[0].axvline(r.mean(), color="k", ls=":", label=f"media = {r.mean():.3f}")
    ax[0].set_xlim(0.95, 2.1); ax[0].set_xlabel("C_obtenido / C_óptimo"); ax[0].set_ylabel("frecuencia")
    ax[0].set_title("Razón de aproximación (MST puro)"); ax[0].legend()
    ax[1].scatter(range(n_inst), r, s=14)
    ax[1].axhline(2, color="r", ls="--", label="límite = 2")
    ax[1].axhline(1, color="g", ls="--", label="óptimo = 1")
    ax[1].set_ylim(0.9, 2.1); ax[1].set_xlabel("instancia"); ax[1].set_ylabel("razón")
    ax[1].set_title("Razón por instancia"); ax[1].legend()
    fig.tight_layout(); fig.savefig(os.path.join(FIG_DIR, "ej5_razon_mst.png"), dpi=150); plt.close(fig)

    names = list(ratios)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].boxplot([mst, mst2, ls, sa], tick_labels=names); ax[0].set_ylabel("costo del tour")
    ax[0].set_title("Costo obtenido (100 instancias, 9 ciudades)")
    ax[1].boxplot([ratios[k] for k in names], tick_labels=names)
    ax[1].axhline(1, color="g", ls="--"); ax[1].set_ylabel("C_obtenido / C_óptimo")
    ax[1].set_title("Razón de aproximación por método")
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIG_DIR, "ej5_comparativa.png"), dpi=150); plt.close(fig)

    print(f"{'Método':<28}{'media':>8}{'mediana':>9}{'máx':>8}{'% óptimo':>10}")
    for k, v in ratios.items():
        print(f"{k.replace(chr(10), ' '):<28}{v.mean():>8.3f}{np.median(v):>9.3f}{v.max():>8.3f}{100*np.mean(v < 1+1e-9):>9.0f}%")


if __name__ == "__main__":
    main()
