## ¿Qué es un agente de búsqueda?

Un **agente inteligente** percibe su entorno y actúa para alcanzar un objetivo. En este proyecto, el agente:

- **Percibe:** la cuadrícula del laberinto (qué celdas son libres, cuáles son paredes).
- **Actúa:** se mueve en cuatro direcciones (arriba, abajo, izquierda, derecha).
- **Objetivo:** encontrar el camino desde el punto **S** (inicio) hasta el punto **E** (salida).

- ## Algoritmos implementados

### 1. BFS — Búsqueda en Anchura (Breadth-First Search)

**Estructura de datos:** Cola FIFO (primero en entrar, primero en salir).

**Cómo funciona:**
1. Comienza en el nodo inicial.
2. Explora **todos los vecinos** del nodo actual antes de pasar al siguiente nivel.
3. Se expande capa por capa, como ondas en el agua.

**Garantía:** Siempre encuentra el **camino más corto** (en número de pasos).


---

### 2. DFS — Búsqueda en Profundidad (Depth-First Search)

**Estructura de datos:** Pila LIFO (último en entrar, primero en salir).

**Cómo funciona:**
1. Comienza en el nodo inicial.
2. Sigue **profundizando** por un camino hasta que no puede más.
3. Retrocede (backtrack) y prueba otra rama.

**Garantía:** Encuentra una solución si existe, pero **no necesariamente la más corta**.

---

### 3. A* — Búsqueda Heurística (A-Star)

**Estructura de datos:** Cola de prioridad (min-heap).

**Cómo funciona:**

Cada nodo se evalúa con la función:

```
f(n) = g(n) + h(n)
```

donde:
- `g(n)` = costo real acumulado desde el inicio hasta `n`
- `h(n)` = estimación heurística del costo desde `n` hasta la meta

**Heurística usada:** Distancia Manhattan  
```
h(n) = |fila_n - fila_meta| + |col_n - col_meta|
```

**Garantía:** Encuentra el **camino óptimo** y es más eficiente que BFS porque usa información del objetivo.

