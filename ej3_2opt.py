"""Ejercicio 3: 2-opt desde solución aleatoria vs. Vecino Más Cercano."""
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon

from common import (FIG_DIR, RES_DIR, dist_matrix, nearest_neighbor,
                    random_instance, tour_cost, two_opt)


def main(n=50, n_inst=30, seed=7):
    rng = np.random.default_rng(seed)
    rnd = random.Random(seed)
    imp_r, imp_n, c_r, c_n, c_nn0 = [], [], [], [], []
    for _ in range(n_inst):
        D = dist_matrix(random_instance(n, rng)).tolist()
        t = list(range(n))
        rnd.shuffle(t)
        _, cost, imp = two_opt(t, D)
        imp_r.append(imp); c_r.append(cost)
        nn = nearest_neighbor(D, rnd.randrange(n))
        c_nn0.append(tour_cost(nn, D))
        _, cost, imp = two_opt(nn, D)
        imp_n.append(imp); c_n.append(cost)
    with open(os.path.join(RES_DIR, "ej3_2opt.csv"), "w") as f:
        f.write("instancia,mejoras_aleatorio,mejoras_NN,costo_aleatorio,costo_NN,costo_NN_inicial\n")
        for i in range(n_inst):
            f.write(f"{i},{imp_r[i]},{imp_n[i]},{c_r[i]:.2f},{c_n[i]:.2f},{c_nn0[i]:.2f}\n")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
    labels = ["Inicio aleatorio", "Inicio NN"]
    ax[0].boxplot([imp_r, imp_n], tick_labels=labels)
    ax[0].set_title("Nº de mejoras 2-opt hasta óptimo local")
    ax[0].set_ylabel("mejoras")
    ax[1].boxplot([c_r, c_n], tick_labels=labels)
    ax[1].set_title("Costo del óptimo local alcanzado")
    ax[1].set_ylabel("longitud del tour")
    for a in ax:
        a.grid(alpha=0.3)
    fig.suptitle(f"2-opt sobre {n_inst} instancias de {n} ciudades")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "ej3_2opt.png"), dpi=150)

    print(f"Mejoras  aleatorio: mediana={np.median(imp_r):.1f} media={np.mean(imp_r):.1f}")
    print(f"Mejoras  NN       : mediana={np.median(imp_n):.1f} media={np.mean(imp_n):.1f}")
    print(f"Costo    aleatorio: media={np.mean(c_r):.1f}")
    print(f"Costo    NN       : media={np.mean(c_n):.1f}  (NN sin 2-opt: {np.mean(c_nn0):.1f})")
    print(f"NN necesita menos mejoras en {sum(a < b for a, b in zip(imp_n, imp_r))}/{n_inst} instancias")
    print("Wilcoxon mejoras:", wilcoxon(imp_r, imp_n))
    print("Wilcoxon costo  :", wilcoxon(c_r, c_n))


if __name__ == "__main__":
    main()
