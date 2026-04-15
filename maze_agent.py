"""
Agente de Búsqueda en Laberinto
================================
Implementa tres algoritmos de búsqueda:
  - BFS  (Búsqueda en Anchura)
  - DFS  (Búsqueda en Profundidad)
  - A*   (A-estrella, búsqueda heurística)

El laberinto se representa como una cuadrícula 2D:
  0 = celda libre
  1 = pared
  S = inicio
  E = salida (end)
"""

import heapq
import time
from collections import deque


# ─────────────────────────────────────────────
#  Laberintos de ejemplo
# ─────────────────────────────────────────────

LABERINTOS = {
    # 7×7 — Dos rutas reales separadas por paredes.
    # Ruta corta (13 pasos): atraviesa el centro del laberinto.
    # Ruta larga (21 pasos): rodea por el borde exterior.
    # DFS toma la larga porque su pila explora primero hacia la derecha.
    # BFS y A* garantizan encontrar la corta.
    "simple": [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
    ],

    # 10×10 — Laberinto con múltiples corredores y bifurcaciones.
    # Ruta corta (19 pasos): corredor central.
    # Ruta larga (33 pasos): DFS la toma al expandir primero hacia la derecha.
    # A* necesita solo 21 nodos explorados vs 31 de BFS — heurística en acción.
    "mediano": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 0],
    ],

    # 12×12 — Laberinto complejo con paredes, cul-de-sacs y dos rutas.
    # BFS explora 74 nodos (entra en los cul-de-sacs del norte).
    # A* solo explora 27 nodos — la heurística lo dirige directo al sur-este.
    # DFS toma 51 pasos (más del doble que el óptimo de 23).
    # Esta es la demostración más clara de la ventaja de A*.
    "difícil": [
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    ],
}

INICIO_SIMPLE  = (0, 0)
INICIO_MEDIANO = (0, 0)
INICIO_DIFÍCIL = (0, 0)

FIN_SIMPLE  = (6, 6)
FIN_MEDIANO = (9, 9)
FIN_DIFÍCIL = (11, 11)

INICIOS = {
    "simple":  INICIO_SIMPLE,
    "mediano": INICIO_MEDIANO,
    "difícil": INICIO_DIFÍCIL,
}

FINES = {
    "simple":  FIN_SIMPLE,
    "mediano": FIN_MEDIANO,
    "difícil": FIN_DIFÍCIL,
}


# ─────────────────────────────────────────────
#  Utilidades comunes
# ─────────────────────────────────────────────

def vecinos(nodo, laberinto):
    """Devuelve las celdas adyacentes (arriba, abajo, izq, der) que no son paredes."""
    filas = len(laberinto)
    cols  = len(laberinto[0])
    f, c  = nodo
    candidatos = [(f-1, c), (f+1, c), (f, c-1), (f, c+1)]
    return [
        (nf, nc)
        for nf, nc in candidatos
        if 0 <= nf < filas and 0 <= nc < cols and laberinto[nf][nc] == 0
    ]


def reconstruir_camino(padres, fin):
    """Recorre el diccionario de padres hacia atrás para obtener el camino."""
    camino = []
    nodo = fin
    while nodo is not None:
        camino.append(nodo)
        nodo = padres[nodo]
    camino.reverse()
    return camino


