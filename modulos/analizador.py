"""
╔══════════════════════════════════════════════════════════════╗
║  SentiMiner V2 — Módulo: Motor de Análisis NLP              ║
║  HU-003: Clasificar sentimiento por línea (POS/NEG/NEU)     ║
║  HU-004: Calcular porcentaje global de sentimientos         ║
║  Motor  : transformers + BETO (BERT en Español - HuggingFace)║
║  Fallback: Léxico propio en español (sin dependencias)      ║
║  Dev 1  : Cristian Pinedo + Klismann De La Cruz             ║
║  Dev 2  : Jose Quispe + Ronald Saavedra                     ║
╚══════════════════════════════════════════════════════════════╝
"""
import re

try:
    from modulos.logger import log_error, log_info
except ImportError:
    def log_error(*a, **kw): pass
    def log_info(*a, **kw): pass

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL MODELO
# Modelo: lxyuan/distilbert-base-multilingual-cased-sentiments-student
#   - DistilBERT fine-tuneado para sentimiento multilingüe
#   - Idiomas: ES, EN, FR, DE, PT, IT, NL, ZH, JA, KO...
#   - Labels de salida: positive / negative / neutral
#   - Tamaño descarga: ~260 MB (se cachea localmente)
#   - Fuente: https://huggingface.co/lxyuan/distilbert-base-multilingual-...
# ══════════════════════════════════════════════════════════════

MODELO_HF = "finiteautomata/beto-sentiment-analysis"
# BETO = BERT en Español, fine-tuneado para análisis de sentimiento
# Labels: POS (Positivo), NEG (Negativo), NEU (Neutro)
# Entrenado con texto en español (tweets + noticias + reviews)
# Fuente: https://huggingface.co/finiteautomata/beto-sentiment-analysis
# Tamaño: ~500 MB (se descarga y cachea solo la primera vez)
MAX_TOKENS = 512   # Límite del modelo BERT

# Pipeline singleton (carga perezosa: solo cuando se necesita)
_pipeline_nlp = None
_modo_activo   = None   # 'modelo' o 'lexico'


# ── Detección de transformers ────────────────────────────────
try:
    from transformers import pipeline as hf_pipeline
    _TRANSFORMERS_OK = True
except ImportError:
    _TRANSFORMERS_OK = False


def _cargar_pipeline():
    """
    Carga el pipeline de HuggingFace una sola vez (lazy loading).
    Retorna el pipeline o None si no está disponible.
    """
    global _pipeline_nlp, _modo_activo

    if _pipeline_nlp is not None:
        return _pipeline_nlp

    if not _TRANSFORMERS_OK:
        print("  [!] transformers no instalado → usando léxico de respaldo.")
        print("      Para instalar: pip install transformers torch")
        _modo_activo = 'lexico'
        return None

    try:
        print(f"\n  Cargando modelo NLP desde HuggingFace...")
        print(f"  Modelo  : {MODELO_HF}")
        print(f"  (Primera ejecucion: descarga ~260 MB — esto tarda solo la primera vez)")

        _pipeline_nlp = hf_pipeline(
            task="text-classification",
            model=MODELO_HF,
            tokenizer=MODELO_HF,
            top_k=1,            # Solo devuelve la etiqueta con mayor confianza
            truncation=True,
            max_length=MAX_TOKENS,
            device=-1,          # CPU (cambiar a 0 si hay GPU disponible)
        )
        _modo_activo = 'modelo'
        print(f"  [OK]  Modelo cargado. Motor NLP: transformers + HuggingFace")
        return _pipeline_nlp

    except Exception as e:
        print(f"  [!] Error al cargar modelo: {e}")
        print("      Usando léxico de respaldo.")
        log_error("_cargar_pipeline", e, f"Modelo: {MODELO_HF}")
        _modo_activo = 'lexico'
        return None


def _mapear_label(label_modelo):
    """
    Convierte el label del modelo HuggingFace al formato interno.
    BETO labels: 'POS' / 'NEG' / 'NEU'
    """
    label = label_modelo.upper().strip()
    if label in ('POS', 'POSITIVE', 'POSITIVO'):
        return 'Positivo'
    elif label in ('NEG', 'NEGATIVE', 'NEGATIVO'):
        return 'Negativo'
    else:
        return 'Neutro'


def get_modo():
    """Retorna el modo activo: 'modelo' o 'lexico'."""
    return _modo_activo or ('modelo' if _TRANSFORMERS_OK else 'lexico')


# ══════════════════════════════════════════════════════════════
# LÉXICO DE RESPALDO (se usa si transformers no está disponible)
# ══════════════════════════════════════════════════════════════

