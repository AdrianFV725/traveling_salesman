import math

# Nombre del archivo de datos
DATA_FILE = "datos.txt"

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
    """
    Esta función resuelve el problema del viajero usando la estrategia del "vecino más cercano".
    
    Imagina que eres un viajero que debe visitar varias ciudades. Esta función te ayuda a decidir
    en qué orden visitarlas para que el viaje sea lo más corto posible.
    
    Funciona así:
    1. Empiezas en la primera ciudad (punto de inicio)
    2. Miras todas las ciudades que aún no has visitado y eliges la más cercana
    3. Te mueves a esa ciudad y la marcas como visitada
    4. Repites los pasos 2 y 3 hasta visitar todas las ciudades intermedias
    5. Al final, vas a la última ciudad (punto final)
    
    Es como cuando haces recados: empiezas en casa, vas primero a la tienda más cercana,
    luego a la siguiente más cercana, y así sucesivamente, hasta terminar en un lugar específico.
    """
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
    """
    Esta función mejora una ruta existente usando el algoritmo 2-opt.
    
    A diferencia del algoritmo de vecino más cercano que construye una ruta desde cero,
    2-opt toma una ruta ya existente y la optimiza intercambiando segmentos para reducir
    la distancia total.
    
    Usar vecino_mas_cercano cuando:
    - Necesitas generar una ruta inicial desde cero
    - Tienes puntos de inicio y fin fijos
    - Quieres una solución rápida pero no necesariamente óptima
    
    Usar dos_opt_simple cuando:
    - Ya tienes una ruta inicial (como la generada por vecino_mas_cercano)
    - Quieres mejorar esa ruta eliminando cruces y optimizando el recorrido
    - Puedes permitirte un tiempo de cálculo adicional para obtener una mejor solución
    
    Lo ideal es usar ambos: primero vecino_mas_cercano para generar una ruta inicial,
    y luego dos_opt_simple para mejorarla.
    """
    # Extremos fijos: no tocamos ruta[0] ni ruta[-1]
    n = len(ruta)
    if n <= 3:
        return ruta
    mejoro = True
    while mejoro:
        mejoro = False
        for i in range(1, n - 2):
            a = ruta[i - 1]
            b = ruta[i]
            for j in range(i + 1, n - 1):
                c = ruta[j]
                d = ruta[j + 1]
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
    # Ordenar por ID para que el inicio sea el primer ID y el fin el último ID
    puntos.sort(key=lambda t: t[0])#
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
