import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from copy import deepcopy
import random
from matplotlib.widgets import Button, TextBox, Slider
import tempfile
import os

# Configuración de estilo matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['figure.facecolor'] = '#ffffff'

# Nombre del archivo de datos
DATA_FILE = "datos_200.txt"

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
    fig = plt.figure(figsize=(14, 9))
    fig.patch.set_facecolor('#ffffff')
    
    # Layout simple y organizado
    ax_main = plt.subplot2grid((10, 1), (0, 0), rowspan=8)
    
    # Variables globales
    global coords, ids, rutas_intermedias, ruta_inicial, ruta_final, mostrar_etiquetas
    coords = []
    ids = []
    rutas_intermedias = []
    mostrar_etiquetas = True
    velocidad_anim = 200
    
    # Widgets en la parte inferior con espaciado uniforme
    ax_num = plt.axes([0.15, 0.12, 0.15, 0.03])
    num_text = TextBox(ax_num, 'Número de puntos:', initial='40', color='#ecf0f1')
    
    ax_slider = plt.axes([0.15, 0.06, 0.3, 0.02])
    slider_velocidad = Slider(ax_slider, 'Velocidad (ms)', 50, 500, valinit=200, 
                              valstep=50, color='#3498db')
    
    ax_gen = plt.axes([0.55, 0.10, 0.12, 0.04])
    button_gen = Button(ax_gen, 'Generar', color='#3498db', hovercolor='#2980b9')
    button_gen.label.set_color('white')
    button_gen.label.set_weight('bold')
    
    ax_anim = plt.axes([0.70, 0.10, 0.12, 0.04])
    button_anim = Button(ax_anim, 'Animar', color='#e74c3c', hovercolor='#c0392b')
    button_anim.label.set_color('white')
    button_anim.label.set_weight('bold')
    
    # Panel de información elegante
    info_text = ax_main.text(0.02, 0.98, "", transform=ax_main.transAxes, 
                            ha='left', va='top', fontsize=10, color='#2c3e50', 
                            weight='normal', family='monospace',
                            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', 
                                     alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5))
    
    def generar_y_resolver(event):
        global coords, ids, rutas_intermedias, ruta_inicial, ruta_final
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
        
        # Generar coordenadas
        puntos = [(i, random.uniform(15, 90), random.uniform(15, 90)) 
                 for i in range(1, n_puntos + 1)]
        puntos.sort(key=lambda t: t[0])
        ids = [p[0] for p in puntos]
        coords = [(p[1], p[2]) for p in puntos]
        
        print(f"Generando solución para {n_puntos} puntos...")
        
        # Resolver TSP
        ruta_inicial = vecino_mas_cercano(coords)
        rutas_intermedias = [deepcopy(ruta_inicial)]
        ruta_final = dos_opt_simple(coords, ruta_inicial, rutas_intermedias)
        
        # Calcular estadísticas
        dist_inicial = longitud(coords, ruta_inicial)
        dist_final = longitud(coords, ruta_final)
        mejora = ((dist_inicial - dist_final) / dist_inicial * 100)
        iteraciones = len(rutas_intermedias) - 1
        
        # Actualizar info
        info_str = f"Puntos: {n_puntos}  |  Inicial: {dist_inicial:.2f}  |  Final: {dist_final:.2f}  |  Mejora: {mejora:.1f}%  |  Iteraciones: {iteraciones}"
        info_text.set_text(info_str)
        
        print(f"Distancia inicial: {dist_inicial:.2f}")
        print(f"Distancia final: {dist_final:.2f}")
        print(f"Mejora: {mejora:.2f}% en {iteraciones} iteraciones")
        
        # Graficar con límites fijos
        ax_main.clear()
        x_min, x_max = min([p[0] for p in coords]) - 5, max([p[0] for p in coords]) + 5
        y_min, y_max = min([p[1] for p in coords]) - 5, max([p[1] for p in coords]) + 5
        
        graficar_ruta(coords, ruta_final, ids, 
                     f"Ruta Optimizada ({n_puntos} puntos) - Distancia: {dist_final:.2f}", 
                     ax_main, mostrar_etiquetas)
        
        ax_main.set_xlim(x_min, x_max)
        ax_main.set_ylim(y_min, y_max)
        ax_main.set_aspect('equal', adjustable='box')
        
        # Re-agregar info text después de clear
        info_text.set_text(info_str)
        
        fig.canvas.draw_idle()
    
    button_gen.on_clicked(generar_y_resolver)
    
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
            titulo = f"Problema del Viajero (TSP) - Optimización en Tiempo Real\nIteración {frame}/{len(rutas_intermedias)-1}  |  Distancia Actual: {dist_actual:.2f}"
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
    ax_main.set_title("Problema del Viajero (TSP) - Optimización Interactiva", 
                     fontsize=16, color='#2c3e50', weight='bold', pad=20)
    ax_main.text(0.5, 0.5, "Ingresa el número de puntos y presiona 'Generar'\nLuego 'Animar' para ver la optimización", 
                transform=ax_main.transAxes, ha='center', va='center', 
                fontsize=13, color='#7f8c8d', style='italic',
                bbox=dict(boxstyle="round,pad=1", facecolor='white', 
                         alpha=0.9, edgecolor='#bdc3c7', linewidth=1.5))
    
    plt.tight_layout()
    plt.show()


# Main
if __name__ == "__main__":
    main()