def heuristica(a, b):
    """Distancia Manhattan — heurística admisible para A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ─────────────────────────────────────────────
#  Algoritmos de búsqueda
# ─────────────────────────────────────────────

def bfs(laberinto, inicio, fin):
    """
    BFS — Búsqueda en Anchura (Breadth-First Search)
    Garantiza el camino más corto en grafos sin pesos.
    Usa una COLA (FIFO).
    """
    frontera   = deque([inicio])          # Cola FIFO
    padres     = {inicio: None}           # nodo → padre
    explorados = []                       # orden de exploración (para visualizar)

    while frontera:
        nodo = frontera.popleft()         # Saca el más antiguo
        explorados.append(nodo)

        if nodo == fin:
            return reconstruir_camino(padres, fin), explorados

        for vecino in vecinos(nodo, laberinto):
            if vecino not in padres:
                padres[vecino] = nodo
                frontera.append(vecino)

    return None, explorados              # Sin solución


def dfs(laberinto, inicio, fin):
    """
    DFS — Búsqueda en Profundidad (Depth-First Search)
    No garantiza el camino más corto.
    Usa una PILA (LIFO).
    """
    pila       = [inicio]                # Pila LIFO
    padres     = {inicio: None}
    explorados = []

    while pila:
        nodo = pila.pop()                # Saca el más reciente
        explorados.append(nodo)

        if nodo == fin:
            return reconstruir_camino(padres, fin), explorados

        for vecino in vecinos(nodo, laberinto):
            if vecino not in padres:
                padres[vecino] = nodo
                pila.append(vecino)

    return None, explorados


def a_estrella(laberinto, inicio, fin):
    """
    A* — Búsqueda informada con heurística.
    f(n) = g(n) + h(n)
      g = costo real desde el inicio
      h = estimación (distancia Manhattan) hasta el fin
    Usa una COLA DE PRIORIDAD (min-heap).
    """
    # heap: (f, g, nodo)
    heap       = [(heuristica(inicio, fin), 0, inicio)]
    padres     = {inicio: None}
    costo_g    = {inicio: 0}
    explorados = []

    while heap:
        f, g, nodo = heapq.heappop(heap)
        explorados.append(nodo)

        if nodo == fin:
            return reconstruir_camino(padres, fin), explorados

        for vecino in vecinos(nodo, laberinto):
            nuevo_g = g + 1
            if vecino not in costo_g or nuevo_g < costo_g[vecino]:
                costo_g[vecino] = nuevo_g
                f_nuevo = nuevo_g + heuristica(vecino, fin)
                heapq.heappush(heap, (f_nuevo, nuevo_g, vecino))
                padres[vecino] = nodo

    return None, explorados


# ─────────────────────────────────────────────
#  Visualización en consola
# ─────────────────────────────────────────────

ICONOS = {
    "pared":      "█",
    "libre":      " ",
    "explorado":  "·",
    "camino":     "●",
    "inicio":     "S",
    "fin":        "E",
}


def imprimir_laberinto(laberinto, inicio, fin, explorados=None, camino=None):
    """Imprime el laberinto con colores ANSI."""
    filas = len(laberinto)
    cols  = len(laberinto[0])

    explorado_set = set(explorados) if explorados else set()
    camino_set    = set(camino)     if camino    else set()

    # Borde superior
    print("  " + "─" * (cols * 2 + 1))

    for f in range(filas):
        fila_str = "│ "
        for c in range(cols):
            celda = (f, c)
            if celda == inicio:
                fila_str += "\033[92mS \033[0m"    # Verde
            elif celda == fin:
                fila_str += "\033[91mE \033[0m"    # Rojo
            elif celda in camino_set:
                fila_str += "\033[93m● \033[0m"    # Amarillo
            elif celda in explorado_set:
                fila_str += "\033[94m· \033[0m"    # Azul
            elif laberinto[f][c] == 1:
                fila_str += "\033[90m█ \033[0m"    # Gris oscuro
            else:
                fila_str += "  "
        fila_str += "│"
        print(fila_str)

    print("  " + "─" * (cols * 2 + 1))


def imprimir_leyenda():
    print("\n  Leyenda:")
    print("  \033[92mS\033[0m  Inicio   "
          "\033[91mE\033[0m  Salida   "
          "\033[93m●\033[0m  Camino   "
          "\033[94m·\033[0m  Explorado   "
          "\033[90m█\033[0m  Pared")


# ─────────────────────────────────────────────
#  Ejecución del agente
# ─────────────────────────────────────────────

def ejecutar_agente(nombre_laberinto, algoritmo_fn, nombre_algoritmo):
    laberinto = LABERINTOS[nombre_laberinto]
    inicio    = INICIOS[nombre_laberinto]
    fin       = FINES[nombre_laberinto]

    print(f"\n{'='*50}")
    print(f"  Algoritmo : {nombre_algoritmo}")
    print(f"  Laberinto : {nombre_laberinto}")
    print(f"  Inicio    : {inicio}  →  Fin: {fin}")
    print(f"{'='*50}")

    t0 = time.perf_counter()
    camino, explorados = algoritmo_fn(laberinto, inicio, fin)
    t1 = time.perf_counter()

    imprimir_laberinto(laberinto, inicio, fin, explorados, camino)
    imprimir_leyenda()

    print(f"\n  Nodos explorados : {len(explorados)}")
    if camino:
        print(f"  Longitud camino  : {len(camino)} pasos")
        print(f"  Tiempo           : {(t1-t0)*1000:.3f} ms")
        print(f"  Ruta             : {' → '.join(str(p) for p in camino)}")
    else:
        print("  ❌ No se encontró solución.")

    return camino, explorados


# ─────────────────────────────────────────────
#  Menú interactivo
# ─────────────────────────────────────────────

ALGORITMOS = {
    "1": (bfs,         "BFS — Búsqueda en Anchura"),
    "2": (dfs,         "DFS — Búsqueda en Profundidad"),
    "3": (a_estrella,  "A* — Búsqueda Heurística"),
}

def menu():
    print("\n" + "="*50)
    print("   AGENTE DE BÚSQUEDA EN LABERINTO")
    print("="*50)

    # Elegir laberinto
    print("\nElige el laberinto:")
    descripciones = {
        "simple":  "( 7× 7) — 2 rutas: corta vs larga",
        "mediano": "(10×10) — corredores con bifurcaciones",
        "difícil": "(12×12) — cul-de-sacs + 2 rutas",
    }
    for i, nombre in enumerate(LABERINTOS, 1):
        print(f"  {i}. {nombre.capitalize():8}  {descripciones[nombre]}")
    opcion_lab = input("\nOpción (1-3): ").strip()
    nombres    = list(LABERINTOS.keys())
    if opcion_lab not in ["1","2","3"]:
        print("Opción inválida."); return
    nombre_lab = nombres[int(opcion_lab) - 1]

    # Elegir algoritmo
    print("\nElige el algoritmo de búsqueda:")
    for k, (_, nombre) in ALGORITMOS.items():
        print(f"  {k}. {nombre}")
    print("  4. Comparar los tres algoritmos")
    opcion_alg = input("\nOpción (1-4): ").strip()

    if opcion_alg in ALGORITMOS:
        fn, nombre = ALGORITMOS[opcion_alg]
        ejecutar_agente(nombre_lab, fn, nombre)

    elif opcion_alg == "4":
        print(f"\n{'─'*50}")
        print("  COMPARACIÓN DE LOS TRES ALGORITMOS")
        print(f"{'─'*50}")
        resultados = []
        for k in ["1","2","3"]:
            fn, nombre = ALGORITMOS[k]
            camino, explorados = ejecutar_agente(nombre_lab, fn, nombre)
            resultados.append((nombre, len(explorados), len(camino) if camino else 0))

        print(f"\n{'─'*50}")
        print(f"  {'Algoritmo':<30} {'Explorados':>10} {'Pasos':>6}")
        print(f"{'─'*50}")
        for nombre, exp, pasos in resultados:
            print(f"  {nombre:<30} {exp:>10} {pasos:>6}")
    else:
        print("Opción inválida.")


if __name__ == "__main__":
    menu()