PALABRAS_POSITIVAS = {
    'bueno','buena','buenos','buenas','bien','buen',
    'excelente','excelentes','excepcional','excepcionales',
    'genial','fantástico','fantástica','maravilloso','maravillosa',
    'increíble','increíbles','espectacular','perfecto','perfecta',
    'hermoso','hermosa','bonito','bonita','lindo','linda',
    'agradable','agradables','placentero','placentera',
    'positivo','positiva','correcto','correcta',
    'adecuado','adecuada','apropiado','apropiada',
    'claro','clara','fácil','fáciles','sencillo','sencilla',
    'rápido','rápida','eficiente','eficientes','eficaz','eficaces',
    'efectivo','efectiva','útil','útiles','valioso','valiosa',
    'importante','importantes','relevante','relevantes',
    'innovador','innovadora','creativo','creativa',
    'inteligente','inteligentes','amable','amables',
    'cordial','cordiales','atento','atenta','cariñoso','cariñosa',
    'tranquilo','tranquila','sereno','serena',
    'fuerte','fuertes','robusto','robusta','sólido','sólida',
    'interesante','interesantes','emocionante','emocionantes',
    'motivado','motivada','inspirado','inspirada',
    'satisfecho','satisfecha','satisfechos','satisfechas',
    'contento','contenta','feliz','felices','alegre','alegres',
    'emocionado','emocionada','entusiasmado','entusiasmada',
    'orgulloso','orgullosa','encantado','encantada',
    'esperanzador','esperanzadora',
    'aprendo','aprendí','aprendemos','aprendió','aprender',
    'mejoro','mejoré','mejoramos','mejoró','mejorar',
    'logro','logré','logramos','logró','lograr','lograron',
    'consigo','conseguí','conseguimos','consiguió','conseguir',
    'gano','gané','ganamos','ganó','ganar','ganaron',
    'avanzo','avancé','avanzamos','avanzó','avanzar',
    'crezco','crecí','crecemos','creció','crecer','crecieron',
    'progreso','progresé','progresamos','progresó','progresar',
    'ayudo','ayudé','ayudamos','ayudó','ayudar','ayudaron',
    'colaboro','colaboré','colaboramos','colaboró','colaborar',
    'disfruto','disfruté','disfrutamos','disfrutó','disfrutar',
    'celebro','celebré','celebramos','celebró','celebrar',
    'agradezco','agradecí','agradecemos','agradeció','agradecer',
    'recomiendo','recomendé','recomendamos','recomendó','recomendar',
    'apoyo','apoyé','apoyamos','apoyó','apoyar','apoyaron',
    'confío','confié','confiamos','confió','confiar',
    'valoro','valoré','valoramos','valoró','valorar',
    'éxito','logro','logros','victoria','victorias','triunfo','triunfos',
    'beneficio','beneficios','ventaja','ventajas','oportunidad','oportunidades',
    'solución','soluciones','mejora','mejoras','progreso','avance','avances',
    'calidad','excelencia','valor','valores','confianza','esperanza','fe',
    'amor','amistad','apoyo','ayuda','colaboración','equipo',
    'innovación','creatividad','talento','habilidad','habilidades',
    'conocimiento','aprendizaje','crecimiento','desarrollo','evolución',
    'bienestar','salud','alegría','felicidad','paz','armonía',
    'prosperidad','gracias','estupendo','bravo','espléndido',
    'acertado','definitivamente','totalmente','completamente',
}

