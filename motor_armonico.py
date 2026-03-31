"""
Motor Armónico - Método de Dirección Armónica Gestual
=====================================================
Gestiona la lógica de acordes, notas, inversiones, bemoles,
notación latina/anglosajona y observaciones didácticas.

Diseñado para ser portable a Flutter/Dart en el futuro.
"""

# ---------------------------------------------------------------------------
# 1. DATOS BASE
# ---------------------------------------------------------------------------

# Escala cromática en notación latina (12 semitonos)
ESCALA_CROMATICA = [
    "Do", "Do#/Reb", "Re", "Re#/Mib", "Mi", "Fa",
    "Fa#/Solb", "Sol", "Sol#/Lab", "La", "La#/Sib", "Si"
]

# Mapeo limpio: nombre canónico -> índice en la escala cromática (0-11)
# NOTA: Dob y Fab NO se usan en este método porque son enarmónicos de Si y Mi
# respectivamente. Si alguien escribe "Dob" o "Fab", el parseo los normaliza
# directamente a "Si" y "Mi" antes de llegar aquí.
NOTA_A_INDICE = {
    "Do": 0,   "Reb": 1,   "Re": 2,   "Mib": 3,   "Mi": 4,
    "Fa": 5,   "Solb": 6,  "Sol": 7,   "Lab": 8,   "La": 9,
    "Sib": 10,  "Si": 11,
    # Sostenidos (se aceptan en entrada pero se normalizan internamente a bemoles)
    "Do#": 1,  "Re#": 3,  "Fa#": 6,  "Sol#": 8,  "La#": 10,
    # Mi# = Fa y Si# = Do: no tienen bemol, se normalizan a la nota natural
    "Mi#": 5,  "Si#": 0,
}

INDICE_A_NOTA_LATINA = {
    0: "Do", 1: "Reb", 2: "Re", 3: "Mib", 4: "Mi",
    5: "Fa", 6: "Solb", 7: "Sol", 8: "Lab", 9: "La",
    10: "Sib", 11: "Si"
}

# Notación anglosajona
LATINA_A_ANGLOSAJONA = {
    "Do": "C",   "Reb": "Db",  "Re": "D",   "Mib": "Eb",  "Mi": "E",
    "Fa": "F",   "Solb": "Gb", "Sol": "G",  "Lab": "Ab",  "La": "A",
    "Sib": "Bb", "Si": "B",
}

# Intervalos en semitonos para cada tipo de acorde
TIPOS_ACORDE = {
    "mayor":       {"intervalos": [0, 4, 7],       "sufijo": "",      "sufijo_anglo": ""},
    "menor":       {"intervalos": [0, 3, 7],       "sufijo": "m",     "sufijo_anglo": "m"},
    "aumentado":   {"intervalos": [0, 4, 8],       "sufijo": "aum",   "sufijo_anglo": "aug"},
    "disminuido":  {"intervalos": [0, 3, 6],       "sufijo": "dim",   "sufijo_anglo": "dim"},
    "7":           {"intervalos": [0, 4, 7, 10],   "sufijo": "7",     "sufijo_anglo": "7"},
    "maj7":        {"intervalos": [0, 4, 7, 11],   "sufijo": "maj7",  "sufijo_anglo": "maj7"},
    "m7":          {"intervalos": [0, 3, 7, 10],   "sufijo": "m7",    "sufijo_anglo": "m7"},
    "dim7":        {"intervalos": [0, 3, 6, 9],    "sufijo": "dim7",  "sufijo_anglo": "dim7"},
    "9":           {"intervalos": [0, 4, 7, 10, 14], "sufijo": "9",   "sufijo_anglo": "9"},
    "m9":          {"intervalos": [0, 3, 7, 10, 14], "sufijo": "m9",  "sufijo_anglo": "m9"},
    # NOTA: sus4, sus2, 6 y m6 han sido eliminados del sistema gestual.
    # El método solo permite 1 nota de bajo + 1 tríada en la mano derecha.
    # Esos tipos no son representables fielmente con esa restricción:
    #   sus4 (Do-Fa-Sol): ninguna tríada cubre las 3 notas sin añadir notas ajenas.
    #   sus2 (Do-Re-Sol): ídem.
    #   6   (Do-Mi-Sol-La): la tríada disponible más cercana añade notas incorrectas.
    #   m6  (Do-Mib-Sol-La): ídem.
}

