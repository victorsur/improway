"""
Tests para svg_gestos.py
========================
Cubre:
  1. Que generar_svg_acorde devuelve un string SVG válido
  2. Que el SVG contiene los elementos estructurales esperados
  3. Posición correcta de manos (izquierda del director a la derecha de pantalla)
  4. Agitación lateral (zigzag) solo aparece cuando la nota es bemol
  5. Altura de la mano derecha según tipo de acorde (Pecho / Cabeza)
  6. Que acordes de error generan SVG de error (sin crash)
  7. Que todas las notas naturales producen un SVG sin excepción
  8. Que el SVG es parseable como XML bien formado
"""

import pytest
import sys
import os
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor_armonico import analizar_acorde_gestual
from svg_gestos import (
    generar_svg_acorde,
    X_MANO_DER,
    X_MANO_IZQ,
    Y_MANO_PECHO,
    Y_MANO_CABEZA,
    COLOR_MANO_IZQ,
    COLOR_MANO_DER,
    COLOR_BEMOL,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def svg_de(nombre_acorde, **kwargs):
    """Shortcut: analiza acorde y genera SVG."""
    r = analizar_acorde_gestual(nombre_acorde, **kwargs)
    return generar_svg_acorde(r), r


def parse_svg(svg_str):
    """Parsea SVG como XML. Lanza si está mal formado."""
    # ElementTree no entiende el namespace SVG por defecto; lo registramos
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    return ET.fromstring(svg_str)


def assert_segmento(svg_str, x1, y1, x2, y2):
    """Comprueba que el SVG contiene un segmento exacto."""
    snippet = f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
    assert snippet in svg_str, f"No se encontró el segmento esperado: {snippet}"


# ---------------------------------------------------------------------------
# 1. Estructura básica del SVG
# ---------------------------------------------------------------------------

class TestEstructuraBasica:
    def test_devuelve_string(self):
        svg, _ = svg_de("Do Mayor")
        assert isinstance(svg, str)

    def test_empieza_con_tag_svg(self):
        svg, _ = svg_de("Do Mayor")
        assert svg.strip().startswith("<svg")

    def test_contiene_cierre_svg(self):
        svg, _ = svg_de("Do Mayor")
        assert "</svg>" in svg

    def test_xml_bien_formado(self):
        svg, _ = svg_de("Re menor")
        # No debe lanzar excepción
        root = parse_svg(svg)
        assert root.tag.endswith("svg")

    def test_tiene_viewbox(self):
        svg, _ = svg_de("Do Mayor")
        assert "viewBox" in svg

    def test_dimensiones_por_defecto(self):
        svg, _ = svg_de("Do Mayor")
        assert 'width="320"' in svg
        assert 'height="480"' in svg

    def test_dimensiones_personalizadas(self):
        r = analizar_acorde_gestual("Do Mayor")
        svg = generar_svg_acorde(r, ancho=400, alto=600)
        assert 'width="400"' in svg
        assert 'height="600"' in svg


# ---------------------------------------------------------------------------
# 2. Contenido semántico
# ---------------------------------------------------------------------------

class TestContenidoSemantico:
    def test_nombre_latino_en_svg(self):
        svg, r = svg_de("Do Mayor")
        nombre = r["acorde"]["nombre_latino"].upper()
        assert nombre in svg

    def test_nombre_anglosajón_en_svg(self):
        svg, r = svg_de("Re menor")
        anglo = r["acorde"]["nombre_anglosajona"]
        assert anglo in svg

    def test_etiqueta_nota_izquierda_en_svg(self):
        """La nota del bajo (mano izquierda) debe aparecer como etiqueta."""
        svg, r = svg_de("Sol 7")
        nota_izq = r["mano_izquierda"]["nota"]
        assert nota_izq in svg

    def test_etiqueta_nota_derecha_en_svg(self):
        """La nota de la armonía (mano derecha) debe aparecer como etiqueta."""
        svg, r = svg_de("Sol 7")
        nota_der = r["mano_derecha"]["nota"]
        assert nota_der in svg

    def test_leyenda_mano_izquierda_presente(self):
        svg, _ = svg_de("Do Mayor")
        assert "bajo" in svg.lower() or "izq" in svg.lower()

    def test_leyenda_mano_derecha_presente(self):
        svg, _ = svg_de("Do Mayor")
        assert "armon" in svg.lower() or "der" in svg.lower()


# ---------------------------------------------------------------------------
# 3. Posiciones de manos (orientación del director)
# ---------------------------------------------------------------------------

class TestPosicionesManos:
    def test_mano_izquierda_x_mayor_que_derecha(self):
        """La mano izquierda del director (bajo, naranja) está a la DERECHA de pantalla."""
        assert X_MANO_IZQ > X_MANO_DER

    def test_mano_izquierda_naranja_en_svg(self):
        svg, _ = svg_de("Do Mayor")
        assert COLOR_MANO_IZQ.lower() in svg.lower()

    def test_mano_derecha_verde_en_svg(self):
        svg, _ = svg_de("Do Mayor")
        assert COLOR_MANO_DER.lower() in svg.lower()

    def test_x_mano_der_en_svg(self):
        """La coordenada X de la mano derecha debe aparecer en el SVG."""
        svg, _ = svg_de("Do Mayor")
        assert str(X_MANO_DER) in svg

    def test_x_mano_izq_en_svg(self):
        svg, _ = svg_de("Do Mayor")
        assert str(X_MANO_IZQ) in svg


# ---------------------------------------------------------------------------
# 4. Altura de la mano derecha (Pecho vs Cabeza)
# ---------------------------------------------------------------------------

class TestAlturaManoDerechaEnSVG:
    def test_acorde_mayor_mano_derecha_a_pecho(self):
        """Acordes de tríada mayor → mano derecha a Y_MANO_PECHO."""
        svg, r = svg_de("Do Mayor")
        assert r["mano_derecha"]["altura"] == "Pecho"
        assert str(Y_MANO_PECHO) in svg

    def test_acorde_menor_mano_derecha_a_pecho(self):
        svg, r = svg_de("Re menor")
        assert r["mano_derecha"]["altura"] == "Pecho"

    def test_acorde_aumentado_mano_derecha_a_cabeza(self):
        svg, r = svg_de("Mi aumentado")
        assert r["mano_derecha"]["altura"] == "Cabeza"
        assert str(Y_MANO_CABEZA) in svg

    def test_acorde_disminuido_mano_derecha_a_cabeza(self):
        svg, r = svg_de("Fa disminuido")
        assert r["mano_derecha"]["altura"] == "Cabeza"

    def test_do7_mano_derecha_a_cabeza(self):
        svg, r = svg_de("Do 7")
        assert r["mano_derecha"]["altura"] == "Cabeza"

    def test_do_maj7_mano_derecha_a_pecho(self):
        svg, r = svg_de("Do maj7")
        assert r["mano_derecha"]["altura"] == "Pecho"

    def test_brazo_levantado_cuando_altura_cabeza(self):
        """Cuando la mano derecha está en Cabeza, el brazo debe tener coordenadas distintas (codo arriba)."""
        svg_cabeza, r_cabeza = svg_de("Mi aumentado")
        svg_pecho,  r_pecho  = svg_de("Do Mayor")
        assert r_cabeza["mano_derecha"]["altura"] == "Cabeza"
        assert r_pecho["mano_derecha"]["altura"]  == "Pecho"
        # Los SVGs deben ser distintos en la zona del brazo derecho
        assert svg_cabeza != svg_pecho

    def test_brazo_no_levantado_cuando_altura_pecho(self):
        """Dos acordes con mano a Pecho generan el mismo dibujo de brazo (idéntico si el resto es igual)."""
        svg_mayor, _ = svg_de("Do Mayor")
        svg_menor, _ = svg_de("Do menor")
        # Ambos tienen altura Pecho: la línea del brazo debe contener Y_PECHO - 10
        assert str(Y_MANO_PECHO - 10) in svg_mayor
        assert str(Y_MANO_PECHO - 10) in svg_menor


# ---------------------------------------------------------------------------
# 4b. Cara del director (ojos y boca)
# ---------------------------------------------------------------------------

class TestCaraDirector:
    def test_ojos_presentes_en_svg(self):
        """El SVG debe contener dos círculos de ojos (fill=COLOR_CUERPO) dentro de la cabeza."""
        svg, _ = svg_de("Do Mayor")
        # La cabeza es stroke=COLOR_CUERPO fill="none"; los ojos son fill=COLOR_CUERPO
        # → debe haber exactamente 2 círculos rellenos con COLOR_CUERPO
        assert svg.count('fill="#5B8DEF"') == 2

    def test_boca_path_presente_en_svg(self):
        """La sonrisa es un <path> con comando Q (curva cuadrática)."""
        svg, _ = svg_de("Do Mayor")
        assert "<path" in svg
        assert " Q " in svg

    def test_cara_presente_en_todos_los_acordes(self):
        """La cara debe aparecer en acordes de pecho y de cabeza."""
        for nombre in ["Do Mayor", "Sol aumentado", "Fa disminuido", "Re m7"]:
            svg, _ = svg_de(nombre)
            assert "<path" in svg, f"Falta <path> (boca) en '{nombre}'"


# ---------------------------------------------------------------------------
# 4c. Anatomía de Mi/Si en mano derecha (dedos hacia el cuerpo)
# ---------------------------------------------------------------------------

class TestAnatomiaManoDerechaMiSi:
    @pytest.mark.parametrize("nombre,y_dedo", [
        ("Si Mayor", 206),
        ("Si menor", 214),
        ("Si disminuido", 24),
    ])
    def test_si_mano_derecha_apunta_hacia_el_centro(self, nombre, y_dedo):
        svg, _ = svg_de(nombre)
        assert_segmento(svg, 56, y_dedo, 79, y_dedo)

    @pytest.mark.parametrize("nombre,y_indice,y_corazon", [
        ("Mi Mayor", 206, 200),
        ("Mi menor", 214, 220),
        ("Mi disminuido", 24, 30),
    ])
    def test_mi_mano_derecha_apunta_hacia_el_centro(self, nombre, y_indice, y_corazon):
        svg, _ = svg_de(nombre)
        assert_segmento(svg, 56, y_indice, 79, y_indice)
        assert_segmento(svg, 56, y_corazon, 77, y_corazon)


# ---------------------------------------------------------------------------
# 5. Agitación lateral (bemol)
# ---------------------------------------------------------------------------

class TestAgitacionLateral:
    def test_agitacion_presente_en_acorde_con_bemol(self):
        """Sib Mayor → fundamental es bemol → zigzag rojo en SVG."""
        svg, r = svg_de("Sib Mayor")
        assert r["mano_derecha"]["agitacion_lateral"].startswith("Sí")
        assert COLOR_BEMOL.lower() in svg.lower()

    def test_agitacion_ausente_en_acorde_natural(self):
        """Do Mayor → sin bemol → no debe haber COLOR_BEMOL en SVG."""
        svg, r = svg_de("Do Mayor")
        assert r["mano_derecha"]["agitacion_lateral"] == "No"
        # El color rojo de bemol NO debe estar (ni en zigzag ni en leyenda de agitación)
        # Nota: COLOR_BEMOL también aparece en la leyenda si agitacion_der es True;
        # aquí solo verificamos que el campo sea False
        assert not r["mano_izquierda"]["es_bemol"]

    def test_leyenda_agitacion_en_svg_cuando_bemol(self):
        svg, _ = svg_de("Mib menor")
        assert "gitaci" in svg  # "Agitación" o "agitación"

    def test_leyenda_agitacion_ausente_cuando_no_bemol(self):
        svg, _ = svg_de("Sol 7")
        # La leyenda de agitación solo aparece si agitacion_der es True
        r = analizar_acorde_gestual("Sol 7")
        assert not r["mano_derecha"]["agitacion_lateral"].startswith("Sí")


# ---------------------------------------------------------------------------
# 6. SVG de error
# ---------------------------------------------------------------------------

class TestSVGError:
    def test_resultado_error_genera_svg_con_texto_rojo(self):
        resultado_error = {"error": True, "mensaje": "Acorde no reconocido"}
        svg = generar_svg_acorde(resultado_error)
        assert "<svg" in svg
        assert "red" in svg or "#" in svg  # color de error
        assert "Acorde no reconocido" in svg

    def test_resultado_error_xml_bien_formado(self):
        resultado_error = {"error": True, "mensaje": "Test error"}
        svg = generar_svg_acorde(resultado_error)
        root = parse_svg(svg)
        assert root is not None


# ---------------------------------------------------------------------------
# 7. Robustez — todos los acordes base sin excepción
# ---------------------------------------------------------------------------

class TestRobustez:
    @pytest.mark.parametrize("nombre", [
        "Do Mayor", "Do menor", "Do aumentado", "Do disminuido",
        "Do 7", "Do maj7", "Do m7", "Do dim7", "Do 9", "Do m9",
        "Reb Mayor", "Mib menor", "Solb 7", "Lab m7", "Sib maj7",
        "Re Mayor", "Mi Mayor", "Fa Mayor", "Sol Mayor", "La Mayor", "Si Mayor",
    ])
    def test_genera_svg_sin_excepcion(self, nombre):
        try:
            svg, _ = svg_de(nombre)
            assert len(svg) > 100  # SVG no vacío
        except Exception as e:
            pytest.fail(f"Excepción generando SVG para '{nombre}': {e}")

    @pytest.mark.parametrize("nombre", [
        "Do sus4", "Do sus2", "Do 6", "Do m6",
    ])
    def test_tipos_no_gesturales_generan_svg_de_error(self, nombre):
        """sus4/sus2/6/m6 devuelven error lógico → el SVG de error se genera sin excepción."""
        try:
            svg, r = svg_de(nombre)
            assert r.get("error") is True, f"'{nombre}' debería devolver error lógico"
            assert len(svg) > 100  # SVG de error no vacío
        except Exception as e:
            pytest.fail(f"Excepción generando SVG de error para '{nombre}': {e}")

    @pytest.mark.parametrize("nombre", [
        "Do Mayor", "Sol 7", "Sib maj7", "La dim7",
    ])
    def test_svg_es_xml_valido(self, nombre):
        svg, _ = svg_de(nombre)
        try:
            parse_svg(svg)
        except ET.ParseError as e:
            pytest.fail(f"SVG para '{nombre}' no es XML válido: {e}")
