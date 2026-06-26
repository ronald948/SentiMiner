"""
╔══════════════════════════════════════════════════════════════════╗
║                     SentiMiner V2                               ║
║           Analizador de Sentimiento en Textos                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Universidad Privada del Norte (UPN)                            ║
║  Proyecto de Disrupción Tecnológica                             ║
║  Grupo 1 — Sprint Review #2                                     ║
╠══════════════════════════════════════════════════════════════════╣
║  SPRINT 1 — HUs implementadas:                                  ║
║    HU-001  Cargar archivo .txt          → cargador.py          ║
║    HU-002  Leer líneas del archivo      → cargador.py          ║
║    HU-003  Clasificar sentimiento       → analizador.py        ║
║    HU-004  Calcular porcentajes globales→ analizador.py        ║
║    HU-005  Reporte en consola           → reporte.py           ║
╠══════════════════════════════════════════════════════════════════╣
║  SPRINT 2 — HUs implementadas:                                  ║
║    HU-006  Gráfico pastel/barras .png   → graficador.py        ║
║    HU-007  Menú interactivo mejorado    → sentiminer.py        ║
║    HU-008  Manejo de errores avanzado   → logger.py            ║
╚══════════════════════════════════════════════════════════════════╝
"""
import sys
import os
import io

# ── Forzar salida UTF-8 en Windows (evita error cp1252 con tildes/Unicode) ──
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Asegurar que los módulos sean accesibles desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modulos.cargador   import cargar_archivo
from modulos.analizador import analizar_sentimiento, calcular_estadisticas
from modulos.reporte    import mostrar_reporte
from modulos.graficador import generar_grafico, matplotlib_disponible
from modulos.logger     import log_error, log_info, limpiar_log, mostrar_ruta_log


# ── Constantes ───────────────────────────────────────────────
VERSION = "2.0.0 (Sprint 2)"
ANCHO   = 65

# ── Historial de la sesión (HU-007) ─────────────────────────
_historial = []   # lista de dicts: {archivo, total, predominante, ruta_png}


# ══════════════════════════════════════════════════════════════
# UTILIDADES DE PRESENTACIÓN
# ══════════════════════════════════════════════════════════════

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_banner():
    print('\n' + '═' * ANCHO)
    print('  SentiMiner V2  |  Análisis de Sentimiento en Textos')
    print('  Grupo 1  |  Universidad Privada del Norte  |  UPN')
    print('═' * ANCHO)


def _pedir_opcion(prompt: str, opciones_validas: set) -> str:
    """
    HU-008: Solicita una opción al usuario con validación robusta.
    Nunca lanza excepción por entrada inesperada.
    """
    while True:
        try:
            raw = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            return 'salir'
        if raw in opciones_validas:
            return raw
        print(f"  [!]  Opción inválida. Elija entre: {', '.join(sorted(opciones_validas))}")


# ══════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════

def mostrar_menu():
    mostrar_banner()
    print()
    print('  MENÚ PRINCIPAL')
    print('  ' + '─' * 40)
    print('  [1]  Analizar archivo .txt')
    print('  [2]  Historial de la sesión')
    print('  [3]  Información del sistema')
    print('  [4]  Salir')
    print('  ' + '─' * 40)
    print()


# ══════════════════════════════════════════════════════════════
# OPCIÓN 1 — ANALIZAR ARCHIVO + SUB-MENÚ POST-ANÁLISIS
# ══════════════════════════════════════════════════════════════