# Configuración de dedos para el gesto (según el método)
DEDOS_MAP = {
    "Do":  {"dedos": 1, "descripcion": "1 dedo (Índice)"},
    "Re":  {"dedos": 2, "descripcion": "2 dedos (Victoria)"},
    "Mi":  {"dedos": 3, "descripcion": "3 dedos (Pulgar, Índice, Medio)"},
    "Fa":  {"dedos": 4, "descripcion": "4 dedos (Índice, Medio, Anular, Meñique)"},
    "Sol": {"dedos": 5, "descripcion": "Mano abierta (5 dedos)"},
    "La":  {"dedos": 1, "descripcion": "1 dedo (Pulgar)"},
    "Si":  {"dedos": 2, "descripcion": "2 dedos (Pulgar + Índice)"},
}

# Para bemoles: la nota base del gesto es la nota natural correspondiente.
# Ej: Reb -> gesto de Re (2 dedos Victoria) + dedos hacia abajo (mano izq)
#                                            + agitación lateral (mano der)
# IMPORTANTE: Dob y Fab NO están aquí porque en este método no existen:
#   - Dob se expresa directamente como Si (misma tecla, mismo gesto)
#   - Fab se expresa directamente como Mi (misma tecla, mismo gesto)
BEMOL_A_NATURAL = {
    "Reb": "Re", "Mib": "Mi", "Solb": "Sol", "Lab": "La", "Sib": "Si",
}

# Tipos de acorde que son tríadas simples: la mano derecha muestra la fundamental
# (mismo gesto que la izquierda, con diferente orientación/altura).
# Para el resto (extendidos), la mano derecha muestra la 3ª del acorde,
# que es la cabeza de la tríada que "rellena" el acorde completo.
TIPOS_TRIADA = {"mayor", "menor", "aumentado", "disminuido"}

OBSERVACIONES_AUTO = {
    "mayor": "Acorde mayor: sonoridad brillante y estable. Base de la armonía tonal.",
    "menor": "Acorde menor: sonoridad oscura y emotiva. Muy usado como ii, iii o vi en tonalidad mayor.",
    "aumentado": "Acorde aumentado: sonoridad tensa y suspensiva. Útil como dominante alterada.",
    "disminuido": "Acorde disminuido: sonoridad inestable. Funciona como acorde de paso o dominante sin fundamental.",
    "7": "Acorde de séptima dominante: genera tensión que pide resolver a la tónica.",
    "maj7": "Acorde de séptima mayor: sonoridad suave y jazzy. Típico como I o IV.",
    "m7": "Acorde menor séptima: muy usado en jazz y bossa nova como ii7.",
    "dim7": "Acorde disminuido séptima: totalmente simétrico (intervalos iguales). Gran recurso de modulación.",
    "9": "Acorde de novena: extiende la dominante con color adicional. Gestualmente: bajo en la fundamental, mano derecha muestra la tríada de la 5ª (5ª-7ª-9ª).",
    "m9": "Acorde menor novena: sonoridad rica y moderna. Gestualmente: bajo en la fundamental, mano derecha muestra la tríada menor de la 5ª (5ª-7ª-9ª).",
}


# ---------------------------------------------------------------------------
# 2. FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------

def nota_por_indice(indice):
    """Devuelve el nombre latino de una nota dado su índice cromático (0-11)."""
    return INDICE_A_NOTA_LATINA[indice % 12]


def obtener_notas_acorde(fundamental, tipo_acorde):
    """
    Calcula las notas de un acorde dada su fundamental y tipo.
    Devuelve lista de notas en notación latina.
    """
    if fundamental not in NOTA_A_INDICE:
        return None
    if tipo_acorde not in TIPOS_ACORDE:
        return None

    indice_base = NOTA_A_INDICE[fundamental]
    intervalos = TIPOS_ACORDE[tipo_acorde]["intervalos"]
    return [nota_por_indice(indice_base + i) for i in intervalos]