PALABRAS_NEGATIVAS = {
    'malo','mala','malos','malas','mal',
    'terrible','terribles','horrendo','horrenda','horrible','horribles',
    'pésimo','pésima','pésimos','pésimas',
    'deficiente','deficientes','inadecuado','inadecuada',
    'insuficiente','insuficientes','incompleto','incompleta',
    'difícil','difíciles','complicado','complicada',
    'problemático','problemática','negativo','negativa',
    'perjudicial','perjudiciales','dañino','dañina',
    'triste','tristes','melancólico','melancólica',
    'infeliz','infelices','descontento','descontenta',
    'decepcionado','decepcionada','frustrado','frustrada',
    'enojado','enojada','molesto','molesta','irritado','irritada',
    'furioso','furiosa','preocupado','preocupada',
    'angustiado','angustiada','ansioso','ansiosa',
    'estresado','estresada','agotado','agotada',
    'cansado','cansada','aburrido','aburrida',
    'perdido','perdida','confundido','confundida',
    'incapaz','incapaces','ineficiente','ineficientes',
    'lento','lenta','obsoleto','obsoleta',
    'injusto','injusta','peligroso','peligrosa',
    'costoso','costosa','caro','cara','excesivo','excesiva',
    'inútil','inútiles',
    'fallo','fallé','fallamos','falló','fallar','fallaron',
    'fracaso','fracasé','fracasamos','fracasó','fracasar','fracasaron',
    'pierdo','perdí','perdemos','perdió','perder','perdieron',
    'empeoro','empeoré','empeoramos','empeoró','empeorar',
    'rechazo','rechacé','rechazamos','rechazó','rechazar','rechazaron',
    'abandono','abandoné','abandonamos','abandonó','abandonar',
    'critico','critiqué','criticamos','criticó','criticar','criticaron',
    'odio','odié','odiamos','odió','odiar','odiaron',
    'temo','temí','tememos','temió','temer','temieron',
    'sufro','sufrí','sufrimos','sufrió','sufrir','sufrieron',
    'lamento','lamenté','lamentamos','lamentó','lamentar','lamentaron',
    'problema','problemas','error','errores','falla','fallas',
    'fracaso','fracasos','pérdida','pérdidas','daño','daños',
    'amenaza','amenazas','crisis','conflicto','conflictos',
    'dificultad','dificultades','obstáculo','obstáculos',
    'queja','quejas','crítica','críticas',
    'violencia','agresión','abuso','corrupción','fraude',
    'desempleo','pobreza','miseria','injusticia','desigualdad',
    'decepción','frustración','angustia','miedo','temor',
    'tristeza','dolor','sufrimiento','odio','rencor',
    'catástrofe','tragedia','desastre','ruina',
}

NEGACIONES = {
    'no','ni','nunca','jamás','tampoco','sin','nadie','nada',
    'ningún','ninguno','ninguna',
}

INTENSIFICADORES = {
    'muy','bastante','sumamente','totalmente','completamente',
    'definitivamente','absolutamente','extremadamente','super',
    'tremendamente','enormemente','muchísimo','demasiado',
    'altamente','profundamente','increíblemente',
}


def _preprocesar(texto):
    """Normaliza texto para análisis léxico."""
    texto = texto.lower()
    texto = re.sub(r'[^\w\sáéíóúüñàèìòùâêîôûãõ]', ' ', texto, flags=re.UNICODE)
    return re.sub(r'\s+', ' ', texto).strip()


def _clasificar_lexico(texto):
    """Clasificación de respaldo usando léxico propio en español."""
    tokens = _preprocesar(texto).split()
    score = 0.0
    palabras_pos = []
    palabras_neg = []

    for i, token in enumerate(tokens):
        ventana = tokens[max(0, i - 2):i]
        es_negacion = any(n in ventana for n in NEGACIONES)
        factor = 1.5 if (i > 0 and tokens[i - 1] in INTENSIFICADORES) else 1.0

        if token in PALABRAS_POSITIVAS:
            delta = factor * (1.0 if not es_negacion else -1.0)
            score += delta
            if not es_negacion:
                palabras_pos.append(token)
            else:
                palabras_neg.append(f"no {token}")
        elif token in PALABRAS_NEGATIVAS:
            score += factor * (-1.0 if not es_negacion else 0.5)
            if not es_negacion:
                palabras_neg.append(token)

    if score > 0.4:
        sent, kw = 'Positivo', palabras_pos[:3]
    elif score < -0.4:
        sent, kw = 'Negativo', palabras_neg[:3]
    else:
        sent, kw = 'Neutro', []

    return {
        'sentimiento': sent,
        'score': round(abs(score) / max(len(tokens), 1), 4),  # normalizado [0,1]
        'palabras_clave': kw,
        'texto': texto,
        'confianza': None,
        'motor': 'lexico',
    }


# ══════════════════════════════════════════════════════════════
# API PÚBLICA — HU-003 y HU-004
# ══════════════════════════════════════════════════════════════

def clasificar_linea(texto):
    """
    HU-003: Clasifica el sentimiento de una línea.

    Flujo:
      1. Intenta usar el pipeline de transformers (HuggingFace)
      2. Si no está disponible → usa léxico propio como fallback

    Parámetros:
        texto (str): Línea de texto a clasificar

    Retorna:
        dict: sentimiento, score, palabras_clave, texto, motor, confianza
    """
    if not texto or not texto.strip():
        return {
            'sentimiento': 'Neutro', 'score': 0.0,
            'palabras_clave': [], 'texto': texto,
            'confianza': None, 'motor': 'n/a',
        }

    nlp = _cargar_pipeline()

    if nlp is not None:
        try:
            # El pipeline retorna [[{'label': ..., 'score': ...}]]
            pred = nlp(texto[:MAX_TOKENS])[0]
            # top_k=1 puede retornar lista de 1 elemento
            if isinstance(pred, list):
                pred = pred[0]

            sent = _mapear_label(pred['label'])
            conf = round(pred['score'] * 100, 1)

            return {
                'sentimiento': sent,
                'score': round(pred['score'], 4),
                'palabras_clave': [],
                'texto': texto,
                'confianza': conf,
                'motor': 'transformers/HuggingFace',
            }
        except Exception as e:
            # Fallback silencioso al léxico
            resultado = _clasificar_lexico(texto)
            resultado['_error_modelo'] = str(e)
            return resultado

    return _clasificar_lexico(texto)