def opcion_analizar():
    """HU-001 a HU-006: Flujo completo de análisis con sub-menú de resultados."""
    print('\n' + '─' * ANCHO)
    print('  ANÁLISIS DE ARCHIVO')
    print('─' * ANCHO)

    # ── Pedir ruta con validación (HU-008) ───────────────────
    try:
        ruta = input('\n  Ingrese la ruta del archivo .txt a analizar:\n  > ').strip()
    except (KeyboardInterrupt, EOFError):
        print('\n  [!]  Operación cancelada.')
        return

    # HU-001 + HU-002
    lineas = cargar_archivo(ruta)
    if lineas is None:
        return

    # HU-003
    resultados = analizar_sentimiento(lineas)

    # HU-004
    estadisticas = calcular_estadisticas(resultados)

    # Guardar en historial (HU-007)
    entrada_historial = {
        'archivo': ruta,
        'total': estadisticas['total'],
        'predominante': estadisticas['predominante'],
        'porcentajes': estadisticas['porcentajes'],
        'ruta_png': None,
    }
    _historial.append(entrada_historial)

    log_info(f"Análisis completado: {os.path.basename(ruta)} — {estadisticas['total']} líneas")

    # ── Sub-menú post-análisis (HU-007) ──────────────────────
    _submenu_resultados(ruta, resultados, estadisticas, entrada_historial)


def _submenu_resultados(ruta, resultados, estadisticas, entrada_historial):
    """
    HU-007: Sub-menú que aparece después de analizar un archivo.
    Permite al usuario explorar los resultados sin volver al menú principal.
    """
    pred = estadisticas['predominante']
    total = estadisticas['total']

    while True:
        print('\n' + '═' * ANCHO)
        print(f'  ANÁLISIS COMPLETO  |  {os.path.basename(ruta)}')
        print(f'  {total} frases  |  Predominante: {pred.upper()}')
        print('═' * ANCHO)
        print()
        print('  ¿Qué desea hacer con los resultados?')
        print('  ' + '─' * 40)
        print('  [1]  Ver reporte en consola')
        print('  [2]  Ver detalle línea por línea')

        if matplotlib_disponible():
            print('  [3]  Generar gráfico .png')
        else:
            print('  [3]  Generar gráfico .png  [requiere: pip install matplotlib]')

        print('  [4]  Analizar otro archivo')
        print('  [5]  Volver al menú principal')
        print('  ' + '─' * 40)
        print()

        opcion = _pedir_opcion('  Seleccione una opción [1-5]: ', {'1','2','3','4','5','salir'})

        if opcion == '1':
            mostrar_reporte(ruta, resultados, estadisticas)

        elif opcion == '2':
            from modulos.reporte import _mostrar_detalle
            _mostrar_detalle(resultados)

        elif opcion == '3':
            _generar_y_mostrar_grafico(ruta, estadisticas, entrada_historial)

        elif opcion == '4':
            opcion_analizar()
            return

        elif opcion in ('5', 'salir'):
            return

        print('\n  Presione ENTER para continuar...', end='')
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            return


def _generar_y_mostrar_grafico(ruta, estadisticas, entrada_historial):
    """HU-006: Genera el gráfico .png y muestra dónde se guardó."""
    print('\n  Generando gráfico...')
    try:
        ruta_png = generar_grafico(estadisticas, ruta)
        if ruta_png:
            entrada_historial['ruta_png'] = ruta_png
            print(f'\n  [OK]  Gráfico generado exitosamente.')
            print(f'     Guardado en: {ruta_png}')
            log_info(f"Gráfico generado: {ruta_png}")
        # Si es None, graficador.py ya mostró el mensaje de error
    except Exception as e:
        print(f'\n  [ERR] Error al generar gráfico: {e}')
        log_error("_generar_y_mostrar_grafico", e)


# ══════════════════════════════════════════════════════════════
# OPCIÓN 2 — HISTORIAL DE SESIÓN (HU-007)
# ══════════════════════════════════════════════════════════════

def opcion_historial():
    """HU-007: Muestra todos los archivos analizados en la sesión actual."""
    sep = '─' * (ANCHO - 2)
    print('\n' + '═' * ANCHO)
    print('  HISTORIAL DE LA SESIÓN')
    print('═' * ANCHO)

    if not _historial:
        print('\n  No se ha analizado ningún archivo en esta sesión.')
        print('  Use la opción [1] para analizar un archivo .txt')
        print('\n' + '═' * ANCHO)
        return

    print(f'\n  {len(_historial)} archivo(s) analizados en esta sesión:\n')
    print(f'  {sep}')

    for idx, h in enumerate(_historial, 1):
        nombre = os.path.basename(h['archivo'])
        pred   = h['predominante']
        total  = h['total']
        pct    = h['porcentajes']
        png    = '  [PNG generado]' if h['ruta_png'] else ''

        print(f'\n  [{idx}]  {nombre}{png}')
        print(f'       Frases   : {total}')
        print(f'       Resultado: {pred.upper()}  '
              f'(+{pct["Positivo"]:.1f}%  -{pct["Negativo"]:.1f}%  ={pct["Neutro"]:.1f}%)')
        if h['ruta_png']:
            print(f'       Gráfico  : {h["ruta_png"]}')

    print(f'\n  {sep}')
    print(f'  Total Story Points Sprint 2: 11 SP completados')
    print('\n' + '═' * ANCHO)


