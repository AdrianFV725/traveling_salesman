"""
Problema del Viajero (TSP) - Versión Optimizada con Visualización
Adrian Flores Villatoro
Cristian Moreno Villarreal
"""

import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from copy import deepcopy
import random
from matplotlib.widgets import Button, TextBox, Slider
import numpy as np

# Configuración de estilo matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['figure.facecolor'] = '#ffffff'

# Nombre del archivo de datos
DATA_FILE = "datos_60.txt"

# Lee los puntos del archivo de datos
def leer_puntos(nombre_archivo):
    puntos = []  # (id, x, y)
    try:
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
    except FileNotFoundError:
        return []
    return puntos


# Calcula la distancia entre dos puntos
def distancia(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# Encuentra la ruta más corta usando el algoritmo de vecino más cercano
def vecino_mas_cercano(coords):
    n = len(coords)
    inicio = 0
    fin = n - 1
    visitado = [False] * n
    ruta = [inicio]
    visitado[inicio] = True
    restantes = n - 2
    actual = inicio
    while restantes > 0:
        mejor = None
        mejor_d = float("inf")
        for i in range(1, n - 1):
            if not visitado[i]:
                d = distancia(coords[actual], coords[i])
                if d < mejor_d:
                    mejor_d = d
                    mejor = i
        ruta.append(mejor)
        visitado[mejor] = True
        actual = mejor
        restantes -= 1
    ruta.append(fin)
    return ruta


# Mejora la ruta usando el algoritmo de 2-opt simple
def dos_opt_simple(coords, ruta_inicial, rutas_intermedias=None):
    ruta = deepcopy(ruta_inicial)
    n = len(ruta)
    if n <= 3:
        if rutas_intermedias is not None:
            rutas_intermedias.append(deepcopy(ruta))
        return ruta
    mejoro = True
    iteracion = 0
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
                    iteracion += 1
                    if rutas_intermedias is not None:
                        rutas_intermedias.append(deepcopy(ruta))
        if not mejoro:
            break
    if rutas_intermedias is not None:
        rutas_intermedias.append(deepcopy(ruta))
    return ruta


# 2-opt mejorado con más iteraciones
def dos_opt_mejorado(coords, ruta, rutas_intermedias=None):
    """
    Versión mejorada de 2-opt que itera múltiples veces desde diferentes puntos
    para encontrar mejores soluciones
    """
    mejor_ruta = deepcopy(ruta)
    mejor_dist = longitud(coords, mejor_ruta)
    
    # Aplicar 2-opt múltiples veces
    for intento in range(3):  # 3 pasadas completas
        ruta_temp = dos_opt_simple(coords, mejor_ruta, rutas_intermedias)
        dist_temp = longitud(coords, ruta_temp)
        if dist_temp < mejor_dist:
            mejor_ruta = ruta_temp
            mejor_dist = dist_temp
    
    return mejor_ruta


# Simulated Annealing mejorado con movimientos más efectivos
def simulated_annealing(coords, ruta_inicial, temp_inicial=5000, temp_final=0.1, alpha=0.98, 
                       iteraciones_por_temp=200, rutas_intermedias=None, capturar_cada=10):
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
    iteracion_global = 0
    
    while temperatura > temp_final:
        for _ in range(iteraciones_por_temp):
            iteracion_global += 1
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
                    # Capturar mejoras significativas
                    if rutas_intermedias is not None:
                        rutas_intermedias.append(deepcopy(mejor_ruta))
            else:  # Peor solución
                # Aceptar con probabilidad exp(-delta/T)
                probabilidad = math.exp(-delta / temperatura)
                if random.random() < probabilidad:
                    ruta_actual = nueva_ruta
                    dist_actual = nueva_dist
            
            # Capturar rutas intermedias cada N iteraciones
            if rutas_intermedias is not None and iteracion_global % capturar_cada == 0:
                rutas_intermedias.append(deepcopy(mejor_ruta))
        
        # Enfriar temperatura
        temperatura *= alpha
    
    if rutas_intermedias is not None:
        rutas_intermedias.append(deepcopy(mejor_ruta))
    
    return mejor_ruta


# Calcula la longitud de la ruta
def longitud(coords, ruta):
    total = 0.0
    for i in range(len(ruta) - 1):
        total += distancia(coords[ruta[i]], coords[ruta[i + 1]])
    return total


def graficar_ruta(coords, ruta, ids, titulo, ax, mostrar_etiquetas=True):
    """Función elegante y minimalista para graficar la ruta"""
    
    # Dibujar todos los puntos con estilo limpio
    x_all = [p[0] for p in coords]
    y_all = [p[1] for p in coords]
    
    # Puntos con estilo elegante
    ax.scatter(x_all, y_all, c='#3498db', s=70, alpha=0.6, 
              edgecolors='#2c3e50', linewidth=1.2, zorder=3)
    
    # Dibujar la ruta con línea suave
    ruta_x = [coords[i][0] for i in ruta]
    ruta_y = [coords[i][1] for i in ruta]
    
    # Ruta principal elegante
    ax.plot(ruta_x, ruta_y, color='#e74c3c', linewidth=2.5, alpha=0.8, 
           solid_capstyle='round', zorder=2)
    
    # Marcar inicio y fin con estilo minimalista
    ax.scatter(coords[ruta[0]][0], coords[ruta[0]][1], c='#2ecc71', s=200, 
              marker='o', edgecolors='#27ae60', linewidth=2.5, zorder=4, label='Inicio')
    ax.scatter(coords[ruta[-1]][0], coords[ruta[-1]][1], c='#e74c3c', s=200, 
              marker='s', edgecolors='#c0392b', linewidth=2.5, zorder=4, label='Fin')
    
    # Etiquetas solo si hay pocos puntos
    if mostrar_etiquetas and len(coords) <= 30:
        for idx in [ruta[0], ruta[-1]]:  # Solo inicio y fin
            ax.annotate(str(ids[idx]), (coords[idx][0], coords[idx][1]), 
                       xytext=(8, 8), textcoords='offset points', 
                       fontsize=10, color='#2c3e50', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                                alpha=0.9, edgecolor='#95a5a6', linewidth=1))
    
    # Título elegante
    ax.set_title(titulo, fontsize=14, color='#2c3e50', weight='bold', pad=15)
    
    # Leyenda minimalista
    ax.legend(loc='upper right', fontsize=10, frameon=True, 
             shadow=False, fancybox=False, framealpha=0.95,
             edgecolor='#bdc3c7')
    
    # Grid sutil
    ax.grid(True, alpha=0.2, linestyle='-', color='#bdc3c7', linewidth=0.5)
    ax.set_facecolor('#f8f9fa')
    
    # Bordes limpios
    for spine in ax.spines.values():
        spine.set_edgecolor('#bdc3c7')
        spine.set_linewidth(1)