def nota_es_bemol(nota):
    """Determina si una nota es bemol (contiene 'b' pero no es 'Si')."""
    return nota in BEMOL_A_NATURAL


def nota_base_para_gesto(nota):
    """
    Devuelve la nota natural que determina el gesto de dedos.
    Para bemoles, devuelve la nota natural + indicación de agitación.
    """
    if nota in BEMOL_A_NATURAL:
        return BEMOL_A_NATURAL[nota]
    # Para notas naturales directas
    if nota in DEDOS_MAP:
        return nota
    # Si es un sostenido, buscamos el nombre alternativo
    return None


def nota_a_anglosajona(nota):
    """Convierte una nota latina a anglosajona."""
    return LATINA_A_ANGLOSAJONA.get(nota, nota)


def calcular_nota_mano_derecha(fundamental, tipo_acorde, notas):
    """
    Determina qué nota/gesto debe mostrar la mano derecha.

    Regla del método (restricción física: 1 bajo + 1 tríada):
      - Tríadas (mayor, menor, aumentado, disminuido):
          La mano derecha muestra la FUNDAMENTAL (mismo gesto que la izquierda).
          La orientación ↑/↓ y la altura pecho/cabeza describen el tipo de acorde.
          Ejemplo: Do Mayor → izq=Do, der=Do (pecho ↑)

      - Cuatríadas extendidas (7, m7, maj7, dim7):
          La mano derecha muestra la 3ª del acorde (índice 1).
          Esa nota encabeza la tríada superior (3ª-5ª-7ª) que rellena el acorde.
          Ejemplo: Re m7 (Re-Fa-La-Do) → der=Fa  (Fa-La-Do = mayor)

      - Acordes de novena (9, m9):
          La mano derecha muestra la 5ª del acorde (índice 2).
          Esa nota encabeza la tríada superior (5ª-7ª-9ª).
          La 3ª queda implícita; la 5ª ya suena como armónico natural del bajo.
          Ejemplo: Do 9 (Do-Mi-Sol-Sib-Re) → der=Sol  (Sol-Sib-Re = menor)
          Ejemplo: Do m9 (Do-Mib-Sol-Sib-Re) → der=Sol (Sol-Sib-Re = menor)

    Devuelve la nota latina que debe gesticular la mano derecha.
    """
    if tipo_acorde in TIPOS_TRIADA:
        return fundamental                  # tríada: derecha = fundamental
    elif tipo_acorde in ("9", "m9"):
        return notas[2]                     # novena: derecha = 5ª del acorde
    else:
        return notas[1]                     # cuatríada: derecha = 3ª del acorde


# ---------------------------------------------------------------------------
# 3. LÓGICA DE INVERSIONES
# ---------------------------------------------------------------------------

def calcular_inversiones_posibles(notas_acorde):
    """
    Dada una lista de notas del acorde, devuelve todas las inversiones posibles.
    - Estado fundamental (inversión 0): nota más grave = fundamental
    - 1ª inversión: nota más grave = 3ª del acorde
    - 2ª inversión: nota más grave = 5ª del acorde
    - 3ª inversión: solo para acordes de 4+ notas (7ª en el bajo)
    """
    n = len(notas_acorde)
    inversiones = {}
    nombres_inversion = [
        "Estado fundamental",
        "1ª inversión",
        "2ª inversión",
        "3ª inversión",
        "4ª inversión",
    ]
    for i in range(n):
        inv = notas_acorde[i:] + notas_acorde[:i]
        nombre = nombres_inversion[i] if i < len(nombres_inversion) else f"{i}ª inversión"
        inversiones[i] = {
            "nombre": nombre,
            "bajo": inv[0],
            "notas_ordenadas": inv,
        }
    return inversiones


