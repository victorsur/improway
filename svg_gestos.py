"""
Generador SVG de gestos para el Método de Dirección Armónica Gestual.
Dibuja un cuerpo estilizado con:
  - Mano izquierda: nota del bajo (dedos arriba=natural, abajo=bemol)
  - Mano derecha:   acorde (altura pecho/cabeza, orientación, agitación lateral si bemol)
"""

# ---------------------------------------------------------------------------
# Coordenadas de referencia del cuerpo (viewBox 0 0 320 480)
# ---------------------------------------------------------------------------
# El cuerpo ocupa el centro. Referencia Y (de arriba abajo):
#   Cabeza:  top=40  center=80   bottom=120
#   Hombros: y=150
#   Pecho:   y=210
#   Cintura: y=290
#   Cadera:  y=330

CX = 160          # centro horizontal del cuerpo
Y_CABEZA_TOP = 40
Y_CABEZA_CTR = 80
Y_HOMBROS    = 150
Y_PECHO      = 210
Y_CINTURA    = 290

# Posiciones horizontales de las manos
# El director está DE FRENTE al espectador:
#   - Su mano DERECHA (armonía, verde) queda a la IZQUIERDA de la pantalla
#   - Su mano IZQUIERDA (bajo, naranja) queda a la DERECHA de la pantalla
X_MANO_DER = 55   # mano derecha del director → izquierda de la pantalla
X_MANO_IZQ = 265  # mano izquierda del director → derecha de la pantalla

# Alturas donde aparecen las manos según la lógica gestual
Y_MANO_PECHO  = Y_PECHO      # 210  — acordes mayor/menor/7/etc.
Y_MANO_CABEZA = Y_CABEZA_TOP - 20  # 20   — acordes aumentado/disminuido

# Colores
COLOR_CUERPO   = "#5B8DEF"
COLOR_MANO_IZQ = "#E67E22"   # naranja — mano izquierda (bajo)
COLOR_MANO_DER = "#27AE60"   # verde   — mano derecha (armonía)
COLOR_BEMOL    = "#E74C3C"   # rojo    — indicador de bemol / agitación
COLOR_FLECHA   = "#2C3E50"
COLOR_BG       = "#F8F9FA"
COLOR_ETIQ     = "#2C3E50"


# ---------------------------------------------------------------------------
# Primitivas SVG
# ---------------------------------------------------------------------------

def _line(x1, y1, x2, y2, color, width=2, dash=""):
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {dash_attr}/>'