# Función principal interactiva
def main():
    # Configuración inicial limpia
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor('#ffffff')
    
    # Layout con dos paneles principales
    # Panel izquierdo: gráfica principal
    ax_main = plt.subplot2grid((12, 3), (0, 0), rowspan=9, colspan=2)
    
    # Panel derecho: información y estadísticas
    ax_stats = plt.subplot2grid((12, 3), (0, 2), rowspan=9, colspan=1)
    ax_stats.axis('off')
    
    # Variables globales
    global coords, ids, rutas_intermedias, ruta_inicial, ruta_final, mostrar_etiquetas
    global temp_inicial, temp_final, alpha_sa, iters_temp, num_intentos_sa
    coords = []
    ids = []
    rutas_intermedias = []
    mostrar_etiquetas = True
    velocidad_anim = 200
    
    # Parámetros de Simulated Annealing
    temp_inicial = 10000
    temp_final = 0.01
    alpha_sa = 0.97
    iters_temp = 300
    num_intentos_sa = 10
    
    # Widgets en la parte inferior con espaciado uniforme
    # Primera fila de controles
    ax_num = plt.axes([0.08, 0.18, 0.12, 0.025])
    num_text = TextBox(ax_num, 'N° puntos:', initial='40', color='#ecf0f1')
    
    ax_temp_ini = plt.axes([0.08, 0.14, 0.12, 0.025])
    temp_ini_text = TextBox(ax_temp_ini, 'Temp Inicial:', initial='10000', color='#ecf0f1')
    
    ax_temp_fin = plt.axes([0.08, 0.10, 0.12, 0.025])
    temp_fin_text = TextBox(ax_temp_fin, 'Temp Final:', initial='0.01', color='#ecf0f1')
    
    # Segunda fila de controles
    ax_alpha = plt.axes([0.30, 0.18, 0.12, 0.025])
    alpha_text = TextBox(ax_alpha, 'Alpha:', initial='0.97', color='#ecf0f1')
    
    ax_iters = plt.axes([0.30, 0.14, 0.12, 0.025])
    iters_text = TextBox(ax_iters, 'Iters/Temp:', initial='300', color='#ecf0f1')
    
    ax_intentos = plt.axes([0.30, 0.10, 0.12, 0.025])
    intentos_text = TextBox(ax_intentos, 'N° Intentos SA:', initial='10', color='#ecf0f1')
    
    # Slider de velocidad
    ax_slider = plt.axes([0.08, 0.05, 0.34, 0.02])
    slider_velocidad = Slider(ax_slider, 'Velocidad Anim (ms)', 50, 500, valinit=200, 
                              valstep=50, color='#3498db')
    
    # Botones
    ax_gen = plt.axes([0.52, 0.16, 0.10, 0.04])
    button_gen = Button(ax_gen, 'Generar', color='#3498db', hovercolor='#2980b9')
    button_gen.label.set_color('white')
    button_gen.label.set_weight('bold')
    
    ax_opt = plt.axes([0.52, 0.10, 0.10, 0.04])
    button_opt = Button(ax_opt, 'Optimizar SA', color='#9b59b6', hovercolor='#8e44ad')
    button_opt.label.set_color('white')
    button_opt.label.set_weight('bold')
    
    ax_anim = plt.axes([0.52, 0.04, 0.10, 0.04])
    button_anim = Button(ax_anim, 'Animar', color='#e74c3c', hovercolor='#c0392b')
    button_anim.label.set_color('white')
    button_anim.label.set_weight('bold')
    
    # Panel de información elegante
    info_text = ax_main.text(0.02, 0.98, "", transform=ax_main.transAxes, 
                            ha='left', va='top', fontsize=10, color='#2c3e50', 
                            weight='normal', family='monospace',
                            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', 
                                     alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5))
    
    # Texto de estadísticas en panel derecho
    stats_text = None
    
    def actualizar_panel_stats(dist_inicial, dist_2opt, dist_final, mejora_2opt, mejora_sa, mejora_total, n_puntos):
        """Actualiza el panel de estadísticas"""
        ax_stats.clear()
        ax_stats.axis('off')
        
        # Título del panel
        ax_stats.text(0.5, 0.95, 'ESTADÍSTICAS', ha='center', va='top', 
                     fontsize=14, weight='bold', color='#2c3e50',
                     transform=ax_stats.transAxes)
        
        # Información general
        y_pos = 0.88
        ax_stats.text(0.1, y_pos, f'Puntos: {n_puntos}', ha='left', va='top', 
                     fontsize=11, color='#34495e', transform=ax_stats.transAxes)
        
        # Distancias
        y_pos -= 0.08
        ax_stats.text(0.1, y_pos, 'DISTANCIAS', ha='left', va='top', 
                     fontsize=11, weight='bold', color='#2c3e50',
                     transform=ax_stats.transAxes)
        
        y_pos -= 0.06
        ax_stats.text(0.1, y_pos, f'Inicial: {dist_inicial:.2f}', ha='left', va='top', 
                     fontsize=10, color='#e74c3c', transform=ax_stats.transAxes)
        
        y_pos -= 0.05
        ax_stats.text(0.1, y_pos, f'Post 2-opt: {dist_2opt:.2f}', ha='left', va='top', 
                     fontsize=10, color='#f39c12', transform=ax_stats.transAxes)
        
        y_pos -= 0.05
        ax_stats.text(0.1, y_pos, f'Final (SA): {dist_final:.2f}', ha='left', va='top', 
                     fontsize=10, color='#2ecc71', weight='bold', transform=ax_stats.transAxes)
        
        # Mejoras
        y_pos -= 0.08
        ax_stats.text(0.1, y_pos, 'MEJORAS', ha='left', va='top', 
                     fontsize=11, weight='bold', color='#2c3e50',
                     transform=ax_stats.transAxes)
        
        y_pos -= 0.06
        ax_stats.text(0.1, y_pos, f'2-opt: {mejora_2opt:.2f}%', ha='left', va='top', 
                     fontsize=10, color='#f39c12', transform=ax_stats.transAxes)
        
        y_pos -= 0.05
        ax_stats.text(0.1, y_pos, f'Annealing: {mejora_sa:.2f}%', ha='left', va='top', 
                     fontsize=10, color='#9b59b6', transform=ax_stats.transAxes)
        
        y_pos -= 0.05
        ax_stats.text(0.1, y_pos, f'Total: {mejora_total:.2f}%', ha='left', va='top', 
                     fontsize=10, color='#2ecc71', weight='bold', transform=ax_stats.transAxes)
        
        # Gráfico de barras de mejora
        y_pos -= 0.10
        ax_stats.text(0.1, y_pos, 'EVOLUCIÓN', ha='left', va='top', 
                     fontsize=11, weight='bold', color='#2c3e50',
                     transform=ax_stats.transAxes)
        
        # Mini gráfico de barras
        y_pos -= 0.05
        barras_x = [0.15, 0.4, 0.65]
        barras_y_base = y_pos - 0.15
        max_altura = 0.12
        
        # Normalizar alturas
        max_dist = max(dist_inicial, dist_2opt, dist_final)
        h1 = (dist_inicial / max_dist) * max_altura
        h2 = (dist_2opt / max_dist) * max_altura
        h3 = (dist_final / max_dist) * max_altura
        
        rect1 = plt.Rectangle((barras_x[0], barras_y_base), 0.15, h1, 
                              color='#e74c3c', alpha=0.7, transform=ax_stats.transAxes)
        rect2 = plt.Rectangle((barras_x[1], barras_y_base), 0.15, h2, 
                              color='#f39c12', alpha=0.7, transform=ax_stats.transAxes)
        rect3 = plt.Rectangle((barras_x[2], barras_y_base), 0.15, h3, 
                              color='#2ecc71', alpha=0.7, transform=ax_stats.transAxes)
        
        ax_stats.add_patch(rect1)
        ax_stats.add_patch(rect2)
        ax_stats.add_patch(rect3)
        
        # Etiquetas de barras
        label_y = barras_y_base - 0.03
        ax_stats.text(barras_x[0] + 0.075, label_y, 'Inicial', ha='center', va='top', 
                     fontsize=8, color='#2c3e50', rotation=0, transform=ax_stats.transAxes)
        ax_stats.text(barras_x[1] + 0.075, label_y, '2-opt', ha='center', va='top', 
                     fontsize=8, color='#2c3e50', rotation=0, transform=ax_stats.transAxes)
        ax_stats.text(barras_x[2] + 0.075, label_y, 'SA', ha='center', va='top', 
                     fontsize=8, color='#2c3e50', rotation=0, transform=ax_stats.transAxes)
        
        # Parámetros SA utilizados
        y_pos = barras_y_base - 0.12
        ax_stats.text(0.1, y_pos, 'PARÁMETROS SA', ha='left', va='top', 
                     fontsize=11, weight='bold', color='#2c3e50',
                     transform=ax_stats.transAxes)
        
        y_pos -= 0.06
        ax_stats.text(0.1, y_pos, f'T₀: {temp_inicial}', ha='left', va='top', 
                     fontsize=9, color='#34495e', transform=ax_stats.transAxes)
        y_pos -= 0.04
        ax_stats.text(0.1, y_pos, f'Tₓ: {temp_final}', ha='left', va='top', 
                     fontsize=9, color='#34495e', transform=ax_stats.transAxes)
        y_pos -= 0.04
        ax_stats.text(0.1, y_pos, f'α: {alpha_sa}', ha='left', va='top', 
                     fontsize=9, color='#34495e', transform=ax_stats.transAxes)
        y_pos -= 0.04
        ax_stats.text(0.1, y_pos, f'Iters: {iters_temp}', ha='left', va='top', 
                     fontsize=9, color='#34495e', transform=ax_stats.transAxes)
        y_pos -= 0.04
        ax_stats.text(0.1, y_pos, f'Intentos: {num_intentos_sa}', ha='left', va='top', 
                     fontsize=9, color='#34495e', transform=ax_stats.transAxes)
    
    def generar_y_resolver(event):
        global coords, ids, rutas_intermedias, ruta_inicial, ruta_final
        global temp_inicial, temp_final, alpha_sa, iters_temp, num_intentos_sa
        
        try:
            n_puntos = int(num_text.text)
            if n_puntos < 3:
                print("Error: Mínimo 3 puntos.")
                return
            if n_puntos > 300:
                print("Advertencia: Más de 300 puntos puede ser lento.")
        except ValueError:
            print("Error: Ingresa un número válido.")
            return
        
        # Leer parámetros de SA
        try:
            temp_inicial = float(temp_ini_text.text)
            temp_final = float(temp_fin_text.text)
            alpha_sa = float(alpha_text.text)
            iters_temp = int(iters_text.text)
            num_intentos_sa = int(intentos_text.text)
        except ValueError:
            print("Error: Parámetros inválidos para SA.")
            return
        
        # Generar coordenadas
        puntos = [(i, random.uniform(15, 90), random.uniform(15, 90)) 
                 for i in range(1, n_puntos + 1)]
        puntos.sort(key=lambda t: t[0])
        ids = [p[0] for p in puntos]
        coords = [(p[1], p[2]) for p in puntos]
        
        print(f"\n=== Generando solución para {n_puntos} puntos ===")
        
        # Paso 1: Vecino más cercano
        ruta_inicial = vecino_mas_cercano(coords)
        dist_inicial = longitud(coords, ruta_inicial)
        print(f"1. Vecino más cercano - Distancia: {dist_inicial:.2f}")
        
        # Paso 2: 2-opt mejorado
        rutas_intermedias = [deepcopy(ruta_inicial)]
        ruta = dos_opt_mejorado(coords, ruta_inicial, rutas_intermedias)
        dist_2opt = longitud(coords, ruta)
        mejora_2opt = ((dist_inicial - dist_2opt) / dist_inicial * 100)
        print(f"2. Después de 2-opt - Distancia: {dist_2opt:.2f} (mejora: {mejora_2opt:.2f}%)")
        
        # Guardar ruta después de 2-opt
        ruta_final = ruta
        dist_final = dist_2opt
        mejora_sa = 0
        mejora_total = mejora_2opt
        
        # Actualizar visualización
        info_str = f"Puntos: {n_puntos}  |  Inicial: {dist_inicial:.2f}  |  2-opt: {dist_2opt:.2f}  |  Mejora: {mejora_2opt:.1f}%"
        info_text.set_text(info_str)
        
        # Graficar con límites fijos
        ax_main.clear()
        x_min, x_max = min([p[0] for p in coords]) - 5, max([p[0] for p in coords]) + 5
        y_min, y_max = min([p[1] for p in coords]) - 5, max([p[1] for p in coords]) + 5
        
        graficar_ruta(coords, ruta_final, ids, 
                     f"Ruta Optimizada con 2-opt ({n_puntos} puntos) - Distancia: {dist_final:.2f}", 
                     ax_main, mostrar_etiquetas)
        
        ax_main.set_xlim(x_min, x_max)
        ax_main.set_ylim(y_min, y_max)
        ax_main.set_aspect('equal', adjustable='box')
        
        # Re-agregar info text después de clear
        info_text.set_text(info_str)
        
        # Actualizar panel de estadísticas
        actualizar_panel_stats(dist_inicial, dist_2opt, dist_final, mejora_2opt, mejora_sa, mejora_total, n_puntos)
        
        fig.canvas.draw_idle()
    
    button_gen.on_clicked(generar_y_resolver)
    
    def optimizar_con_sa(event):
        global coords, ids, rutas_intermedias, ruta_final
        global temp_inicial, temp_final, alpha_sa, iters_temp, num_intentos_sa
        
        if not coords:
            print("Primero genera los puntos.")
            return
        
        print(f"\n=== Optimizando con Simulated Annealing ===")
        print(f"Parámetros: T₀={temp_inicial}, Tₓ={temp_final}, α={alpha_sa}, Iters={iters_temp}, Intentos={num_intentos_sa}")
        
        # Obtener ruta actual
        if len(rutas_intermedias) > 0:
            ruta_base = rutas_intermedias[-1]
        else:
            ruta_base = ruta_final
        
        dist_antes_sa = longitud(coords, ruta_base)
        
        # Ejecutar múltiples intentos de SA
        mejor_ruta_global = ruta_base
        mejor_dist_global = dist_antes_sa
        
        # Limpiar rutas intermedias para la animación de SA
        rutas_sa = [deepcopy(ruta_base)]
        
        for intento in range(1, num_intentos_sa + 1):
            print(f"   Intento {intento}/{num_intentos_sa}...", end=" ")
            ruta_temp = simulated_annealing(coords, ruta_base, temp_inicial, temp_final, 
                                          alpha_sa, iters_temp, rutas_sa, capturar_cada=50)
            dist_temp = longitud(coords, ruta_temp)
            print(f"Distancia: {dist_temp:.2f}")
            
            if dist_temp < mejor_dist_global:
                mejor_ruta_global = ruta_temp
                mejor_dist_global = dist_temp
                print(f"      ¡Nueva mejor distancia encontrada!")
        
        ruta_final = mejor_ruta_global
        dist_final = mejor_dist_global
        
        # Agregar a rutas intermedias para animación
        rutas_intermedias.extend(rutas_sa)
        
        # Calcular mejoras
        dist_inicial = longitud(coords, vecino_mas_cercano(coords))
        mejora_sa = ((dist_antes_sa - dist_final) / dist_antes_sa * 100)
        mejora_total = ((dist_inicial - dist_final) / dist_inicial * 100)
        
        print(f"\nResultado SA - Distancia: {dist_final:.2f} (mejora adicional: {mejora_sa:.2f}%)")
        print(f"Mejora total: {mejora_total:.2f}%")
        
        # Actualizar visualización
        info_str = f"Puntos: {len(coords)}  |  Inicial: {dist_inicial:.2f}  |  Final (SA): {dist_final:.2f}  |  Mejora Total: {mejora_total:.1f}%"
        info_text.set_text(info_str)
        
        # Graficar resultado final
        ax_main.clear()
        x_min, x_max = min([p[0] for p in coords]) - 5, max([p[0] for p in coords]) + 5
        y_min, y_max = min([p[1] for p in coords]) - 5, max([p[1] for p in coords]) + 5
        
        graficar_ruta(coords, ruta_final, ids, 
                     f"Ruta Optimizada con SA ({len(coords)} puntos) - Distancia: {dist_final:.2f}", 
                     ax_main, mostrar_etiquetas)
        
        ax_main.set_xlim(x_min, x_max)
        ax_main.set_ylim(y_min, y_max)
        ax_main.set_aspect('equal', adjustable='box')
        
        info_text.set_text(info_str)
        
        # Actualizar panel de estadísticas
        mejora_2opt = ((dist_inicial - dist_antes_sa) / dist_inicial * 100)
        actualizar_panel_stats(dist_inicial, dist_antes_sa, dist_final, mejora_2opt, mejora_sa, mejora_total, len(coords))
        
        fig.canvas.draw_idle()
    
    button_opt.on_clicked(optimizar_con_sa)
    
    def animar_iteraciones(event):
        if not rutas_intermedias:
            print("Primero genera y resuelve los datos.")
            return
        
        # Crear figura de animación con espacio para título y progreso
        fig_anim = plt.figure(figsize=(14, 9))
        fig_anim.patch.set_facecolor('#ffffff')
        
        # Ajustar layout para dar espacio al título y progreso
        ax_anim = plt.subplot2grid((20, 1), (1, 0), rowspan=18, fig=fig_anim)
        
        # Calcular límites fijos para toda la animación
        x_all = [p[0] for p in coords]
        y_all = [p[1] for p in coords]
        x_min, x_max = min(x_all) - 5, max(x_all) + 5
        y_min, y_max = min(y_all) - 5, max(y_all) + 5
        
        # Título fijo en la parte superior
        titulo_text = fig_anim.text(0.5, 0.96, "", ha='center', va='top', 
                                    fontsize=14, color='#2c3e50', weight='bold')
        
        # Texto de progreso en la parte inferior
        progress_text = fig_anim.text(0.5, 0.02, "", ha='center', va='bottom', 
                                     fontsize=11, color='#2c3e50', weight='bold',
                                     bbox=dict(boxstyle="round,pad=0.4", 
                                              facecolor='#ecf0f1', alpha=0.9,
                                              edgecolor='#95a5a6', linewidth=1.5))
        
        def update(frame):
            ax_anim.clear()
            
            # Establecer límites fijos
            ax_anim.set_xlim(x_min, x_max)
            ax_anim.set_ylim(y_min, y_max)
            ax_anim.set_aspect('equal', adjustable='box')
            
            # Graficar frame actual sin título (lo pondremos arriba)
            dist_actual = longitud(coords, rutas_intermedias[frame])
            progreso = (frame / (len(rutas_intermedias) - 1)) * 100
            
            # Graficar ruta sin título en el eje
            graficar_ruta(coords, rutas_intermedias[frame], ids, "", ax_anim, False)
            
            # Actualizar título principal arriba
            titulo = f"Optimización TSP en Tiempo Real\nIteración {frame}/{len(rutas_intermedias)-1}  |  Distancia Actual: {dist_actual:.2f}"
            titulo_text.set_text(titulo)
            
            # Actualizar progreso
            barra = '█' * int(progreso / 2) + '░' * (50 - int(progreso / 2))
            progress_text.set_text(f"Progreso: {progreso:.0f}% [{barra}]")
        
        velocidad = int(slider_velocidad.val)
        ani = FuncAnimation(fig_anim, update, frames=len(rutas_intermedias), 
                          interval=velocidad, repeat=False, blit=False)
        
        plt.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.08)
        plt.show()
    
    button_anim.on_clicked(animar_iteraciones)
    
    # Título inicial elegante
    ax_main.set_title("Problema del Viajero (TSP) - Optimización con Simulated Annealing", 
                     fontsize=16, color='#2c3e50', weight='bold', pad=20)
    ax_main.text(0.5, 0.5, "Configura los parámetros y presiona 'Generar'\nLuego 'Optimizar SA' para aplicar Simulated Annealing\nPresiona 'Animar' para ver la optimización paso a paso", 
                transform=ax_main.transAxes, ha='center', va='center', 
                fontsize=13, color='#7f8c8d', style='italic',
                bbox=dict(boxstyle="round,pad=1", facecolor='white', 
                         alpha=0.9, edgecolor='#bdc3c7', linewidth=1.5))
    
    # Panel de estadísticas inicial
    ax_stats.text(0.5, 0.5, "Estadísticas\naparecerán\naquí", ha='center', va='center', 
                 fontsize=12, color='#95a5a6', style='italic', transform=ax_stats.transAxes)
    
    plt.tight_layout()
    plt.show()


# Main
if __name__ == "__main__":
    main()