def validar_inversion(notas_acorde, inversion_solicitada):
    """
    Valida si una inversión es posible para un acorde dado.
    Devuelve un diccionario con el resultado y un mensaje específico.

    Parámetros:
        notas_acorde: lista de notas del acorde
        inversion_solicitada: int (0 = fundamental, 1 = 1ª inv, 2 = 2ª inv, etc.)

    Retorna:
        dict con: valida (bool), mensaje (str), datos (dict o None)
    """
    n = len(notas_acorde)
    inversiones = calcular_inversiones_posibles(notas_acorde)
    max_inversion = n - 1

    nombres_inversion = {
        0: "estado fundamental",
        1: "1ª inversión",
        2: "2ª inversión",
        3: "3ª inversión",
        4: "4ª inversión",
    }
    nombre_sol = nombres_inversion.get(
        inversion_solicitada, f"{inversion_solicitada}ª inversión"
    )

    if inversion_solicitada < 0:
        return {
            "valida": False,
            "mensaje": f"La inversión no puede ser negativa.",
            "datos": None,
        }

    if inversion_solicitada > max_inversion:
        tipo_acorde = "tríada" if n == 3 else f"acorde de {n} notas"
        return {
            "valida": False,
            "mensaje": (
                f"No existe {nombre_sol} para una {tipo_acorde}. "
                f"Máximo: {nombres_inversion.get(max_inversion, f'{max_inversion}ª inversión')} "
                f"(bajo en {notas_acorde[max_inversion]})."
            ),
            "datos": None,
        }

    datos_inv = inversiones[inversion_solicitada]
    return {
        "valida": True,
        "mensaje": (
            f"{nombre_sol.capitalize()} válida: "
            f"{datos_inv['bajo']} en el bajo. "
            f"Notas de grave a agudo: {' - '.join(datos_inv['notas_ordenadas'])}."
        ),
        "datos": datos_inv,
    }


# ---------------------------------------------------------------------------
# 4. LÓGICA GESTUAL
# ---------------------------------------------------------------------------

# Intervalos en semitonos que identifican el tipo de una tríada
_TRIADA_POR_INTERVALOS = {
    (4, 7):  "mayor",
    (3, 7):  "menor",
    (4, 8):  "aumentado",
    (3, 6):  "disminuido",
}

def inferir_tipo_triada(notas_triada):
    """
    Dadas 3 notas latinas, infiere si forman una tríada mayor, menor,
    aumentada o disminuida calculando sus intervalos en semitonos.
    Devuelve el tipo como string, o None si no reconoce la tríada.
    """
    if len(notas_triada) < 3:
        return None
    idx = [NOTA_A_INDICE.get(n) for n in notas_triada[:3]]
    if None in idx:
        return None
    i0, i1, i2 = int(idx[0]), int(idx[1]), int(idx[2])  # type: ignore
    i1 = (i1 - i0) % 12
    i2 = (i2 - i0) % 12
    return _TRIADA_POR_INTERVALOS.get((i1, i2))


