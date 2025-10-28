"""
Problema del Viajero (TSP)
Adrian Flores Villatoro
Cristian Moreno Villarreal
"""

import math

# Nombre del archivo de datos
DATA_FILE = "datos_60.txt"

# Lee los puntos del archivo de datos
def leer_puntos(nombre_archivo):
    puntos = []  # (id, x, y)
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split()
            if len(partes) < 3:
                continue
            try:
                pid = int(partes[0])
                x = float(partes[1])
                y = float(partes[2])
                puntos.append((pid, x, y))
            except ValueError:
                continue
    return puntos


# Calcula la distancia entre dos puntos
def distancia(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# Encuentra la ruta más corta usando el algoritmo de vecino más cercano
def vecino_mas_cercano(coords):
    # Asumimos que los puntos ya están ordenados por ID.
    n = len(coords)
    inicio = 0
    fin = n - 1
    visitado = [False] * n
    ruta = [inicio]
    visitado[inicio] = True
    # Dejamos el último punto (fin) para el final.
    restantes = n - 2  # sin inicio y sin fin
    actual = inicio
    while restantes > 0:
        mejor = None
        mejor_d = float("inf")
        for i in range(1, n - 1):  # no considerar 0 ni n-1 aquí
            if not visitado[i]:
                d = distancia(coords[actual], coords[i])
                if d < mejor_d:
                    mejor_d = d
                    mejor = i
        ruta.append(mejor)
        visitado[mejor] = True
        actual = mejor
        restantes -= 1
    # Al final, agregar el punto fin
    ruta.append(fin)
    return ruta

# Mejora la ruta usando el algoritmo de 2-opt simple
def dos_opt_simple(coords, ruta):
    # Extremos fijos: no tocamos ruta[0] ni ruta[-1]
    n = len(ruta)
    if n <= 3:
        return ruta
    mejoro = True
    while mejoro:
        mejoro = False
        for i in range(1, n - 2):
            a = ruta[i - 1]  # Punto anterior al segmento que evaluaremos
            b = ruta[i]      # Primer punto del segmento a evaluar
            for j in range(i + 1, n - 1):
                c = ruta[j]      # Último punto del segmento a evaluar
                d = ruta[j + 1]  # Punto siguiente al segmento
                antes = distancia(coords[a], coords[b]) + distancia(coords[c], coords[d])
                despues = distancia(coords[a], coords[c]) + distancia(coords[b], coords[d])
                if despues + 1e-12 < antes:
                    ruta[i:j + 1] = reversed(ruta[i:j + 1])
                    mejoro = True
    return ruta


# Calcula la longitud de la ruta
def longitud(coords, ruta):
    total = 0.0
    # Calcula la distancia total de la ruta
    for i in range(len(ruta) - 1):
        total += distancia(coords[ruta[i]], coords[ruta[i + 1]])
    return total

# Función principal
def main():
    puntos = leer_puntos(DATA_FILE)
    if not puntos:
        print("No hay puntos en el archivo de datos.")
        return
    puntos.sort()
    ids = [p[0] for p in puntos]
    coords = [(p[1], p[2]) for p in puntos]
    # Encuentra la ruta más corta usando el algoritmo de vecino más cercano
    ruta = vecino_mas_cercano(coords)
    ruta = dos_opt_simple(coords, ruta)
    # Calcula la distancia total
    dist = longitud(coords, ruta)
    ruta_ids = [ids[i] for i in ruta]
    # Imprime la ruta y la distancia total
    print("Archivo:", DATA_FILE)
    print("Ruta (IDs):", ruta_ids)
    print(f"Distancia total: {dist:.2f}")

# Main
if __name__ == "__main__":
    main()
