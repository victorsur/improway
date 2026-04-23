"""
app.py — Interfaz Streamlit para el Método de Dirección Armónica Gestual
=========================================================================
Dos modos:
  1. Acorde individual: introduce un acorde y ve el gesto + datos completos.
  2. Secuencia: pide N acordes (con tonalidad opcional) y los muestra en fila.

Arrancar con:
    .venv/bin/streamlit run app.py
"""

import streamlit as st
import random

from motor_armonico import (
    analizar_acorde_gestual,
    TIPOS_ACORDE,
    NOTA_A_INDICE,
    INDICE_A_NOTA_LATINA,
    obtener_notas_acorde,
)
from svg_gestos import generar_svg_acorde

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Método Gestual Improway",
    page_icon="🎼",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOTAS_LATINAS = [
    "Do", "Reb", "Re", "Mib", "Mi", "Fa",
    "Solb", "Sol", "Lab", "La", "Sib", "Si",
]

TIPOS_DISPLAY = list(TIPOS_ACORDE.keys())

# Grados de una tonalidad mayor (intervalos en semitonos desde la tónica)
# I  II  III IV  V   VI  VII
GRADOS_MAYOR = [0, 2, 4, 5, 7, 9, 11]
TIPOS_GRADOS_MAYOR = [
    "mayor", "menor", "menor", "mayor", "mayor", "menor", "disminuido"
]

GRADOS_MENOR = [0, 2, 3, 5, 7, 8, 10]
TIPOS_GRADOS_MENOR = [
    "menor", "disminuido", "mayor", "menor", "menor", "mayor", "mayor"
]

NOMBRES_GRADOS = ["I", "II", "III", "IV", "V", "VI", "VII"]


def acordes_de_tonalidad(tonica: str, escala: str = "mayor") -> list[dict]:
    """Devuelve los 7 acordes diatónicos de una tonalidad."""
    idx_base = NOTA_A_INDICE.get(tonica, 0)
    grados   = GRADOS_MAYOR if escala == "mayor" else GRADOS_MENOR
    tipos    = TIPOS_GRADOS_MAYOR if escala == "mayor" else TIPOS_GRADOS_MENOR
    acordes  = []
    for i, (intervalo, tipo) in enumerate(zip(grados, tipos)):
        nota = INDICE_A_NOTA_LATINA[(idx_base + intervalo) % 12]
        acordes.append({
            "grado": NOMBRES_GRADOS[i],
            "nombre": f"{nota} {tipo}",
            "nota": nota,
            "tipo": tipo,
        })
    return acordes


def mostrar_tarjeta_acorde(resultado: dict, col=None):
    """Muestra el SVG y la información de un acorde en una columna."""
    target = col if col else st

    if resultado.get("error"):
        target.error(resultado["mensaje"])
        return

    ac    = resultado["acorde"]
    notas = resultado["notas"]
    izq   = resultado["mano_izquierda"]
    der   = resultado["mano_derecha"]
    obs   = resultado["observaciones"]

    svg = generar_svg_acorde(resultado)
    target.markdown(f"### {ac['nombre_latino'].upper()}")
    target.markdown(f"*{ac['nombre_anglosajona']}*")
    # st.image() no soporta SVG (usa PIL internamente). Lo inyectamos como HTML.
    import base64
    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    target.markdown(
        f'<img src="data:image/svg+xml;base64,{svg_b64}" style="width:100%;max-width:320px;display:block;margin:auto"/>',
        unsafe_allow_html=True,
    )

    with target.expander("Ver detalles del gesto"):
        target.markdown(f"**Notas:** {' — '.join(notas['latinas'])}")
        target.markdown(f"**Anglosajona:** {' — '.join(notas['anglosajonas'])}")
        target.markdown("---")
        target.markdown("**Mano izquierda (bajo)**")
        target.markdown(f"- Nota: **{izq['nota']}**")
        target.markdown(f"- Gesto: {izq['gesto_dedos']}")
        target.markdown(f"- Orientación: {izq['orientacion']}")
        target.markdown("**Mano derecha (armonía)**")
        target.markdown(f"- Nota: **{der['nota']}**")
        target.markdown(f"- Gesto: {der['gesto_dedos']}")
        target.markdown(f"- Altura: {der['altura']}")
        target.markdown(f"- Orientación: {der['orientacion']}")
        target.markdown(f"- Tríada inferida: {der['tipo_triada_derecha']}")
        if der["agitacion_lateral"].startswith("Sí"):
            target.markdown(f"- ↔ Agitación lateral activa (la nota {der['nota']} es bemol)")
        target.markdown("---")
        target.markdown(f"**Observación:** {obs['mostrar']}")

    # Inversiones posibles
    inv_posibles = resultado["inversiones_posibles"]
    filas = []
    for idx, datos in inv_posibles.items():
        filas.append({
            "Inversión": datos["nombre"],
            "Bajo": datos["bajo"],
            "Notas": " - ".join(datos["notas_ordenadas"]),
        })
    with target.expander("Inversiones posibles"):
        target.table(filas)


# ---------------------------------------------------------------------------
# UI Principal
# ---------------------------------------------------------------------------