def determinar_gesto_mano_derecha(tipo_acorde, es_bemol_nota_der, notas=None):
    """
    Determina la posición, orientación y agitación de la mano derecha.

    Para tríadas simples (mayor/menor/aumentado/disminuido) el tipo viene
    directamente del acorde completo.

    Para acordes extendidos (7, m7, maj7, etc.) la mano derecha muestra la
    tríada que forman las notas 2ª-3ª-4ª del acorde. Se calcula inferiendo
    el tipo de esa tríada a partir de sus intervalos reales.

    Ejemplos:
      Do 7    (Do-Mi-Sol-Sib) → tríada der: Mi-Sol-Sib = disminuido → Cabeza ↓
      Do maj7 (Do-Mi-Sol-Si)  → tríada der: Mi-Sol-Si  = menor     → Pecho  ↓
      Sol 7   (Sol-Si-Re-Fa)  → tríada der: Si-Re-Fa   = disminuido → Cabeza ↓
      Re m7   (Re-Fa-La-Do)   → tríada der: Fa-La-Do   = mayor     → Pecho  ↑
    """
    # Tabla de gestos por tipo de tríada
    GESTOS_TRIADA = {
        "mayor":      {"altura": "Pecho",  "orientacion": "Arriba (↑)"},
        "menor":      {"altura": "Pecho",  "orientacion": "Abajo (↓)"},
        "aumentado":  {"altura": "Cabeza", "orientacion": "Arriba (↑)"},
        "disminuido": {"altura": "Cabeza", "orientacion": "Abajo (↓)"},
    }

    if tipo_acorde in TIPOS_TRIADA:
        # Tríada simple: el tipo del acorde ES el tipo de la tríada
        tipo_triada = tipo_acorde
    elif notas and len(notas) >= 5 and tipo_acorde in ("9", "m9"):
        # Acorde de novena: la tríada gestual es la 5ª-7ª-9ª (notas[2:5])
        tipo_triada = inferir_tipo_triada(notas[2:5])
        if tipo_triada is None:
            tipo_triada = "menor"  # Sol-Sib-Re siempre es menor; fallback seguro
    elif notas and len(notas) >= 4:
        # Cuatríada extendida (7, m7, maj7, dim7): tríada gestual es 3ª-5ª-7ª (notas[1:4])
        tipo_triada = inferir_tipo_triada(notas[1:4])
        if tipo_triada is None:
            tipo_triada = "mayor"  # fallback genérico
    else:
        tipo_triada = "mayor"  # fallback para casos inesperados

    gesto = GESTOS_TRIADA.get(tipo_triada, {"altura": "Pecho", "orientacion": "Arriba (↑)"})
    agitacion = "Sí (↔) — indica bemol en la nota" if es_bemol_nota_der else "No"

    return {
        "altura": gesto["altura"],
        "orientacion": gesto["orientacion"],
        "agitacion_lateral": agitacion,
        "tipo_triada_derecha": tipo_triada,
    }




def determinar_gesto_mano_izquierda(nota_fundamental):
    """
    Determina el gesto de la mano izquierda (bajo).
    """
    es_bemol = nota_es_bemol(nota_fundamental)
    nota_gesto = nota_base_para_gesto(nota_fundamental)

    if nota_gesto is None:
        return {
            "gesto": "Desconocido",
            "orientacion": "Desconocida",
            "nota": nota_fundamental,
            "nota_natural_del_gesto": None,
        }

    info_dedos = DEDOS_MAP.get(nota_gesto, {"dedos": "?", "descripcion": "Desconocido"})

    return {
        "gesto": info_dedos["descripcion"],
        "orientacion": "Abajo (↓)" if es_bemol else "Arriba (↑)",
        "nota": nota_fundamental,
        "nota_natural_del_gesto": nota_gesto,
    }


# ---------------------------------------------------------------------------
# 5. PARSEO DE ENTRADA
# ---------------------------------------------------------------------------

