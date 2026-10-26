"""Utilidades compartidas: TSP (instancias, NN, 2-opt, MST, Held-Karp, SA)."""
import itertools
import math
import os
import random

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "figures")
RES_DIR = os.path.join(ROOT, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)


# ---------- Instancias y costo ----------
def random_instance(n, rng):
    """n ciudades uniformes en [0,100]^2 (distancia euclidiana => cumple desigualdad triangular)."""
    return rng.random((n, 2)) * 100


def dist_matrix(pts):
    diff = pts[:, None, :] - pts[None, :, :]
    return np.sqrt((diff ** 2).sum(-1))


def tour_cost(tour, D):
    return float(sum(D[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour))))


# ---------- Construcción ----------
def nearest_neighbor(D, start):
    n = len(D)
    visited = [False] * n
    tour = [start]
    visited[start] = True
    for _ in range(n - 1):
        cur = tour[-1]
        nxt = min((j for j in range(n) if not visited[j]), key=lambda j: D[cur][j])
        tour.append(nxt)
        visited[nxt] = True
    return tour


# ---------- 2-opt (primera mejora) ----------
def two_opt(tour, D):
    """Devuelve (tour, costo, n_mejoras). Cada inversión que reduce el costo cuenta como 1 mejora."""
    t = list(tour)
    n = len(t)
    cost = tour_cost(t, D)
    improvements = 0
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = t[i], t[i + 1]
                c, d = t[j], t[(j + 1) % n]
                delta = D[a][c] + D[b][d] - D[a][b] - D[c][d]
                if delta < -1e-10:
                    t[i + 1:j + 1] = reversed(t[i + 1:j + 1])
                    cost += delta
                    improvements += 1
                    improved = True
    return t, cost, improvements


# ---------- MST (2-aproximación) ----------
def mst_tour(D):
    """Prim + recorrido en preorden (atajos) => 2-aproximación para TSP métrico."""
    n = len(D)
    in_tree = [False] * n
    key = [math.inf] * n
    parent = [-1] * n
    key[0] = 0
    children = [[] for _ in range(n)]
    for _ in range(n):
        u = min((v for v in range(n) if not in_tree[v]), key=lambda v: key[v])
        in_tree[u] = True
        if parent[u] != -1:
            children[parent[u]].append(u)
        for v in range(n):
            if not in_tree[v] and D[u][v] < key[v]:
                key[v] = D[u][v]
                parent[v] = u
    order, stack = [], [0]
    while stack:
        u = stack.pop()
        order.append(u)
        stack.extend(reversed(children[u]))
    return order


# ---------- Óptimo exacto (Held-Karp) ----------
def held_karp(D):
    n = len(D)
    dp = {}
    for k in range(1, n):
        dp[(1 << k, k)] = D[0][k]
    for size in range(2, n):
        for subset in itertools.combinations(range(1, n), size):
            bits = sum(1 << k for k in subset)
            for k in subset:
                prev = bits & ~(1 << k)
                dp[(bits, k)] = min(dp[(prev, m)] + D[m][k] for m in subset if m != k)
    full = (1 << n) - 2
    return min(dp[(full, k)] + D[k][0] for k in range(1, n))


# ---------- Recocido simulado con 2-opt ----------
def temperature(schedule, it, iters, T0, Tf):
    frac = it / max(iters - 1, 1)
    if schedule == "lineal":
        return T0 + (Tf - T0) * frac
    if schedule == "exponencial":
        return T0 * (Tf / T0) ** frac
    if schedule == "logaritmico":
        c = (T0 / Tf - 1) / math.log(iters)
        return T0 / (1 + c * math.log(1 + it))
    raise ValueError(schedule)


def simulated_annealing(D, schedule, iters, T0, Tf, seed, log_every=0):
    rnd = random.Random(seed)
    n = len(D)
    t = list(range(n))
    rnd.shuffle(t)
    cost = tour_cost(t, D)
    best = cost
    hist_it, hist_cost, hist_best, hist_T = [], [], [], []
    for it in range(iters):
        T = temperature(schedule, it, iters, T0, Tf)
        i = rnd.randrange(n)
        j = rnd.randrange(n)
        if i > j:
            i, j = j, i
        if j - i >= 1 and not (i == 0 and j == n - 1):
            a, b = t[i - 1], t[i]
            c, d = t[j], t[(j + 1) % n]
            delta = D[a][c] + D[b][d] - D[a][b] - D[c][d]
            if delta < 0 or rnd.random() < math.exp(-delta / T):
                t[i:j + 1] = reversed(t[i:j + 1])
                cost += delta
                if cost < best:
                    best = cost
        if log_every and it % log_every == 0:
            hist_it.append(it)
            hist_cost.append(cost)
            hist_best.append(best)
            hist_T.append(T)
    return t, best, (hist_it, hist_cost, hist_best, hist_T)
