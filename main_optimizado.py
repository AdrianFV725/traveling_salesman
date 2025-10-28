"""
Problema del Viajero (TSP)
Adrian Flores Villatoro
Cristian Moreno Villarreal
"""

import math
import random
from copy import deepcopy

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


# Simulated Annealing mejorado con movimientos más efectivos
def simulated_annealing(coords, ruta_inicial, temp_inicial=5000, temp_final=0.1, alpha=0.98, iteraciones_por_temp=200):
    """
    Aplica Simulated Annealing para optimizar la ruta después de 2-opt.
    Mantiene fijos los extremos (inicio y fin).
    Usa múltiples tipos de movimientos para mejor exploración.
    """
    ruta_actual = deepcopy(ruta_inicial)
    mejor_ruta = deepcopy(ruta_inicial)
    dist_actual = longitud(coords, ruta_actual)
    mejor_dist = dist_actual
    
    temperatura = temp_inicial
    n = len(ruta_actual)
    
    # Solo podemos modificar los nodos interiores (no los extremos)
    nodos_interiores = list(range(1, n - 1))
    
    mejoras = 0
    
    while temperatura > temp_final:
        for _ in range(iteraciones_por_temp):
            # Crear nueva ruta con diferentes tipos de movimientos
            nueva_ruta = deepcopy(ruta_actual)
            tipo_movimiento = random.random()
            
            if tipo_movimiento < 0.5:  # 50% - Intercambio de dos nodos
                if len(nodos_interiores) >= 2:
                    i, j = random.sample(nodos_interiores, 2)
                    nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]
            
            elif tipo_movimiento < 0.85:  # 35% - Inversión de segmento (mini 2-opt)
                if len(nodos_interiores) >= 2:
                    i, j = sorted(random.sample(nodos_interiores, 2))
                    nueva_ruta[i:j+1] = reversed(nueva_ruta[i:j+1])
            
            else:  # 15% - Inserción (mover un nodo a otra posición)
                if len(nodos_interiores) >= 2:
                    i = random.choice(nodos_interiores)
                    j = random.choice(nodos_interiores)
                    if i != j:
                        nodo = nueva_ruta.pop(i)
                        nueva_ruta.insert(j, nodo)
            
            # Calcular nueva distancia
            nueva_dist = longitud(coords, nueva_ruta)
            delta = nueva_dist - dist_actual
            
            # Decidir si aceptar la nueva ruta
            if delta < 0:  # Mejora
                ruta_actual = nueva_ruta
                dist_actual = nueva_dist
                mejoras += 1
                
                if dist_actual < mejor_dist:
                    mejor_ruta = deepcopy(ruta_actual)
                    mejor_dist = dist_actual
            else:  # Peor solución
                # Aceptar con probabilidad exp(-delta/T)
                probabilidad = math.exp(-delta / temperatura)
                if random.random() < probabilidad:
                    ruta_actual = nueva_ruta
                    dist_actual = nueva_dist
        
        # Enfriar temperatura
        temperatura *= alpha
    
    print(f"   (Annealing realizó {mejoras} mejoras)")
    return mejor_ruta


# 2-opt mejorado con más iteraciones
def dos_opt_mejorado(coords, ruta):
    """
    Versión mejorada de 2-opt que itera múltiples veces desde diferentes puntos
    para encontrar mejores soluciones
    """
    mejor_ruta = deepcopy(ruta)
    mejor_dist = longitud(coords, mejor_ruta)
    
    # Aplicar 2-opt múltiples veces
    for intento in range(3):  # 3 pasadas completas
        ruta_temp = dos_opt_simple(coords, mejor_ruta)
        dist_temp = longitud(coords, ruta_temp)
        if dist_temp < mejor_dist:
            mejor_ruta = ruta_temp
            mejor_dist = dist_temp
    
    return mejor_ruta

# Función principal
def main():
    puntos = leer_puntos(DATA_FILE)
    if not puntos:
        print("No hay puntos en el archivo de datos.")
        return
    puntos.sort()
    ids = [p[0] for p in puntos]
    coords = [(p[1], p[2]) for p in puntos]
    
    # Paso 1: Genera ruta inicial con vecino más cercano
    print("=== Optimización del Viajero (TSP) ===")
    print(f"Archivo: {DATA_FILE}")
    print(f"Puntos: {len(coords)}\n")
    
    ruta = vecino_mas_cercano(coords)
    dist_inicial = longitud(coords, ruta)
    print(f"1. Vecino más cercano - Distancia: {dist_inicial:.2f}")
    
    # Paso 2: Optimiza con 2-opt mejorado (múltiples pasadas)
    ruta = dos_opt_mejorado(coords, ruta)
    dist_2opt = longitud(coords, ruta)
    mejora_2opt = ((dist_inicial - dist_2opt) / dist_inicial) * 100
    print(f"2. Después de 2-opt    - Distancia: {dist_2opt:.2f} (mejora: {mejora_2opt:.2f}%)")
    
    # Paso 3: Ejecutar múltiples intentos de Simulated Annealing para encontrar la mejor solución
    print(f"3. Ejecutando Annealing múltiples veces para encontrar mejor solución...")
    mejor_ruta_global = ruta
    mejor_dist_global = dist_2opt
    
    num_intentos = 35  # Ejecutar 35 veces y quedarse con la mejor
    for intento in range(1, num_intentos + 1):
        print(f"   Intento {intento}/{num_intentos}...", end=" ")
        ruta_temp = simulated_annealing(coords, ruta, temp_inicial=10000, temp_final=0.01, alpha=0.97, iteraciones_por_temp=300)
        dist_temp = longitud(coords, ruta_temp)
        print(f"Distancia: {dist_temp:.2f}")
        
        if dist_temp < mejor_dist_global:
            mejor_ruta_global = ruta_temp
            mejor_dist_global = dist_temp
            print(f"      ¡Nueva mejor distancia encontrada!")  # Indicador de mejora
    
    dist_final = mejor_dist_global
    ruta = mejor_ruta_global
    
    mejora_sa = ((dist_2opt - dist_final) / dist_2opt) * 100
    mejora_total = ((dist_inicial - dist_final) / dist_inicial) * 100
    print(f"\n   Mejor resultado de Annealing - Distancia: {dist_final:.2f} (mejora adicional: {mejora_sa:.2f}%)")
    
    print(f"\nMejora total: {mejora_total:.2f}% (de {dist_inicial:.2f} a {dist_final:.2f})")
    
    # Imprime la ruta final
    ruta_ids = [ids[i] for i in ruta]
    print(f"\nRuta final (IDs): {ruta_ids}")

# Main
if __name__ == "__main__":
    main()