st.title("🎼 Método Gestual Improway")
st.markdown("Visualiza los gestos manuales del **Método de Dirección Armónica**.")

tab1, tab2 = st.tabs(["Acorde individual", "Secuencia de acordes"])

# ===========================================================================
# TAB 1: Acorde individual
# ===========================================================================
with tab1:
    st.subheader("Consulta un acorde")

    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
        nota_sel = st.selectbox("Nota fundamental", NOTAS_LATINAS, key="nota_ind")

    with c2:
        tipo_sel = st.selectbox("Tipo de acorde", TIPOS_DISPLAY, key="tipo_ind")

    with c3:
        inversion_sel = st.number_input(
            "Inversión", min_value=0, max_value=4, value=0,
            help="0 = estado fundamental, 1 = 1ª inversión, etc.",
            key="inv_ind",
        )

    obs_manual = st.text_input(
        "Observación personalizada (opcional)",
        placeholder="Deja vacío para usar la automática",
        key="obs_ind",
    )

    if st.button("Mostrar gesto", type="primary", key="btn_ind"):
        nombre_acorde = f"{nota_sel} {tipo_sel}"
        resultado = analizar_acorde_gestual(
            nombre_acorde,
            inversion=int(inversion_sel),
            observacion_manual=obs_manual or None,
        )
        mostrar_tarjeta_acorde(resultado)

        # Validación de inversión prominente
        if resultado.get("inversion"):
            inv = resultado["inversion"]
            if inv["valida"]:
                st.success(f"✅ {inv['mensaje']}")
            else:
                st.warning(f"⚠️ {inv['mensaje']}")

# ===========================================================================
# TAB 2: Secuencia de acordes
# ===========================================================================
with tab2:
    st.subheader("Genera una secuencia de acordes")

    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])

    with c1:
        num_acordes = st.number_input(
            "Cantidad de acordes", min_value=1, max_value=8, value=2, key="num_seq"
        )

    with c2:
        usar_tonalidad = st.checkbox("Filtrar por tonalidad", value=False, key="usar_ton")

    tonica_seq = None
    escala_seq = "mayor"

    if usar_tonalidad:
        with c3:
            tonica_seq = st.selectbox("Tónica", NOTAS_LATINAS, key="tonica_seq")
        with c4:
            escala_seq = st.selectbox("Escala", ["mayor", "menor"], key="escala_seq")

    modo_seq = st.radio(
        "Modo de selección",
        ["Aleatorio", "Elegir manualmente"],
        horizontal=True,
        key="modo_seq",
    )

    # Si el usuario elige manualmente
    acordes_manuales = []
    if modo_seq == "Elegir manualmente":
        for i in range(int(num_acordes)):
            ca, cb = st.columns(2)
            with ca:
                n = st.selectbox(f"Acorde {i+1} — nota", NOTAS_LATINAS, key=f"nota_m_{i}")
            with cb:
                t = st.selectbox(f"Acorde {i+1} — tipo", TIPOS_DISPLAY, key=f"tipo_m_{i}")
            acordes_manuales.append(f"{n} {t}")

    if st.button("Generar secuencia", type="primary", key="btn_seq"):
        # Determinar lista de acordes
        if modo_seq == "Elegir manualmente":
            nombres_secuencia = acordes_manuales
        else:
            if usar_tonalidad and tonica_seq:
                pool = acordes_de_tonalidad(tonica_seq, escala_seq)
                elegidos = random.choices(pool, k=int(num_acordes))
                nombres_secuencia = [a["nombre"] for a in elegidos]
            else:
                # Aleatorio libre
                nombres_secuencia = [
                    f"{random.choice(NOTAS_LATINAS)} {random.choice(TIPOS_DISPLAY)}"
                    for _ in range(int(num_acordes))
                ]

        # Mostrar acordes en columnas (máx 4 por fila)
        n = int(num_acordes)
        resultados = [analizar_acorde_gestual(nombre) for nombre in nombres_secuencia]

        if n <= 4:
            cols = st.columns(n)
            for i, res in enumerate(resultados):
                mostrar_tarjeta_acorde(res, cols[i])
        else:
            # Dos filas
            fila1 = resultados[:4]
            fila2 = resultados[4:]
            cols1 = st.columns(len(fila1))
            for i, res in enumerate(fila1):
                mostrar_tarjeta_acorde(res, cols1[i])
            if fila2:
                cols2 = st.columns(len(fila2))
                for i, res in enumerate(fila2):
                    mostrar_tarjeta_acorde(res, cols2[i])

        # Resumen de la secuencia
        st.markdown("---")
        st.markdown("**Secuencia generada:**")
        resumen = " → ".join(
            res["acorde"]["nombre_latino"] if not res.get("error") else "?"
            for res in resultados
        )
        st.code(resumen)

        if usar_tonalidad and tonica_seq:
            st.info(f"Tonalidad: {tonica_seq} {escala_seq}")

st.markdown('<div style="text-align:center;color:#888;margin-top:2em;font-size:0.8em;">Recuerda que no está prohibido estudiar</div>', unsafe_allow_html=True)
