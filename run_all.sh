#!/bin/sh
cd "$(dirname "$0")/src" || exit 1
for e in ej1_speedup ej2_knapsack ej3_2opt ej4_sa ej5_mst; do
  echo "===== $e ====="; python3 $e.py
done
