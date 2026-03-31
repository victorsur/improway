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

def _dibujar_dedos(cx, cy, num_dedos, color, orientacion_abajo=False, es_pulgar_solo=False, es_pulgar_indice=False):
    """
    Dibuja dedos estilizados como líneas que salen de la palma.
    orientacion_abajo: True = dedos apuntan abajo, False = arriba.
    """
    partes = []
    # Palma — radio mayor para mano abierta (5 dedos) para que los extremos no se confundan con el borde
    radio_palma = 18 if num_dedos == 5 else 14
    partes.append(_circle(cx, cy, radio_palma, color))

    largo = 22
    dy = largo if orientacion_abajo else -largo

    if es_pulgar_solo:
        # Solo pulgar: apunta a los lados
        partes.append(_line(cx, cy, cx - 18, cy - 8, "white", 3))
        return "\n".join(partes)

    if es_pulgar_indice:
        # Pulgar (lateral) + índice
        partes.append(_line(cx, cy, cx - 16, cy - 10, "white", 3))
        partes.append(_line(cx, cy, cx + 6, cy + dy, "white", 3))
        return "\n".join(partes)

    # Dedos normales (1 a 5): separados horizontalmente
    offsets = {
        1: [0],
        2: [-7, 7],
        3: [-10, 0, 10],
        4: [-12, -4, 4, 12],
        5: [-13, -6, 0, 6, 13],
    }
    xs = offsets.get(num_dedos, [0])
    for ox in xs:
        partes.append(_line(cx + ox, cy, cx + ox, cy + dy, "white", 3))
    return "\n".join(partes)


def _dibujar_mano(cx, cy, info_dedos, orientacion_arriba, color, agitacion=False, etiqueta=""):
    """
    Dibuja la mano completa con flecha de orientación y, opcionalmente, zigzag de agitación.
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
    ))

    # Flecha de orientación (más grande, encima/debajo de la mano)
    offset_flecha = 28
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
    elements.append(_dibujar_mano(
        cx=X_MANO_IZQ,
        cy=Y_MANO_PECHO,
        info_dedos=info_dedos_izq,
        orientacion_arriba=orientacion_izq_arriba,
        color=COLOR_MANO_IZQ,
        agitacion=False,
        etiqueta=nota_izq,
    ))

    # Mano DERECHA (armonía) — altura variable
    elements.append(_dibujar_mano(
        cx=X_MANO_DER,
        cy=y_mano_der,
        info_dedos=info_dedos_der,
        orientacion_arriba=orientacion_der_arriba,
        color=COLOR_MANO_DER,
        agitacion=agitacion_der,
        etiqueta=der.get("nota", nota_izq),
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