def _circle(cx, cy, r, fill, stroke="none", sw=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def _rect(x, y, w, h, fill, rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="{rx}"/>'


def _text(x, y, txt, size=12, color=COLOR_ETIQ, anchor="middle", bold=False):
    weight = "bold" if bold else "normal"
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-family="sans-serif">{txt}</text>'


def _flecha_arriba(cx, cy, color=COLOR_FLECHA, size=20):
    """Triángulo apuntando hacia arriba."""
    pts = f"{cx},{cy-size} {cx-size//2},{cy} {cx+size//2},{cy}"
    return f'<polygon points="{pts}" fill="{color}"/>'


def _flecha_abajo(cx, cy, color=COLOR_FLECHA, size=20):
    """Triángulo apuntando hacia abajo."""
    pts = f"{cx},{cy+size} {cx-size//2},{cy} {cx+size//2},{cy}"
    return f'<polygon points="{pts}" fill="{color}"/>'


def _zigzag(cx, cy, color=COLOR_BEMOL, amplitud=12, pasos=4, ancho=2):
    """Línea en zigzag horizontal para indicar agitación lateral."""
    elems = []
    paso_w = amplitud / pasos * 2
    x = cx - amplitud
    for i in range(pasos * 2):
        x2 = x + paso_w
        y2 = cy + (amplitud // 3 if i % 2 == 0 else -amplitud // 3)
        elems.append(_line(x, cy if i == 0 else (cy + amplitud // 3 if (i-1) % 2 == 0 else cy - amplitud // 3),
                           x2, y2, color, ancho))
        x = x2
    return "\n".join(elems)


def _path(d, stroke, fill="none", width=2):
    return f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{width}" stroke-linecap="round"/>'


# ---------------------------------------------------------------------------
# Cuerpo estilizado
# ---------------------------------------------------------------------------

def _dibujar_cuerpo(brazo_der_levantado=False):
    partes = []
    # Cabeza (círculo)
    partes.append(_circle(CX, Y_CABEZA_CTR, 38, "none", COLOR_CUERPO, 3))
    # Ojos
    partes.append(_circle(CX - 12, Y_CABEZA_CTR - 8, 5, COLOR_CUERPO))
    partes.append(_circle(CX + 12, Y_CABEZA_CTR - 8, 5, COLOR_CUERPO))
    # Sonrisa (arco SVG)
    partes.append(_path(
        f"M {CX-14} {Y_CABEZA_CTR+8} Q {CX} {Y_CABEZA_CTR+22} {CX+14} {Y_CABEZA_CTR+8}",
        COLOR_CUERPO, "none", 2
    ))
    # Cuello
    partes.append(_line(CX, Y_CABEZA_CTR + 38, CX, Y_HOMBROS, COLOR_CUERPO, 3))
    # Tronco
    partes.append(_line(CX, Y_HOMBROS, CX, Y_CINTURA, COLOR_CUERPO, 3))
    # Hombros (línea horizontal)
    partes.append(_line(CX - 60, Y_HOMBROS, CX + 60, Y_HOMBROS, COLOR_CUERPO, 3))

    # Brazo DERECHO del director (izquierda de pantalla, X_MANO_DER=55)
    # Hombro en (CX-60=100, Y_HOMBROS=150)
    if brazo_der_levantado:
        # Codo sube y se abre, mano llega a Y_MANO_CABEZA
        codo_x, codo_y = CX - 85, Y_HOMBROS - 60   # (75, 90)
        partes.append(_line(CX - 60, Y_HOMBROS, codo_x, codo_y, COLOR_CUERPO, 3))
        partes.append(_line(codo_x, codo_y, X_MANO_DER, Y_MANO_CABEZA, COLOR_CUERPO, 3))
    else:
        partes.append(_line(CX - 60, Y_HOMBROS, CX - 80, Y_PECHO - 10, COLOR_CUERPO, 3))

    # Brazo IZQUIERDO del director (derecha de pantalla, X_MANO_IZQ=265)
    # La mano izquierda siempre queda a altura de pecho
    partes.append(_line(CX + 60, Y_HOMBROS, CX + 80, Y_PECHO - 10, COLOR_CUERPO, 3))

    # Piernas
    partes.append(_line(CX, Y_CINTURA, CX - 35, Y_CINTURA + 100, COLOR_CUERPO, 3))
    partes.append(_line(CX, Y_CINTURA, CX + 35, Y_CINTURA + 100, COLOR_CUERPO, 3))
    # Línea de referencia de pecho (punteada, sutil)
    partes.append(_line(20, Y_PECHO, 300, Y_PECHO, "#BDC3C7", 1, "6,4"))
    partes.append(_text(15, Y_PECHO + 4, "pecho", 9, "#BDC3C7", "start"))
    # Línea de referencia de cabeza (punteada, sutil)
    partes.append(_line(20, Y_CABEZA_TOP, 300, Y_CABEZA_TOP, "#BDC3C7", 1, "6,4"))
    partes.append(_text(15, Y_CABEZA_TOP - 3, "cabeza", 9, "#BDC3C7", "start"))
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Dibujo de una mano
# ---------------------------------------------------------------------------

def _dedo_seg(x1, y1, x2, y2, color, grosor=5):
    """Trazo de un dedo con extremos redondeados."""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{grosor}" stroke-linecap="round"/>')


def _pulgar_derecha_mano_derecha(nota_gesto, tipo_triada):
    """
    Decide en qué lateral debe caer el pulgar de la mano derecha del director.

    Regla anatómica:
      - En los gestos de Mi y Si, ambas manos deben "enfrentarse": los dedos
        horizontales de la mano derecha apuntan siempre hacia el centro del
        cuerpo (o hacia la cabeza si la mano está arriba). Por tanto, en
        pantalla el pulgar queda a la IZQUIERDA.
      - En el resto de gestos, menor/disminuido se representan espejados para
        mantener la palma hacia el cuerpo.

    Devuelve True si el pulgar debe quedar a la derecha de la pantalla.
    """
    if nota_gesto in ("Mi", "Si"):
        return False
    return tipo_triada in ("menor", "disminuido")


def _dibujar_dedos(cx, cy, num_dedos, color, orientacion_abajo=False,
                   es_pulgar_solo=False, es_pulgar_indice=False,
                   pulgar_derecha=False, descripcion=""):
    """
    Dibuja una mano anatómica:
      - Palma oval (elipse)
      - Dedos del mismo color que la palma, con longitudes naturales
      - Pulgar en el lateral, más corto y en ángulo
    pulgar_derecha=True → el pulgar aparece a la DERECHA en pantalla (mano izq. del director).
    """
    partes = []

    rx_p, ry_p = 12, 14    # semiejes de la palma
    grosor = 5              # grosor de los dedos
    sign = 1 if orientacion_abajo else -1   # +1 = dedos hacia abajo, -1 = hacia arriba

    # Palma ovalada
    partes.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx_p}" ry="{ry_p}" fill="{color}"/>')

    # ── Pulgar ──────────────────────────────────────────────────────────
    # Sale del lateral de la palma, más corto e inclinado hacia afuera.
    lado = 1 if pulgar_derecha else -1
    p_bx = cx + lado * rx_p           # base en el lateral de la palma
    p_by = cy + sign * 3              # ligeramente en la dirección de los dedos
    p_tx = p_bx + lado * 10           # punta lateral
    p_ty = p_by + sign * 9            # punta en la dirección de los dedos

    # ── Dedos principales (índice, medio, anular, meñique) ──────────────
    # Si pulgar a la derecha: de izq. a der. → meñique, anular, medio, índice
    # Si pulgar a la izquierda: de izq. a der. → índice, medio, anular, meñique
    # Cada tupla: (desplazamiento_x, longitud)
    if pulgar_derecha:
        layout_4 = [(-11, 19), (-4, 23), (3, 25), (10, 22)]  # meñ, anu, med, ind
        I_IND, I_MED, I_ANU, I_MEN = 3, 2, 1, 0
    else:
        layout_4 = [(-10, 22), (-3, 25), (4, 23), (11, 19)]  # ind, med, anu, meñ
        I_IND, I_MED, I_ANU, I_MEN = 0, 1, 2, 3

    # Los dedos arrancan bastante dentro del borde de la palma para que no quede hueco visual
    base_y = cy + sign * (ry_p - 7)

    def _dedo(idx):
        ox, largo = layout_4[idx]
        return _dedo_seg(cx + ox, base_y, cx + ox, base_y + sign * largo, color, grosor)

    def _pulgar():
        return _dedo_seg(p_bx, p_by, p_tx, p_ty, color, grosor)

    def _pulgar_vertical():
        """
        Pulgar vertical tipo "OK/KO": la mano rota y el pulgar apunta claramente
        hacia arriba o hacia abajo.
        """
        base_x = cx + lado * 6
        base_y_p = cy - sign * 5
        tip_x = base_x + lado * 1
        tip_y = base_y_p + sign * 22
        return _dedo_seg(base_x, base_y_p, tip_x, tip_y, color, grosor)

    def _dedo_horizontal(base_y_h, largo=22):
        """Dedo horizontal que apunta al lado opuesto del pulgar."""
        dir_h = -lado
        base_x = cx + dir_h * 1
        tip_x = base_x + dir_h * largo
        return _dedo_seg(base_x, base_y_h, tip_x, base_y_h, color, grosor)

    # ── Seleccionar qué dedos dibujar según el gesto ────────────────────
    tiene_pulgar_trio = num_dedos == 3 and "Pulgar" in descripcion

    if es_pulgar_solo:
        # La → mano rotada con pulgar vertical (OK/KO)
        partes.append(_pulgar_vertical())

    elif es_pulgar_indice:
        # Si → igual que La pero añadiendo índice horizontal tipo pistola
        partes.append(_pulgar_vertical())
        partes.append(_dedo_horizontal(cy + sign * 4, 23))

    elif tiene_pulgar_trio:
        # Mi → igual que Si, añadiendo también el dedo corazón paralelo al índice
        partes.append(_pulgar_vertical())
        partes.append(_dedo_horizontal(cy + sign * 4, 23))
        partes.append(_dedo_horizontal(cy + sign * 10, 21))

    elif num_dedos == 1:
        # Do → solo índice
        partes.append(_dedo(I_IND))

    elif num_dedos == 2:
        # Re → victoria (índice + medio, con mayor separación para formar la V)
        ox_i, l_i = layout_4[I_IND]
        ox_m, l_m = layout_4[I_MED]
        sep = 2 * lado
        partes.append(_dedo_seg(cx + ox_i + sep, base_y,
                                cx + ox_i + sep, base_y + sign * l_i, color, grosor))
        partes.append(_dedo_seg(cx + ox_m - sep, base_y,
                                cx + ox_m - sep, base_y + sign * l_m, color, grosor))

    elif num_dedos == 4:
        # Fa → índice, medio, anular, meñique (sin pulgar)
        for i in range(4):
            partes.append(_dedo(i))

    else:
        # Sol → mano abierta (5 dedos)
        partes.append(_pulgar())
        for i in range(4):
            partes.append(_dedo(i))

    return "\n".join(partes)


def _dibujar_mano(cx, cy, info_dedos, orientacion_arriba, color, agitacion=False,
                  etiqueta="", pulgar_derecha=False):
    """
    Dibuja la mano completa con flecha de orientación y, opcionalmente, zigzag de agitación.
    pulgar_derecha: orientación anatómica del pulgar (True = derecha de pantalla).
    """
    partes = []

    # Detectar forma especial
    desc = info_dedos.get("descripcion", "")
    num_dedos = info_dedos.get("dedos", 1)
    es_pulgar_solo   = "Pulgar" in desc and "Índice" not in desc and num_dedos == 1
    es_pulgar_indice = "Pulgar" in desc and "Índice" in desc and num_dedos == 2

    partes.append(_dibujar_dedos(
        cx, cy, num_dedos, color,
        orientacion_abajo=not orientacion_arriba,
        es_pulgar_solo=es_pulgar_solo,
        es_pulgar_indice=es_pulgar_indice,
        pulgar_derecha=pulgar_derecha,
        descripcion=desc,
    ))

    # Flecha de orientación — alejada de la mano para no solaparse con los dedos
    # El dedo más largo mide 25px desde base_y=(ry_p-7)=7px → punta a ~32px del centro
    offset_flecha = 50
    if orientacion_arriba:
        partes.append(_flecha_arriba(cx, cy - offset_flecha, color, 12))
    else:
        partes.append(_flecha_abajo(cx, cy + offset_flecha, color, 12))

    # Agitación lateral (zigzag rojo) si bemol
    if agitacion:
        partes.append(_zigzag(cx, cy + 20, COLOR_BEMOL, 14, 3, 2))

    # Etiqueta de nota/tipo
    if etiqueta:
        label_y = cy + 58 if orientacion_arriba else cy - 45
        partes.append(_rect(cx - 26, label_y - 14, 52, 18, color, 4))
        partes.append(_text(cx, label_y, etiqueta, 11, "white", "middle", True))

    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Función principal: genera el SVG completo
# ---------------------------------------------------------------------------

def generar_svg_acorde(resultado: dict, ancho: int = 320, alto: int = 480) -> str:
    """
    Genera un SVG completo a partir del diccionario devuelto por analizar_acorde_gestual().
    """
    if resultado.get("error"):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="80"><text x="10" y="40" fill="red" font-size="14">{resultado["mensaje"]}</text></svg>'

    izq  = resultado["mano_izquierda"]
    der  = resultado["mano_derecha"]
    ac   = resultado["acorde"]

    # --- Mano izquierda (bajo) ---
    nota_izq = izq["nota"]
    orientacion_izq_arriba = izq["orientacion"] == "Arriba (↑)"

    # Gesto de dedos: buscamos en DEDOS_MAP por la nota natural del gesto
    from motor_armonico import DEDOS_MAP
    nota_gesto_izq = izq.get("nota_natural_gesto") or nota_izq
    info_dedos_izq = DEDOS_MAP.get(nota_gesto_izq, {"dedos": 1, "descripcion": "1 dedo (Índice)"})

    # --- Mano derecha (armonía) ---
    altura_der = der["altura"]           # "Pecho" o "Cabeza"
    orientacion_der_arriba = der["orientacion"] == "Arriba (↑)"
    agitacion_der = der["agitacion_lateral"].startswith("Sí")
    # Usar la nota y gesto que calcula el motor (puede ser fundamental o 3ª)
    nota_gesto_der = der.get("nota_natural_gesto") or der.get("nota") or nota_izq
    info_dedos_der = DEDOS_MAP.get(nota_gesto_der, {"dedos": 1, "descripcion": "1 dedo (Índice)"})

    # Posición vertical de la mano derecha
    y_mano_der = Y_MANO_CABEZA if altura_der == "Cabeza" else Y_MANO_PECHO

    # Etiquetas
    tipo_acorde = ac["tipo"]
    nombre_anglo = ac["nombre_anglosajona"]

    # --- Construir SVG ---
    elements = []

    # Fondo
    elements.append(_rect(0, 0, ancho, alto, COLOR_BG, 0))

    # Título
    elements.append(_text(ancho // 2, 22, ac["nombre_latino"].upper(), 15, COLOR_ETIQ, "middle", True))
    elements.append(_text(ancho // 2, 38, nombre_anglo, 11, "#7F8C8D", "middle"))

    # Cuerpo
    elements.append(_dibujar_cuerpo(brazo_der_levantado=(altura_der == "Cabeza")))

    # Mano IZQUIERDA (bajo) — siempre a altura de pecho
    # Director de frente: su mano izquierda está a la DERECHA de pantalla → pulgar a la derecha
    elements.append(_dibujar_mano(
        cx=X_MANO_IZQ,
        cy=Y_MANO_PECHO,
        info_dedos=info_dedos_izq,
        orientacion_arriba=orientacion_izq_arriba,
        color=COLOR_MANO_IZQ,
        agitacion=False,
        etiqueta=nota_izq,
        pulgar_derecha=True,
    ))

    # Mano DERECHA (armonía) — altura variable
    # Director de frente: su mano derecha está a la IZQUIERDA de pantalla.
    # En Mi/Si los dedos horizontales deben apuntar siempre hacia el cuerpo;
    # menor/disminuido solo cambian el eje vertical (arriba/abajo).
    tipo_triada_der = der.get("tipo_triada_derecha", "mayor")
    pulgar_derecha_der = _pulgar_derecha_mano_derecha(nota_gesto_der, tipo_triada_der)
    elements.append(_dibujar_mano(
        cx=X_MANO_DER,
        cy=y_mano_der,
        info_dedos=info_dedos_der,
        orientacion_arriba=orientacion_der_arriba,
        color=COLOR_MANO_DER,
        agitacion=agitacion_der,
        etiqueta=der.get("nota", nota_izq),
        pulgar_derecha=pulgar_derecha_der,
    ))

    # Leyenda inferior
    y_leyenda = alto - 55
    elements.append(_rect(10, y_leyenda, 135, 42, "#ECF0F1", 6))
    elements.append(_circle(22, y_leyenda + 12, 7, COLOR_MANO_IZQ))
    elements.append(_text(32, y_leyenda + 16, "Mano izq: bajo", 10, COLOR_ETIQ, "start"))
    elements.append(_circle(22, y_leyenda + 30, 7, COLOR_MANO_DER))
    elements.append(_text(32, y_leyenda + 34, "Mano der: armonía", 10, COLOR_ETIQ, "start"))

    if agitacion_der:
        elements.append(_rect(155, y_leyenda, 155, 20, "#FADBD8", 6))
        elements.append(_text(163, y_leyenda + 13, "↔ Agitación = bemol", 10, COLOR_BEMOL, "start"))


    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}">
{chr(10).join(elements)}
</svg>'''
    return svg


# ---------------------------------------------------------------------------
# Test rápido en terminal
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from motor_armonico import analizar_acorde_gestual

    acordes_test = ["Do Mayor", "Re menor", "Sol aumentado", "Fa disminuido", "Sib Mayor", "La m7"]
    for nombre in acordes_test:
        resultado = analizar_acorde_gestual(nombre)
        svg = generar_svg_acorde(resultado)
        fname = f"/tmp/test_{nombre.replace(' ', '_')}.svg"
        with open(fname, "w") as f:
            f.write(svg)
        print(f"SVG generado: {fname}")