def parsear_nombre_acorde(nombre_acorde):
    """
    Parsea un nombre de acorde en notación latina y devuelve (fundamental, tipo).
    Ejemplos:
        "Do Mayor"      -> ("Do", "mayor")
        "Reb menor"     -> ("Reb", "menor")
        "Sol# dim7"     -> ("Lab", "dim7")  (normaliza a bemol)
        "Mi aumentado"  -> ("Mi", "aumentado")
        "Fa m7"         -> ("Fa", "m7")
        "La 7"          -> ("La", "7")
        "Sib maj7"      -> ("Sib", "maj7")
    """
    nombre = nombre_acorde.strip()

    # Mapeo de sinónimos a tipos canónicos
    sinonimos_tipo = {
        "mayor": "mayor", "may": "mayor", "maj": "mayor", "m": "menor",
        "menor": "menor", "min": "menor",
        "aumentado": "aumentado", "aum": "aumentado", "aug": "aumentado",
        "disminuido": "disminuido", "dis": "disminuido", "dim": "disminuido",
        "7": "7", "7a": "7", "septima": "7", "séptima": "7",
        "maj7": "maj7", "7m": "maj7", "7maj": "maj7",
        "m7": "m7", "min7": "m7", "menor7": "m7",
        "dim7": "dim7", "dis7": "dim7",
        "9": "9", "9a": "9", "novena": "9",
        "m9": "m9", "min9": "m9", "menor9": "m9",
    }

    # Tipos eliminados del sistema gestual (no representables con 1 bajo + 1 tríada)
    TIPOS_NO_GESTURALES = {
        "sus4", "sus2", "6", "m6", "sexta", "menor6", "min6",
        "suspendido4", "suspendido2",
    }

    # Notas posibles (ordenadas de más larga a más corta para evitar conflictos)
    notas_posibles = [
        "Solb", "Sol#", "Sol",
        "Lab", "La#", "La",
        "Sib", "Si#", "Si",
        "Dob", "Do#", "Do",
        "Reb", "Re#", "Re",
        "Mib", "Mi#", "Mi",
        "Fab", "Fa#", "Fa",
    ]

    # Normalización a la nota gestual canónica:
    # - Sostenidos -> su bemol enarmónico
    # - Bemoles que no existen gesturalmente -> su enarmónico natural
    #   · Dob = Si  (misma tecla, se expresa directamente como Si)
    #   · Fab = Mi  (misma tecla, se expresa directamente como Mi)
    #   · Mi# = Fa  (misma tecla, se expresa directamente como Fa)
    #   · Si# = Do  (misma tecla, se expresa directamente como Do)
    normalizar_a_gesto = {
        # Sostenidos → bemol equivalente
        "Do#": "Reb", "Re#": "Mib", "Fa#": "Solb",
        "Sol#": "Lab", "La#": "Sib",
        # Enarmonías sin gesto propio → nota natural directa
        "Mi#": "Fa",  "Si#": "Do",
        "Dob": "Si",  "Fab": "Mi",
    }

    fundamental = None
    resto = nombre

    for nota in notas_posibles:
        if nombre.startswith(nota):
            fundamental = nota
            resto = nombre[len(nota):].strip()
            break

    if fundamental is None:
        return None, None

    # Normalizar a nota gestual canónica
    if fundamental in normalizar_a_gesto:
        fundamental = normalizar_a_gesto[fundamental]

    # Determinar tipo de acorde
    resto_lower = resto.lower()

    if not resto_lower or resto_lower in ("mayor", "may", "maj"):
        tipo = "mayor"
    else:
        tipo = sinonimos_tipo.get(resto_lower, None)

    if tipo is None:
        # Intentar matchear parcialmente
        for clave, valor in sorted(sinonimos_tipo.items(), key=lambda x: -len(x[0])):
            if resto_lower == clave:
                tipo = valor
                break
        if tipo is None:
            # Comprobar si es un tipo eliminado del sistema gestual
            if resto_lower in TIPOS_NO_GESTURALES:
                return fundamental, f"_NO_GESTURAL_{resto_lower}"
            tipo = "mayor"  # Default

    return fundamental, tipo


