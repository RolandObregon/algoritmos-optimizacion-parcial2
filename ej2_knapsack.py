"""Ejercicio 2: mochila 0/1 voraz: valor/peso vs. menor peso primero."""
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIG_DIR


def greedy(weights, values, cap, criterion):
    idx = range(len(weights))
    if criterion == "valor/peso":
        order = sorted(idx, key=lambda i: values[i] / weights[i], reverse=True)
    elif criterion == "menor peso":
        order = sorted(idx, key=lambda i: (weights[i], -values[i]))
    else:
        raise ValueError(criterion)
    sel, w, v = [], 0, 0
    for i in order:
        if w + weights[i] <= cap:
            sel.append(i)
            w += weights[i]
            v += values[i]
    return sorted(sel), w, v


def compare(weights, values, cap, name, save_png):
    rows = {c: greedy(weights, values, cap, c) for c in ("valor/peso", "menor peso")}
    print(f"\n=== {name} (capacidad={cap}) ===")
    print("Objeto: (peso, valor) ->", {i: (weights[i], values[i]) for i in range(len(weights))})
    print(f"{'Criterio':<12}{'Objetos':<34}{'Cap. usada':<12}{'Valor':<8}")
    for crit, (sel, w, v) in rows.items():
        print(f"{crit:<12}{str(sel):<34}{w}/{cap:<9}{v:<8}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
    crits = list(rows)
    cols = ["tab:green", "tab:orange"]
    ax[0].bar(crits, [rows[c][2] for c in crits], color=cols)
    ax[0].set_title("Valor total")
    ax[1].bar(crits, [rows[c][1] for c in crits], color=cols)
    ax[1].axhline(cap, color="k", ls="--", label=f"capacidad = {cap}")
    ax[1].set_title("Capacidad usada")
    ax[1].legend(loc="lower right")
    for a, k in zip(ax, (2, 1)):
        for x, c in enumerate(crits):
            a.text(x, rows[c][k], f"{rows[c][k]}\nobjetos={rows[c][0]}", ha="center", va="bottom", fontsize=8)
        a.margins(y=0.35)
    fig.suptitle(name)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, save_png), dpi=150)
    plt.close(fig)
    return rows


if __name__ == "__main__":
    rnd = random.Random(42)
    n, cap = 12, 40
    W = [rnd.randint(1, 20) for _ in range(n)]
    V = [rnd.randint(5, 60) for _ in range(n)]
    compare(W, V, cap, "Instancia aleatoria (12 objetos)", "ej2_aleatoria.png")

    # Contraejemplo: menor peso llena la mochila con objetos casi inútiles
    compare([1, 2, 10], [1, 1, 100], 10, "Contraejemplo: menor peso pierde", "ej2_contraejemplo.png")
