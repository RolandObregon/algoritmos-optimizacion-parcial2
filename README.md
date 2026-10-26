# Algoritmos y Optimización – Ejercicios (2º parcial)

**Autor:** Rolando Obregon Guzman
**Repositorio:** https://github.com/RolandObregon/algoritmos-optimizacion-parcial2
**Video demo (≤ 8 min):** https://youtu.be/OMASpyxsuIw

## Estructura
```
proyecto/
├── README.md            <- este reporte
├── requirements.txt
├── run_all.sh           <- corre los 5 ejercicios
├── src/
│   ├── common.py        <- TSP: NN, 2-opt, MST, Held-Karp, Recocido Simulado
│   ├── ej1_speedup.py   ├── ej2_knapsack.py   ├── ej3_2opt.py
│   ├── ej4_sa.py        └── ej5_mst.py
├── figures/             <- gráficas (PNG)
└── results/             <- tablas (CSV)
```
Ejecutar: `pip install -r requirements.txt && ./run_all.sh`
(Si tu profesor pidió otra estructura de carpetas, solo mueve los archivos y ajusta los imports/`common.py`.)

---
## Ejercicio 1 – Speedup paralelo
Figura: `figures/ej1_speedup.png`. Datos: `results/ej1_speedup.csv`.

<!--EJ1_START-->
Mi equipo tiene **16 procesadores lógicos** (`os.cpu_count()`). Resultados medidos (mediana de varias corridas):

| Procesos | Tiempo (s) | Speedup | Ideal | Eficiencia |
|---|---|---|---|---|
| 1 | 0.861 | 1.00 | 1 | 100 % |
| 2 | 0.764 | 1.13 | 2 | 56 % |
| 4 | 0.734 | 1.17 | 4 | 29 % |
| 8 | 0.689 | 1.25 | 8 | 16 % |
<!--EJ1_END-->

**Análisis:** el speedup queda por debajo de la recta ideal S = p porque:
1. **Ley de Amdahl:** S(p) = 1 / ((1−f) + f/p); la parte serial (crear el Pool, repartir tareas, sumar resultados) no se acelera y limita el máximo S(∞) = 1/(1−f).
2. **Sobrecosto de procesos y comunicación:** crear procesos, serializar (pickle) argumentos y resultados y esperar a que terminen.
3. **Sincronización:** `pool.map` espera al proceso más lento (barrera), así que cualquier desbalance o proceso retrasado frena al resto.
4. **Recursos de hardware:** mi equipo tiene 16 procesadores lógicos, así que con 1, 2, 4 y 8 procesos hay hilos disponibles de sobra. Aun así, los procesadores lógicos suelen ser hilos de hyper-threading que comparten los recursos de un núcleo físico, y todos los procesos compiten por memoria y caché, además de que el sistema operativo y otros programas usan CPU al mismo tiempo. Por eso el speedup no es perfecto.

## Ejercicio 2 – Mochila voraz
Figuras: `figures/ej2_aleatoria.png`, `figures/ej2_contraejemplo.png`.
| Instancia | Criterio | Objetos | Capacidad usada | Valor |
|---|---|---|---|---|
| Aleatoria (12 obj., cap. 40) | valor/peso | 0,1,4,5,8,10,11 | 37/40 | **208** |
| | menor peso | 0,1,3,4,5,6,8,11 | 35/40 | 187 |
| Contraejemplo (cap. 10) | valor/peso | 2 | 10/10 | **100** |
| | menor peso | 0,1 | 3/10 | 2 |

**Contraejemplo:** objetos (peso, valor) = A(1,1), B(2,1), C(10,100), capacidad 10. Menor peso toma A y B (valor 2) y C ya no cabe; valor/peso toma C (valor 100). El criterio de peso ignora el valor, por eso puede ser arbitrariamente malo.

## Ejercicio 3 – 2-opt: aleatorio vs. Vecino Más Cercano
Figura: `figures/ej3_2opt.png` (30 instancias, 50 ciudades). Resultados de mi corrida:
- Mejoras: aleatorio mediana 117 vs. NN mediana 16 (NN necesitó menos en **30/30** instancias; Wilcoxon p ≈ 1.7e-6).
- Costo del óptimo local: aleatorio ≈ 610.5 vs. NN ≈ 600.3 (diferencia pequeña, p ≈ 0.04). NN solo, sin 2-opt: ≈ 702.7.

**Conclusión:** sí, NN converge con muchas menos mejoras porque ya parte de un tour razonable (sin cruces grandes), mientras que el aleatorio debe "deshacer" muchísimo desorden. Además, la calidad final es igual o ligeramente mejor.

## Ejercicio 4 – Recocido Simulado
Figuras: `ej4_convergencia.png`, `ej4_esquemas.png`, `ej4_tiempo_vs_calidad.png`. Datos: `results/ej4_sa.csv`.
Resultados (n=40, 100k iteraciones, 8 semillas): exponencial ≈ 514.5 ± 3.3, lineal ≈ 516.6 ± 5.3, logarítmico ≈ 540.6 ± 16.9.
**Análisis:** el tiempo es prácticamente el mismo en los tres esquemas (mismo nº de iteraciones y mismo costo por iteración O(n)); lo que cambia es la **calidad por iteración**. El exponencial baja T rápido al inicio y dedica mucho tiempo a temperaturas bajas útiles (explotación) → mejor y más estable. El lineal gasta gran parte del presupuesto a T alta (casi caminata aleatoria) y necesita más iteraciones para igualar. El logarítmico enfría tan lento que casi todo el tiempo está caliente y termina "congelándose" tarde → peor resultado con este presupuesto. Con más tiempo todos mejoran (curva tiempo vs. calidad).

## Ejercicio 5 – Razón de aproximación MST
Figuras: `ej5_razon_mst.png`, `ej5_comparativa.png`. Datos: `results/ej5_mst.csv` (óptimo exacto por Held-Karp).
| Método | Razón media | Máxima | % instancias óptimas |
|---|---|---|---|
| MST puro | 1.114 | 1.334 | 13 % |
| MST + 2-opt | 1.005 | 1.091 | 84 % |
| 2-opt desde aleatorio | 1.010 | 1.194 | 77 % |
| Recocido simulado | 1.000 | 1.000 | 100 % |

**Análisis:** el límite teórico es 2 (recorrido preorden del MST + desigualdad triangular), pero en la práctica la razón máxima fue 1.33 y la media 1.11: la cota es de peor caso y muy pesimista para instancias euclidianas aleatorias. Aplicar 2-opt como post-procesamiento reduce la razón media de 1.114 a 1.005 y supera ligeramente al 2-opt desde inicio aleatorio (1.010) y con menos riesgo en el peor caso (1.09 vs. 1.19), porque MST da un buen punto de partida (igual que NN en el Ej. 3). El recocido simulado fue el mejor en estas instancias pequeñas (9 ciudades), a costa de muchas más evaluaciones.