# ---------------------------------------------------------------------------
# 6. FUNCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def analizar_acorde_gestual(nombre_acorde, inversion=None, observacion_manual=None):
    """
    Analiza un acorde gestual y devuelve un diccionario estructurado completo.

    Parámetros:
        nombre_acorde: str - Nombre del acorde en notación latina (ej. "Re menor", "Sib maj7")
        inversion: int o None - Inversión solicitada (0=fundamental, 1=1ª, 2=2ª, 3=3ª)
        observacion_manual: str o None - Observación personalizada (sobreescribe la automática)

    Retorna:
        dict con toda la información del acorde, gestos, notas, inversión y observaciones.
    """
    # Parsear entrada
    fundamental, tipo_acorde = parsear_nombre_acorde(nombre_acorde)

    if fundamental is None:
        return {
            "error": True,
            "mensaje": f"No se pudo interpretar el acorde: '{nombre_acorde}'",
        }

    # Tipos eliminados del sistema gestual
    if tipo_acorde and tipo_acorde.startswith("_NO_GESTURAL_"):
        tipo_pedido = tipo_acorde.replace("_NO_GESTURAL_", "")
        return {
            "error": True,
            "mensaje": (
                f"El tipo '{tipo_pedido}' no es representable en el sistema gestual. "
                f"El método solo permite 1 nota de bajo + 1 tríada en la mano derecha. "
                f"Los tipos sus4, sus2, 6 y m6 requieren notas que ninguna tríada puede "
                f"cubrir sin añadir notas ajenas al acorde."
            ),
        }

    # Calcular notas del acorde
    assert fundamental is not None  # ya comprobado arriba
    assert tipo_acorde is not None  # ya comprobado arriba

    notas = obtener_notas_acorde(fundamental, tipo_acorde)
    if notas is None:
        return {
            "error": True,
            "mensaje": f"Tipo de acorde no reconocido: '{tipo_acorde}'",
        }

    # Notación
    sufijo_latino = TIPOS_ACORDE[tipo_acorde]["sufijo"]
    sufijo_anglo = TIPOS_ACORDE[tipo_acorde]["sufijo_anglo"]
    nombre_latino = f"{fundamental} {tipo_acorde}"
    nombre_anglo = f"{nota_a_anglosajona(fundamental)}{sufijo_anglo}"

    notas_anglosajonas = [nota_a_anglosajona(n) for n in notas]

    # Gestos
    es_bemol = nota_es_bemol(fundamental)
    gesto_izq = determinar_gesto_mano_izquierda(fundamental)

    # Nota que muestra la mano derecha (fundamental para tríadas, 3ª para extendidos)
    nota_der = calcular_nota_mano_derecha(fundamental, tipo_acorde, notas)
    es_bemol_der = nota_es_bemol(nota_der)
    nota_gesto_der = nota_base_para_gesto(nota_der) or nota_der
    info_dedos_der = DEDOS_MAP.get(nota_gesto_der, {"dedos": "?", "descripcion": "Desconocido"})
    # Pasar las notas para que calcule la tríada superior real en acordes extendidos
    gesto_der = determinar_gesto_mano_derecha(tipo_acorde, es_bemol_der, notas)

    # Inversiones
    resultado_inversion = None
    if inversion is not None:
        resultado_inversion = validar_inversion(notas, inversion)

    # Observaciones
    observacion_auto = OBSERVACIONES_AUTO.get(tipo_acorde, "")
    if es_bemol:
        observacion_auto += f" Nota: {fundamental} se indica con el gesto de {BEMOL_A_NATURAL.get(fundamental, '?')} + agitación lateral."

    observacion_final = observacion_manual if observacion_manual else observacion_auto

    # Construir respuesta
    return {
        "error": False,
        "acorde": {
            "entrada_original": nombre_acorde,
            "nombre_latino": nombre_latino,
            "nombre_anglosajona": nombre_anglo,
            "fundamental": fundamental,
            "tipo": tipo_acorde,
        },
        "notas": {
            "latinas": notas,
            "anglosajonas": notas_anglosajonas,
            "num_notas": len(notas),
        },
        "mano_izquierda": {
            "funcion": "Bajo / Nota fundamental",
            "nota": gesto_izq["nota"],
            "gesto_dedos": gesto_izq["gesto"],
            "orientacion": gesto_izq["orientacion"],
            "nota_natural_gesto": gesto_izq["nota_natural_del_gesto"],
            "es_bemol": es_bemol,
        },
        "mano_derecha": {
            "funcion": "Armonía / Tipo de acorde",
            "nota": nota_der,
            "nota_natural_gesto": nota_gesto_der,
            "es_bemol": es_bemol_der,
            "gesto_dedos": info_dedos_der["descripcion"],
            "altura": gesto_der["altura"],
            "orientacion": gesto_der["orientacion"],
            "agitacion_lateral": gesto_der["agitacion_lateral"],
            "tipo_triada_derecha": gesto_der["tipo_triada_derecha"],
        },
        "inversion": resultado_inversion,
        "inversiones_posibles": calcular_inversiones_posibles(notas),
        "observaciones": {
            "automatica": observacion_auto,
            "manual": observacion_manual,
            "mostrar": observacion_final,
        },
    }


# ---------------------------------------------------------------------------
# 7. UTILIDAD DE IMPRESIÓN
# ---------------------------------------------------------------------------

