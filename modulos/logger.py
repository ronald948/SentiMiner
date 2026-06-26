"""
╔══════════════════════════════════════════════════════════════╗
║  SentiMiner V2 — Módulo: Logger de Errores                  ║
║  HU-008: Manejo de errores y recuperación automática        ║
║  Responsable: Developer 2 (Jose Quispe + Ronald Saavedra)   ║
╚══════════════════════════════════════════════════════════════╝
"""
import os
import sys
import traceback
from datetime import datetime


LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sentiminer_errores.log')


def _timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log_error(contexto: str, excepcion: Exception = None, detalle: str = None):
    """
    HU-008: Registra un error en sentiminer_errores.log de forma silenciosa.
    No interrumpe el flujo de la aplicación.

    Parámetros:
        contexto (str): Descripción de dónde ocurrió el error
        excepcion (Exception): Excepción capturada (opcional)
        detalle (str): Información adicional (opcional)
    """
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'─'*60}\n")
            f.write(f"[{_timestamp()}] ERROR EN: {contexto}\n")
            if detalle:
                f.write(f"Detalle   : {detalle}\n")
            if excepcion:
                f.write(f"Excepción : {type(excepcion).__name__}: {excepcion}\n")
                f.write("Traceback :\n")
                f.write(traceback.format_exc())
    except Exception:
        pass  # El logger nunca debe romper la aplicación


def log_info(mensaje: str):
    """Registra un evento informativo en el log."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{_timestamp()}] INFO: {mensaje}\n")
    except Exception:
        pass


def limpiar_log():
    """Limpia el archivo de log (útil al iniciar sesión)."""
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    except Exception:
        pass


def mostrar_ruta_log():
    """Retorna la ruta absoluta del archivo de log."""
    return os.path.abspath(LOG_FILE)
