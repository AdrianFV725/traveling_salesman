# Traveling Salesman

## Descripción

Implementación sencilla del problema del Viajero (TSP) usando:

- **Heurística de vecino más cercano** para construir una ruta inicial.
- **Mejora 2-opt** para optimizar la ruta manteniendo fijos los extremos (inicio y fin).

El programa lee un archivo de coordenadas 2D, construye una ruta que inicia en el primer ID y termina en el último ID, calcula la distancia total y muestra la secuencia de IDs visitados.

## Estructura del proyecto

- `main.py`: lógica principal, lectura de datos, heurística, optimización y salida.
- `pruebaProyecto.txt`: archivo de datos utilizado por defecto en el código (`DATA_FILE`).
- `datos.txt`: archivo de datos alternativo con el mismo formato (no se usa por defecto).
- `README.md`: este documento.

## Formato del archivo de entrada

Cada línea válida contiene: `ID X Y`

Ejemplo:

```text
1    15      15
2    71.95   60.9
...
40   85      15

OJO:  comentarios o restricciones pueden aparecer a partir de esta línea
```

Reglas de lectura implementadas:

- Líneas vacías se ignoran.
- La lectura se detiene cuando una línea empieza con `OJO`.
- Líneas con menos de 3 columnas se ignoran.
- `ID` debe ser entero; `X` e `Y` deben ser números reales.

## Cómo ejecutar

Requisitos: Python 3.8+

```bash
python3 main.py
```

Salida típica:

```text
Archivo: pruebaProyecto.txt
Ruta (IDs): [1, 7, 14, ..., 40]
Distancia total: 3xx.xx
```

Para usar otro archivo de datos, modifica la constante `DATA_FILE` en `main.py` (por ejemplo, a `"datos.txt"`).

## Detalle del código y funciones (main.py)

- `DATA_FILE = "pruebaProyecto.txt"`

  - Archivo que se leerá por defecto. Cambia este valor para usar otro dataset.

- `leer_puntos(nombre_archivo)`

  - Lee el archivo y devuelve una lista de tuplas `(id, x, y)`.
  - Comportamiento clave:
    - Se detiene al encontrar una línea que empieza con `OJO`.
    - Valida tipos; líneas mal formateadas se ignoran.

- `distancia(a, b)`

  - Calcula distancia euclidiana entre dos puntos 2D usando `math.hypot`.
  - Importante: `a` y `b` son pares `(x, y)` (no incluyen el `id`).

- `vecino_mas_cercano(coords)`

  - Construye una ruta con la heurística de vecino más cercano manteniendo fijos los extremos.
  - Detalles:
    - Supone que `coords` está alineado con los `ids` ya ordenados por `id`.
    - Fija `inicio = 0` y `fin = n - 1`.
    - Solo elige siguientes nodos entre los índices `1..n-2` (interiores), marcando los visitados.
    - Devuelve la ruta como índices sobre `coords`.

- `dos_opt_simple(coords, ruta)`

  - Aplica una mejora 2-opt simple manteniendo fijos los extremos de la ruta.
  - Compara el costo de los segmentos `a-b` y `c-d` antes y después de invertir el subcamino `ruta[i:j+1]`.
  - Itera hasta que no hay mejoras.

- `longitud(coords, ruta)`

  - Suma las distancias consecutivas de la ruta y devuelve la distancia total.

- `main()`
  - Flujo:
    1. Lee puntos desde `DATA_FILE`.
    2. Ordena por `id` para alinear `ids` y `coords` y fijar extremos.
    3. Genera ruta con `vecino_mas_cercano` y optimiza con `dos_opt_simple`.
    4. Calcula distancia con `longitud` y muestra tanto la ruta en IDs como la distancia total.

## Líneas clave explicadas (main.py)

- Fijar archivo por defecto:

  - `DATA_FILE = "pruebaProyecto.txt"` — punto único para cambiar el dataset.

- Parada en marca `OJO` durante lectura:

  - `if linea.startswith("OJO"): break` — permite incluir notas o restricciones al final del archivo sin afectar la lectura.

- Distancia euclidiana robusta:

  - `return math.hypot(a[0] - b[0], a[1] - b[1])` — evita errores de precisión al calcular √((dx)^2 + (dy)^2).

- Vecino más cercano sin tocar extremos:

  - `for i in range(1, n - 1):` — el bucle solo considera nodos interiores para mantener fijo inicio y fin.
  - `restantes = n - 2` — cuenta únicamente los nodos interiores que faltan por visitar.