def analizar_sentimiento(lineas):
    """
    HU-003: Analiza el sentimiento de TODAS las líneas del archivo.

    Usa procesamiento por lotes (batch) cuando el modelo HuggingFace
    está disponible para mayor eficiencia.

    Parámetros:
        lineas (list[str]): Líneas de texto a analizar

    Retorna:
        list[dict]: Un resultado por línea
    """
    print(f"\n  Analizando sentimiento de {len(lineas)} lineas...")

    nlp = _cargar_pipeline()

    if nlp is not None:
        # ── Procesamiento por lotes con el modelo HuggingFace ──
        try:
            textos_truncados = [t[:MAX_TOKENS] for t in lineas]
            predicciones = nlp(textos_truncados, batch_size=16)

            resultados = []
            for i, (linea, pred) in enumerate(zip(lineas, predicciones)):
                # top_k=1 puede retornar lista
                p = pred[0] if isinstance(pred, list) else pred
                sent = _mapear_label(p['label'])
                resultados.append({
                    'numero': i + 1,
                    'texto': linea,
                    'sentimiento': sent,
                    'score': round(p['score'], 4),
                    'palabras_clave': [],
                    'confianza': round(p['score'] * 100, 1),
                    'motor': 'transformers/HuggingFace',
                })

            print(f"  [OK]  Clasificacion completada con modelo HuggingFace.")
            print(f"  Motor : {MODELO_HF}")
            return resultados

        except Exception as e:
            print(f"  [!] Error en modelo batch: {e}")
            print("  [!] Recuperación automática → usando léxico de respaldo...")
            log_error("analizar_sentimiento (batch)", e, f"{len(lineas)} líneas")

    # ── Fallback: léxico propio ──────────────────────────────
    resultados = []
    for i, linea in enumerate(lineas, start=1):
        r = _clasificar_lexico(linea)
        resultados.append({
            'numero': i,
            'texto': linea,
            'sentimiento': r['sentimiento'],
            'score': r['score'],
            'palabras_clave': r['palabras_clave'],
            'confianza': None,
            'motor': 'lexico',
        })

    print(f"  [OK]  Clasificacion completada con léxico propio.")
    return resultados


def calcular_estadisticas(resultados):
    """
    HU-004: Calcula el porcentaje global de cada tipo de sentimiento.

    Criterios verificados:
      AC-1: Porcentajes con 2 decimales de precisión
      AC-2: Suma exacta = 100.00%
      AC-3: Un solo tipo → 100% / 0% / 0%
      AC-4: Redondeo consistente

    Parámetros:
        resultados (list[dict]): Lista de resultados por línea

    Retorna:
        dict: total, conteo, porcentajes, predominante, confianza_promedio
    """
    total = len(resultados)
    if total == 0:
        return None

    # Conteo por categoría
    conteo = {'Positivo': 0, 'Negativo': 0, 'Neutro': 0}
    for r in resultados:
        conteo[r['sentimiento']] += 1

    # AC-1, AC-4: Porcentajes con 2 decimales
    pct = {s: round((conteo[s] / total) * 100, 2) for s in conteo}

    # AC-2: Garantizar suma = 100.00%
    suma = pct['Positivo'] + pct['Negativo'] + pct['Neutro']
    dif  = round(100.0 - suma, 2)
    if dif != 0.0:
        sent_max = max(conteo, key=conteo.get)
        pct[sent_max] = round(pct[sent_max] + dif, 2)

    # Sentimiento predominante
    predominante = max(conteo, key=conteo.get)

    # Confianza promedio (solo si se usó el modelo)
    confianzas = [r['confianza'] for r in resultados if r.get('confianza') is not None]
    conf_promedio = round(sum(confianzas) / len(confianzas), 1) if confianzas else None

    # Motor usado
    motores = set(r.get('motor', 'lexico') for r in resultados)
    motor = 'transformers/HuggingFace' if 'transformers/HuggingFace' in motores else 'lexico'

    return {
        'total': total,
        'conteo': conteo,
        'porcentajes': pct,
        'predominante': predominante,
        'confianza_promedio': conf_promedio,
        'motor': motor,
    }
