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
    analizar_notacion_escritura,
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

    mostrar_detalles_gesto(resultado, target)

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


def mostrar_detalles_gesto(resultado: dict, target=None):
    """Muestra el bloque "Ver detalles del gesto" para cualquier resultado gestual."""
    ui = target if target else st

    notas = resultado["notas"]
    izq = resultado["mano_izquierda"]
    der = resultado["mano_derecha"]
    obs = resultado["observaciones"]

    with ui.expander("Ver detalles del gesto"):
        ui.markdown(f"**Notas:** {' — '.join(notas['latinas'])}")
        ui.markdown(f"**Anglosajona:** {' — '.join(notas['anglosajonas'])}")
        ui.markdown("---")
        ui.markdown("**Mano izquierda (bajo)**")
        ui.markdown(f"- Nota: **{izq['nota']}**")
        ui.markdown(f"- Gesto: {izq['gesto_dedos']}")
        ui.markdown(f"- Orientación: {izq['orientacion']}")
        ui.markdown("**Mano derecha (armonía)**")
        ui.markdown(f"- Nota: **{der['nota']}**")
        ui.markdown(f"- Gesto: {der['gesto_dedos']}")
        ui.markdown(f"- Altura: {der['altura']}")
        ui.markdown(f"- Orientación: {der['orientacion']}")
        ui.markdown(f"- Tríada inferida: {der['tipo_triada_derecha']}")
        if der["agitacion_lateral"].startswith("Sí"):
            ui.markdown(f"- ↔ Agitación lateral activa (la nota {der['nota']} es bemol)")
        ui.markdown("---")
        ui.markdown(f"**Observación:** {obs['mostrar']}")


# ---------------------------------------------------------------------------
# UI Principal
# ---------------------------------------------------------------------------

st.title("🎼 Método Gestual Improway")
st.markdown("Visualiza los gestos manuales del **Método de Dirección Armónica**.")

tab1, tab2, tab3 = st.tabs(["Acorde individual", "Secuencia de acordes", "Escritura de acordes"])

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

# ===========================================================================
# TAB 3: Escritura de acordes
# ===========================================================================
with tab3:
    st.subheader("Escritura de acordes")
    st.caption("Selecciona el tipo de acorde y escribe grado superior + bajo en campos separados.")

    c_sup, c_bajo = st.columns(2)
    with c_sup:
        c_signo, c_grado = st.columns([1, 3])
        with c_signo:
            simbolo_sup = st.selectbox(
                "Tipo",
                ["+", "-", "↑", "↓"],
                index=0,
                key="esc_tipo_sup",
                help=" + mayor, - menor, ↑ aumentado, ↓ disminuido",
            )
            st.caption("'+' mayor, '-' menor, '↑' aumentado, '↓' disminuido")
        with c_grado:
            grado_sup = st.text_input(
                "Parte superior (grado: 1..7 y b opcional)",
                value="1",
                key="esc_grado_sup",
                placeholder="Ej: 1, 3, 3b, 7",
            )

        superior_txt = f"{simbolo_sup}{(grado_sup or '').strip().lower()}"
    with c_bajo:
        bajo_txt = st.text_input(
            "Bajo (ej: 1, 2, 3b)",
            value="1",
            key="esc_bajo",
        )

    if st.button("Mostrar escritura", type="primary", key="btn_esc"):
        resultado = analizar_notacion_escritura(superior_txt, bajo_txt)
        if resultado.get("error"):
            st.error(resultado["mensaje"])
        else:
            notacion = resultado["notacion"]
            acorde = resultado["acorde"]

            st.markdown("### Notacion")
            st.markdown(
                (
                    '<div style="max-width:220px;margin:0 auto 1rem auto;text-align:center;">'
                    f'<div style="font-size:2rem;font-weight:700;line-height:1.1;">{notacion["superior"]}</div>'
                    '<div style="border-top:2px solid #2C3E50;margin:0.35rem 0 0.45rem 0;"></div>'
                    f'<div style="font-size:2rem;font-weight:700;line-height:1.1;">{notacion["bajo"]}</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

            st.markdown(f"**{acorde['nombre_completo']}**")

            svg = generar_svg_acorde(resultado["resultado_gestual"])
            import base64
            svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{svg_b64}" style="width:100%;max-width:320px;display:block;margin:auto"/>',
                unsafe_allow_html=True,
            )

            mostrar_detalles_gesto(resultado["resultado_gestual"])

st.markdown('<div style="text-align:center;color:#888;margin-top:2em;font-size:0.8em;">Recuerda que no está prohibido estudiar</div>', unsafe_allow_html=True)
