"""
╔══════════════════════════════════════════════════════════════╗
║  SentiMiner V2 — Módulo: Reporte en Consola                 ║
║  HU-005: Mostrar reporte claro en consola con resumen       ║
║  Responsable: Developer 3 (Jimmy Garcia Acostupa)           ║
╚══════════════════════════════════════════════════════════════╝
"""
import os


# ── Constantes de presentación ───────────────────────────────
ANCHO = 65
ICONOS = {'Positivo': '(+)', 'Negativo': '(-)', 'Neutro': '( )'}
EMOJIS = {'Positivo': '[POS]', 'Negativo': '[NEG]', 'Neutro': '[NEU]'}


def _linea(caracter='─', ancho=ANCHO):
    return '  ' + caracter * ancho


def _barra_progreso(porcentaje, largo=25):
    """Genera una barra visual de progreso ASCII."""
    lleno = int(porcentaje / 100 * largo)
    vacio = largo - lleno
    return '█' * lleno + '░' * vacio


def mostrar_reporte(ruta_archivo, resultados, estadisticas):
    """
    HU-005: Muestra el reporte completo del análisis en consola.

    Criterios de aceptación implementados:
      AC-1: Muestra tabla con % positivo, negativo y neutro (reporte resumen)
      AC-2: Permite ver el detalle de clasificación de cada línea
      AC-3: Indica el sentimiento predominante del texto
      AC-4: Si no hay contenido procesable → informa al usuario

    Parámetros:
        ruta_archivo (str): Ruta del archivo analizado
        resultados (list[dict]): Resultados por línea
        estadisticas (dict): Estadísticas globales calculadas
    """
    # AC-4: Verificar que hay resultados
    if not resultados or not estadisticas:
        print("\n  [!]  No se generaron resultados.")
        print("     El archivo no contiene contenido válido para analizar.")
        return

    nombre = os.path.basename(ruta_archivo)

    # ── Banner principal ─────────────────────────────────────
    print('\n' + _linea('═'))
    print('  SentiMiner V2  |  RESULTADOS DEL ANÁLISIS')
    print(_linea('═'))

    # ── Información del archivo ──────────────────────────────
    print(f"\n  Archivo analizado : {nombre}")
    print(f"  Líneas procesadas : {estadisticas['total']}")

    # ── AC-1: Tabla de distribución de sentimientos ──────────
    print(f"\n  {_linea('─')}")
    print(f"  {'DISTRIBUCIÓN DE SENTIMIENTOS':^{ANCHO}}")
    print(f"  {_linea('─')}")

    for sent in ['Positivo', 'Negativo', 'Neutro']:
        cnt = estadisticas['conteo'][sent]
        pct = estadisticas['porcentajes'][sent]
        barra = _barra_progreso(pct)
        icono = ICONOS[sent]
        print(f"\n  {icono} {sent:<12}  {pct:>6.2f}%  {barra}  ({cnt} frases)")

    # ── AC-2: Verificación de suma ───────────────────────────
    p = estadisticas['porcentajes']
    suma = p['Positivo'] + p['Negativo'] + p['Neutro']
    print(f"\n  {'─'*ANCHO}")
    print(f"  Verificación suma: {p['Positivo']:.2f}% + "
          f"{p['Negativo']:.2f}% + "
          f"{p['Neutro']:.2f}% = {suma:.2f}%  ✓")

    # ── AC-3: Sentimiento predominante ───────────────────────
    pred = estadisticas['predominante']
    cnt_pred = estadisticas['conteo'][pred]
    print(f"\n  {'═'*ANCHO}")
    print(f"  >> SENTIMIENTO PREDOMINANTE: {pred.upper()}")
    print(f"     {cnt_pred} de {estadisticas['total']} frases "
          f"({estadisticas['porcentajes'][pred]:.2f}% del texto)")
    print(f"  {'═'*ANCHO}")

    # ── AC-2: Detalle línea por línea (opcional) ─────────────
    print(f"\n  ¿Ver detalle línea por línea? [s/n]: ", end='')
    try:
        respuesta = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        respuesta = 'n'

    if respuesta == 's':
        _mostrar_detalle(resultados)

    # ── Pie del reporte ──────────────────────────────────────
    print(f"\n  {_linea('═')}")
    print(f"  Análisis completado · SentiMiner V2 · Grupo 1 · UPN")
    print(f"  {_linea('═')}\n")


def _mostrar_detalle(resultados):
    """
    HU-005 AC-2: Muestra la clasificación de CADA línea del archivo.
    """
    print(f"\n  {_linea('═')}")
    print(f"  DETALLE POR LÍNEA  ({len(resultados)} líneas)")
    print(f"  {_linea('═')}")
    print(f"\n  {'#':>4}  {'Sent.':^10}  {'Score':>6}  Texto")
    print(f"  {_linea('─')}")

    for r in resultados:
        numero = r['numero']
        sent = r['sentimiento']
        score = r['score']
        texto = r['texto']
        icono = ICONOS[sent]

        # Truncar texto largo para la consola
        max_chars = ANCHO - 30
        texto_mostrar = texto[:max_chars] + '…' if len(texto) > max_chars else texto

        print(f"  {numero:>4}  {icono} {sent:<8}  {score:>+6.2f}  {texto_mostrar}")

        # Mostrar palabras clave si existen
        if r.get('palabras_clave'):
            kw = ', '.join(r['palabras_clave'])
            print(f"  {'':>4}  {'':10}  {'':>6}  → clave: [{kw}]")

    print(f"\n  {_linea('─')}")
    print(f"  Total: {len(resultados)} líneas clasificadas")
