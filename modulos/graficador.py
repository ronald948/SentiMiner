"""
╔══════════════════════════════════════════════════════════════╗
║  SentiMiner V2 — Módulo: Generador de Gráficos              ║
║  HU-006: Generar gráfico .png con distribución              ║
║          de sentimientos (pastel + barras)                   ║
║  Responsable: Developer 3 (Jimmy Garcia Acostupa)           ║
╚══════════════════════════════════════════════════════════════╝
"""
import os
from datetime import datetime

# ── Detección de matplotlib (opcional) ───────────────────────
try:
    import matplotlib
    matplotlib.use('Agg')   # Backend sin pantalla (para consola)
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    _MATPLOTLIB_OK = True
except ImportError:
    _MATPLOTLIB_OK = False


# ── Paleta de colores SentiMiner ─────────────────────────────
COLORES = {
    'Positivo': '#2ECC71',   # Verde esmeralda
    'Negativo': '#E74C3C',   # Rojo
    'Neutro':   '#95A5A6',   # Gris azulado
}

ICONOS = {
    'Positivo': '(+)',
    'Negativo': '(-)',
    'Neutro':   '( )',
}


def matplotlib_disponible() -> bool:
    """Retorna True si matplotlib está instalado y disponible."""
    return _MATPLOTLIB_OK


def generar_grafico(estadisticas: dict, ruta_archivo: str = None) -> str | None:
    """
    HU-006: Genera un gráfico .png con dos paneles:
      - Panel izquierdo: gráfico de pastel (pie chart)
      - Panel derecho: gráfico de barras horizontales

    Criterios de aceptación implementados:
      AC-1: Genera gráfico con porcentajes de positivo, negativo y neutro
      AC-2: Muestra el sentimiento predominante destacado
      AC-3: Guarda el archivo .png en la misma carpeta del txt analizado
      AC-4: Si matplotlib no está disponible → informa y retorna None

    Parámetros:
        estadisticas (dict): Resultado de calcular_estadisticas()
        ruta_archivo (str): Ruta del archivo .txt analizado (para guardar el .png junto a él)

    Retorna:
        str | None: Ruta del .png generado, o None si no se pudo generar
    """
    # AC-4: Verificar que matplotlib esté disponible
    if not _MATPLOTLIB_OK:
        print("\n  [!]  matplotlib no está instalado.")
        print("     Para habilitar gráficos ejecute:")
        print("     pip install matplotlib")
        return None

    if not estadisticas:
        print("\n  [!]  No hay estadísticas para graficar.")
        return None

    # ── Determinar ruta de salida ─────────────────────────────
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_png = f"reporte_sentiminer_{timestamp}.png"

    if ruta_archivo and os.path.isfile(ruta_archivo):
        carpeta = os.path.dirname(os.path.abspath(ruta_archivo))
    else:
        carpeta = os.getcwd()

    ruta_png = os.path.join(carpeta, nombre_png)

    # ── Preparar datos ────────────────────────────────────────
    categorias  = ['Positivo', 'Negativo', 'Neutro']
    porcentajes = [estadisticas['porcentajes'][s] for s in categorias]
    conteos     = [estadisticas['conteo'][s] for s in categorias]
    colores     = [COLORES[s] for s in categorias]
    total       = estadisticas['total']
    predominante = estadisticas['predominante']
    motor        = estadisticas.get('motor', 'N/A')

    # ── Crear figura con 2 paneles ────────────────────────────
    fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor('#F8F9FA')

    # ─────────────────────────────────────────────────────────
    # PANEL 1: Gráfico de pastel
    # ─────────────────────────────────────────────────────────
    explode = [0.08 if s == predominante else 0.0 for s in categorias]

    wedges, texts, autotexts = ax_pie.pie(
        porcentajes,
        labels=None,
        colors=colores,
        autopct='%1.1f%%',
        startangle=140,
        explode=explode,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        pctdistance=0.75,
    )

    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
        autotext.set_color('white')

    # Leyenda del pie
    leyenda_items = [
        mpatches.Patch(color=COLORES[s], label=f"{ICONOS[s]} {s}  —  {porcentajes[i]:.1f}%  ({conteos[i]} frases)")
        for i, s in enumerate(categorias)
    ]
    ax_pie.legend(handles=leyenda_items, loc='lower center',
                  bbox_to_anchor=(0.5, -0.15), fontsize=10, framealpha=0.9)

    ax_pie.set_title('Distribución de Sentimientos', fontsize=13,
                     fontweight='bold', pad=15, color='#2C3E50')
    ax_pie.set_facecolor('#F8F9FA')

    # ─────────────────────────────────────────────────────────
    # PANEL 2: Gráfico de barras horizontales
    # ─────────────────────────────────────────────────────────
    y_pos = range(len(categorias))

    bars = ax_bar.barh(
        list(y_pos),
        porcentajes,
        color=colores,
        height=0.5,
        edgecolor='white',
        linewidth=1.5,
    )

    # Etiquetas en las barras
    for bar, pct, cnt in zip(bars, porcentajes, conteos):
        x_label = bar.get_width() + 0.8
        ax_bar.text(
            x_label, bar.get_y() + bar.get_height() / 2,
            f'{pct:.1f}%  ({cnt})',
            va='center', ha='left', fontsize=10, fontweight='bold', color='#2C3E50'
        )

    ax_bar.set_yticks(list(y_pos))
    ax_bar.set_yticklabels(
        [f"{ICONOS[s]}  {s}" for s in categorias],
        fontsize=11, fontweight='bold'
    )
    ax_bar.set_xlabel('Porcentaje (%)', fontsize=10, color='#7F8C8D')
    ax_bar.set_xlim(0, max(porcentajes) * 1.35)
    ax_bar.set_title('Distribución por Categoría', fontsize=13,
                     fontweight='bold', pad=15, color='#2C3E50')
    ax_bar.set_facecolor('#F8F9FA')
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.grid(axis='x', linestyle='--', alpha=0.4)

    # ─────────────────────────────────────────────────────────
    # Título general y pie de figura
    # ─────────────────────────────────────────────────────────
    conf_str = ''
    if estadisticas.get('confianza_promedio'):
        conf_str = f"  |  Confianza promedio: {estadisticas['confianza_promedio']:.1f}%"

    fig.suptitle(
        f'SentiMiner V2  |  Análisis de Sentimiento\n'
        f'Total: {total} frases  |  Predominante: {predominante.upper()}{conf_str}',
        fontsize=12, fontweight='bold', color='#2C3E50', y=1.01
    )

    pie_texto = (
        f'Motor NLP: {motor}  ·  '
        f'Universidad Privada del Norte (UPN)  ·  '
        f'Proyecto de Disrupción Tecnológica  ·  Grupo 1'
    )
    fig.text(0.5, -0.03, pie_texto, ha='center', fontsize=8, color='#95A5A6', style='italic')

    plt.tight_layout()

    # ── Guardar .png ──────────────────────────────────────────
    try:
        plt.savefig(ruta_png, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return ruta_png
    except Exception as e:
        plt.close(fig)
        print(f"\n  [ERR] No se pudo guardar el gráfico: {e}")
        return None