- Mejora 2-opt con inversión de subruta:

  - `antes = d(a,b) + d(c,d)` y `despues = d(a,c) + d(b,d)` — criterio de mejora.
  - `if despues + 1e-12 < antes:` — el `1e-12` evita oscilaciones por empates numéricos.
  - `ruta[i:j + 1] = reversed(ruta[i:j + 1])` — inversión in-place del subcamino para aplicar el movimiento 2-opt.

- Mapeo de índices a IDs originales:
  - `ruta_ids = [ids[i] for i in ruta]` — la ruta se calcula sobre índices de `coords`; aquí se transforma a IDs para imprimir.

## Complejidad y limitaciones

- La heurística de vecino más cercano es rápida pero no garantiza optimalidad global.
- 2-opt puede atascarse en óptimos locales; resultados dependen del punto de partida y orden.
- Los extremos (primer y último ID) se mantienen fijos por diseño.
- Para menos de 4 puntos, 2-opt no realiza cambios (no hay subrutas internas que invertir).

## Personalización

- Cambiar dataset: editar `DATA_FILE` en `main.py`.
- Permitir extremos libres: adaptar `vecino_mas_cercano` y los rangos en `dos_opt_simple` para incluir `0` y `n-1` en la selección e inversiones.
- Métrica distinta: sustituir `distancia` por otra métrica (p. ej., Manhattan) si el dominio lo requiere.

## Interfaz Gráfica Interactiva (main_graficado.py)

Además de la versión por línea de comandos (`main.py`), el proyecto incluye **`main_graficado.py`**, una interfaz interactiva con visualización completa que permite:

### Características principales:

1. **Generación dinámica de datos**

   - Ingresa el número de puntos deseado (3-500+ puntos)
   - Genera coordenadas aleatorias automáticamente
   - No requiere archivos de entrada predefinidos

2. **Visualización elegante**

   - Gráfica en tiempo real de la ruta optimizada
   - Código de colores claro:
     - Puntos azules: ciudades
     - Línea roja: ruta calculada
     - Círculo verde: punto de inicio
     - Cuadrado rojo: punto de fin
   - Grid sutil y diseño minimalista

3. **Animación de optimización**

   - Visualiza paso a paso cómo el algoritmo 2-opt mejora la ruta
   - Barra de progreso animada
   - Control de velocidad ajustable (50-500 ms por iteración)
   - Muestra iteración actual y distancia en cada frame

4. **Panel de estadísticas**

   - Distancia inicial vs. final
   - Porcentaje de mejora
   - Número total de iteraciones
   - Actualización en tiempo real

5. **Controles interactivos**
   - Campo de texto para número de puntos
   - Slider para ajustar velocidad de animación
   - Botón "Generar": crea y resuelve el problema
   - Botón "Animar": reproduce la optimización paso a paso

### Cómo ejecutar la interfaz gráfica:

Requisitos adicionales:

```bash
pip install matplotlib
```

Ejecución:

```bash
python3 main_graficado.py
```

### Uso típico:

1. Ingresa un número de puntos (ej: 40, 100)
2. Presiona "Generar" para crear datos aleatorios y calcular la ruta óptima
3. Observa la gráfica con la ruta optimizada y las estadísticas
4. Ajusta la velocidad con el slider si deseas
5. Presiona "Animar" para ver la optimización en tiempo real

La ventana de animación muestra:

- Título: "Problema del Viajero (TSP) - Optimización en Tiempo Real"
- Información de iteración actual y distancia
- Gráfica actualizada en cada paso
- Barra de progreso visual en la parte inferior

### Casos de uso recomendados:

- **Educativo**: Ideal para entender visualmente cómo funciona el algoritmo 2-opt
- **Demostraciones**: Presenta el problema TSP de manera atractiva
- **Experimentación**: Prueba rápidamente con diferentes cantidades de puntos
- **Comparación**: Observa cómo varía la mejora según el número de ciudades

### Diferencias con main.py:

| Característica | main.py           | main_graficado.py              |
| -------------- | ----------------- | ------------------------------ |
| Interfaz       | Línea de comandos | Gráfica interactiva            |
| Entrada        | Archivo de texto  | Generación aleatoria o archivo |
| Visualización  | Solo texto        | Gráfica animada                |
| Animación      | No                | Sí, paso a paso                |
| Estadísticas   | Básicas           | Completas con panel visual     |
| Controles      | Editar código     | Widgets interactivos           |

Ambos archivos usan los mismos algoritmos (vecino más cercano + 2-opt), solo difieren en la presentación y modo de uso.

## Licencia

Uso académico/educativo.
