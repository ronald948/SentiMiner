"""
╔══════════════════════════════════════════════════════════════╗
║  SentiMiner V2 — Módulo: Cargador de Archivos               ║
║  HU-001: Cargar archivo .txt con transcripciones            ║
║  HU-002: Leer y procesar todas las líneas del archivo       ║
║  Responsable: Developer 2 (Jose Quispe + Ronald Saavedra)   ║
╚══════════════════════════════════════════════════════════════╝
"""
import os


def _detectar_encoding(ruta):
    """
    Detecta la codificación del archivo.
    Intenta UTF-8 primero, luego Latin-1 como fallback.
    """
    try:
        import chardet
        with open(ruta, 'rb') as f:
            raw = f.read()
        resultado = chardet.detect(raw)
        enc = resultado.get('encoding') or 'utf-8'
        return enc
    except ImportError:
        # Fallback manual: intenta UTF-8, luego Latin-1
        for enc in ('utf-8', 'utf-8-sig', 'latin-1', 'cp1252'):
            try:
                with open(ruta, 'r', encoding=enc) as f:
                    f.read()
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return 'latin-1'


def cargar_archivo(ruta):
    """
    HU-001: Carga y valida el archivo .txt.

    Criterios de aceptación implementados:
      AC-1: Archivo válido → carga exitosa + mensaje de confirmación
      AC-2: Archivo no encontrado → mensaje de error claro
      AC-3: Formato incorrecto (no .txt) → rechaza + solicita formato válido
      AC-4: Archivo vacío → notifica que no hay contenido para analizar

    Parámetros:
        ruta (str): Ruta del archivo .txt a cargar

    Retorna:
        list[str] | None: Lista de líneas procesadas, o None si hay error
    """
    # ── AC-2: Validar que la ruta no esté vacía ─────────────
    ruta = ruta.strip()
    if not ruta:
        print("\n  [ERR] Error: No ingresó ninguna ruta.")
        print("     Intente nuevamente con la ruta completa del archivo .txt")
        return None

    # ── AC-2: Validar que el archivo existe ──────────────────
    if not os.path.exists(ruta):
        print(f"\n  [ERR] Error: El archivo no fue encontrado.")
        print(f"     Ruta ingresada: '{ruta}'")
        print("     Verifique que la ruta sea correcta e intente nuevamente.")
        return None

    # ── AC-3: Validar extensión .txt ─────────────────────────
    _, extension = os.path.splitext(ruta)
    if extension.lower() != '.txt':
        print(f"\n  [ERR] Error: El archivo debe tener extensión .txt")
        print(f"     Extensión detectada: '{extension}' → No válida")
        print("     SentiMiner V2 solo procesa archivos de texto plano (.txt)")
        return None

    # ── AC-4: Validar que el archivo no esté vacío ───────────
    if os.path.getsize(ruta) == 0:
        print(f"\n  [!]  Advertencia: El archivo '{os.path.basename(ruta)}' está vacío.")
        print("     No hay contenido para analizar.")
        return None

    # ── AC-1: Leer el archivo con detección de encoding ──────
    try:
        encoding = _detectar_encoding(ruta)
        with open(ruta, 'r', encoding=encoding, errors='replace') as f:
            contenido = f.read()

        nombre = os.path.basename(ruta)
        print(f"\n  [OK]  Archivo cargado exitosamente: '{nombre}'")
        print(f"     Codificación detectada: {encoding.upper()}")

        # Delegar lectura de líneas a HU-002
        return leer_lineas(contenido)

    except PermissionError:
        print(f"\n  [ERR] Error: Sin permisos para leer '{ruta}'.")
        return None
    except Exception as e:
        print(f"\n  [ERR] Error inesperado al leer el archivo: {e}")
        return None


def leer_lineas(contenido):
    """
    HU-002: Lee y procesa todas las líneas del archivo .txt.

    Criterios de aceptación implementados:
      AC-1: Archivo con múltiples líneas → procesa cada una individualmente
      AC-2: Líneas en blanco → omitidas, continúa con el resto
      AC-3: Caracteres especiales y tildes → manejados sin error
      AC-4: Archivo de una sola línea → analiza correctamente

    Parámetros:
        contenido (str): Contenido completo del archivo como string

    Retorna:
        list[str] | None: Lista de líneas con contenido, o None si no hay texto
    """
    todas = contenido.splitlines()          # AC-3: splitlines maneja \r\n, \n, \r
    procesadas = []
    omitidas = 0

    for linea in todas:
        limpia = linea.strip()
        if limpia:                          # AC-2: omitir líneas en blanco
            procesadas.append(limpia)       # AC-1, AC-3: preservar texto con tildes
        else:
            omitidas += 1

    print(f"     Total de líneas en el archivo : {len(todas)}")
    print(f"     Líneas con contenido procesadas: {len(procesadas)}")
    print(f"     Líneas en blanco omitidas      : {omitidas}")

    if not procesadas:                      # AC-4 edge case: solo blancos
        print("\n  [!]  El archivo no contiene líneas con texto para analizar.")
        return None

    return procesadas                       # AC-4: funciona con 1 sola línea también