# ══════════════════════════════════════════════════════════════
# OPCIÓN 3 — INFORMACIÓN DEL SISTEMA
# ══════════════════════════════════════════════════════════════

def opcion_info():
    sep = '─' * (ANCHO - 2)
    print('\n' + '═' * ANCHO)
    print('  INFORMACIÓN DEL SISTEMA')
    print('═' * ANCHO)

    print(f'\n  Nombre      : SentiMiner V2')
    print(f'  Versión     : {VERSION}')
    print(f'  Descripción : Herramienta de análisis de sentimiento')
    print(f'                en archivos de texto plano (.txt)')
    print(f'  Motor NLP   : BETO — BERT en Español (HuggingFace)')

    print(f'\n  {sep}')
    print(f'  DATOS ACADÉMICOS')
    print(f'  {sep}')
    print(f'  Institución : Universidad Privada del Norte (UPN)')
    print(f'  Asignatura  : Proyecto de Disrupción Tecnológica')
    print(f'  Docente     : Jorge Gustavo Moreno López')

    print(f'\n  {sep}')
    print(f'  EQUIPO SCRUM — GRUPO 1')
    print(f'  {sep}')
    print(f'  Stakeholder    : Jorge Gustavo Moreno López')
    print(f'  Product Owner  : Carlos Alberto Visurraga Sánchez')
    print(f'  Scrum Master   : Armando Cesar Torres Puertas')
    print(f'  Developer 1    : Cristian Alberto Pinedo Gómez')
    print(f'                   Klismann Henry De La Cruz Corrales')
    print(f'  Developer 2    : Jose Luis Quispe Aracayo')
    print(f'                   Ronald Martin Saavedra Garay')
    print(f'  Developer 3    : Jimmy David Garcia Acostupa')

    print(f'\n  {sep}')
    print(f'  ESTADO DEL SISTEMA')
    print(f'  {sep}')
    matplotlib_str = '[OK] Disponible' if matplotlib_disponible() else '[!] No instalado (pip install matplotlib)'
    print(f'  Gráficos     : {matplotlib_str}')
    print(f'  Log errores  : {mostrar_ruta_log()}')
    print(f'\n' + '═' * ANCHO)


# ══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def main():
    """HU-007 + HU-008: Punto de entrada con manejo global de errores."""
    limpiar_log()
    log_info(f"SentiMiner V2 iniciado — versión {VERSION}")

    while True:
        mostrar_menu()

        opcion = _pedir_opcion('  Seleccione una opción [1-4]: ', {'1','2','3','4','salir'})

        try:
            if opcion == '1':
                opcion_analizar()
            elif opcion == '2':
                opcion_historial()
            elif opcion == '3':
                opcion_info()
            elif opcion in ('4', 'salir'):
                print('\n  ¡Hasta luego! Gracias por usar SentiMiner V2.')
                print('  Grupo 1 — Universidad Privada del Norte\n')
                log_info("SentiMiner V2 cerrado normalmente.")
                sys.exit(0)

        except Exception as e:
            # HU-008: Captura global — nunca muestra traceback crudo al usuario
            print(f'\n  [ERR] Ocurrió un error inesperado: {e}')
            print(f'  El detalle fue registrado en: {mostrar_ruta_log()}')
            log_error("main (captura global)", e)

        print('\n  Presione ENTER para continuar...', end='')
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)


if __name__ == '__main__':
    main()