def imprimir_resultado(resultado):
    """Imprime el resultado de analizar_acorde_gestual de forma legible."""
    if resultado.get("error"):
        print(f"\n[ERROR] {resultado['mensaje']}")
        return

    ac = resultado["acorde"]
    notas = resultado["notas"]
    izq = resultado["mano_izquierda"]
    der = resultado["mano_derecha"]
    inv = resultado["inversion"]
    obs = resultado["observaciones"]

    print(f"\n{'='*60}")
    print(f"  ACORDE: {ac['nombre_latino'].upper()}")
    print(f"  Anglosajona: {ac['nombre_anglosajona']}")
    print(f"{'='*60}")

    print(f"\n  Notas (latina):      {' - '.join(notas['latinas'])}")
    print(f"  Notas (anglosajona): {' - '.join(notas['anglosajonas'])}")

    print(f"\n  MANO IZQUIERDA (Bajo):")
    print(f"    Nota:        {izq['nota']}")
    print(f"    Gesto:       {izq['gesto_dedos']}")
    print(f"    Orientación: {izq['orientacion']}")
    if izq["es_bemol"]:
        print(f"    (Bemol: dedos apuntan abajo)")

    print(f"\n  MANO DERECHA (Armonía):")
    print(f"    Gesto:       {der['gesto_dedos']}")
    print(f"    Altura:      {der['altura']}")
    print(f"    Orientación: {der['orientacion']}")
    print(f"    Agitación:   {der['agitacion_lateral']}")

    if inv is not None:
        estado = "VÁLIDA" if inv["valida"] else "NO VÁLIDA"
        print(f"\n  INVERSIÓN: [{estado}]")
        print(f"    {inv['mensaje']}")

    # Mostrar todas las inversiones posibles
    print(f"\n  Inversiones posibles:")
    for idx, datos in resultado["inversiones_posibles"].items():
        print(f"    {datos['nombre']}: bajo en {datos['bajo']} → {' - '.join(datos['notas_ordenadas'])}")

    print(f"\n  OBSERVACIONES:")
    print(f"    {obs['mostrar']}")
    print()


# ---------------------------------------------------------------------------
# 8. PRUEBAS
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  MOTOR ARMÓNICO - Pruebas del sistema")
    print("=" * 60)

    # Ejemplos básicos
    ejemplos = [
        ("Do Mayor", None, None),
        ("Re menor", None, None),
        ("Mi aumentado", None, None),
        ("Fa disminuido", None, None),
        ("Sib Mayor", None, None),
        ("Reb menor", None, None),
        ("Sol 7", None, None),
        ("La m7", None, None),
        ("Si dim7", None, None),
        ("Mi maj7", None, None),
    ]

    print("\n--- ACORDES BÁSICOS ---")
    for nombre, inv, obs in ejemplos:
        resultado = analizar_acorde_gestual(nombre, inv, obs)
        imprimir_resultado(resultado)

    # Pruebas de inversiones
    print("\n--- PRUEBAS DE INVERSIONES ---")

    # Do Mayor, 1ª inversión (válida)
    resultado = analizar_acorde_gestual("Do Mayor", inversion=1)
    imprimir_resultado(resultado)

    # Do Mayor, 2ª inversión (válida)
    resultado = analizar_acorde_gestual("Do Mayor", inversion=2)
    imprimir_resultado(resultado)

    # Do Mayor, 3ª inversión (NO válida para tríada)
    resultado = analizar_acorde_gestual("Do Mayor", inversion=3)
    imprimir_resultado(resultado)

    # Sol 7, 3ª inversión (válida para cuatríada)
    resultado = analizar_acorde_gestual("Sol 7", inversion=3)
    imprimir_resultado(resultado)

    # Sol 7, 4ª inversión (NO válida)
    resultado = analizar_acorde_gestual("Sol 7", inversion=4)
    imprimir_resultado(resultado)

    # Prueba con observación manual
    print("\n--- PRUEBA CON OBSERVACIÓN MANUAL ---")
    resultado = analizar_acorde_gestual(
        "Re menor",
        inversion=1,
        observacion_manual="Ideal para practicar como ii grado en Do Mayor. Probar resolución ii-V-I."
    )
    imprimir_resultado(resultado)

    # Prueba de error
    print("\n--- PRUEBA DE ERROR ---")
    resultado = analizar_acorde_gestual("Xyz acorde raro")
    imprimir_resultado(resultado)
