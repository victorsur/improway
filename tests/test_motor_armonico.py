"""
Tests para motor_armonico.py
============================
Cubre:
  1. Escala y tablas de datos (NOTA_A_INDICE, DEDOS_MAP, BEMOL_A_NATURAL)
  2. Obtención de notas por tipo de acorde
  3. Normalización de enarmonías y sostenidos en el parseo
  4. Parseo de nombres de acorde (formatos varios)
  5. Gestos de mano izquierda (bajo)
  6. Gestos de mano derecha — tríadas y acordes extendidos
  7. Inferencia de tipo de tríada superior
  8. Inversiones (válidas e inválidas)
  9. Función principal analizar_acorde_gestual — estructura de salida
 10. Casos de error y entradas inválidas
"""

import pytest
import sys
import os

# Aseguramos que el módulo raíz es importable desde tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor_armonico import (
    NOTA_A_INDICE,
    DEDOS_MAP,
    BEMOL_A_NATURAL,
    TIPOS_ACORDE,
    TIPOS_TRIADA,
    obtener_notas_acorde,
    nota_es_bemol,
    nota_base_para_gesto,
    nota_a_anglosajona,
    calcular_nota_mano_derecha,
    inferir_tipo_triada,
    determinar_gesto_mano_derecha,
    determinar_gesto_mano_izquierda,
    calcular_inversiones_posibles,
    validar_inversion,
    parsear_nombre_acorde,
    analizar_acorde_gestual,
)


# ---------------------------------------------------------------------------
# 1. Tablas de datos
# ---------------------------------------------------------------------------

class TestTablasDatos:
    def test_escala_cromatica_12_notas(self):
        """La escala canónica debe tener exactamente 12 índices únicos (0-11)."""
        indices = set(NOTA_A_INDICE[n] for n in ["Do", "Reb", "Re", "Mib", "Mi", "Fa",
                                                   "Solb", "Sol", "Lab", "La", "Sib", "Si"])
        assert indices == set(range(12))

    def test_dedos_map_cubre_7_notas_naturales(self):
        """DEDOS_MAP debe contener entrada para todas las notas naturales."""
        naturales = {"Do", "Re", "Mi", "Fa", "Sol", "La", "Si"}
        assert naturales.issubset(set(DEDOS_MAP.keys()))

    def test_bemol_a_natural_solo_5_bemoles(self):
        """Solo existen 5 bemoles gesturales: Reb, Mib, Solb, Lab, Sib."""
        assert set(BEMOL_A_NATURAL.keys()) == {"Reb", "Mib", "Solb", "Lab", "Sib"}

    def test_bemol_a_natural_valores_son_naturales(self):
        """Los valores en BEMOL_A_NATURAL deben ser notas naturales con gesto propio."""
        for natural in BEMOL_A_NATURAL.values():
            assert natural in DEDOS_MAP

    def test_tipos_triada_son_subconjunto_de_tipos_acorde(self):
        assert TIPOS_TRIADA.issubset(set(TIPOS_ACORDE.keys()))

    def test_10_tipos_de_acorde(self):
        """sus4, sus2, 6 y m6 han sido eliminados: quedan 10 tipos."""
        assert len(TIPOS_ACORDE) == 10

    def test_tipos_eliminados_no_en_tipos_acorde(self):
        """Los tipos no gesturales no deben estar en TIPOS_ACORDE."""
        for tipo in ("sus4", "sus2", "6", "m6"):
            assert tipo not in TIPOS_ACORDE, f"'{tipo}' debería haber sido eliminado"


# ---------------------------------------------------------------------------
# 2. Notas de acordes
# ---------------------------------------------------------------------------

class TestObtenerNotasAcorde:
    @pytest.mark.parametrize("fundamental,tipo,esperadas", [
        ("Do",  "mayor",      ["Do", "Mi", "Sol"]),
        ("Do",  "menor",      ["Do", "Mib", "Sol"]),
        ("Do",  "aumentado",  ["Do", "Mi", "Lab"]),
        ("Do",  "disminuido", ["Do", "Mib", "Solb"]),
        ("Do",  "7",          ["Do", "Mi", "Sol", "Sib"]),
        ("Do",  "maj7",       ["Do", "Mi", "Sol", "Si"]),
        ("Do",  "m7",         ["Do", "Mib", "Sol", "Sib"]),
        ("Do",  "dim7",       ["Do", "Mib", "Solb", "La"]),
        ("Sol", "7",          ["Sol", "Si", "Re", "Fa"]),
        ("Re",  "m7",         ["Re", "Fa", "La", "Do"]),
        ("La",  "dim7",       ["La", "Do", "Mib", "Solb"]),
        ("Sib", "maj7",       ["Sib", "Re", "Fa", "La"]),
        ("Do",  "9",          ["Do", "Mi", "Sol", "Sib", "Re"]),
        ("Do",  "m9",         ["Do", "Mib", "Sol", "Sib", "Re"]),
    ])
    def test_notas_correctas(self, fundamental, tipo, esperadas):
        notas = obtener_notas_acorde(fundamental, tipo)
        assert notas == esperadas, f"{fundamental} {tipo}: {notas} != {esperadas}"

    def test_fundamental_invalida_devuelve_none(self):
        assert obtener_notas_acorde("X", "mayor") is None

    def test_tipo_invalido_devuelve_none(self):
        assert obtener_notas_acorde("Do", "fusion") is None


# ---------------------------------------------------------------------------
# 3. Funciones auxiliares de notas
# ---------------------------------------------------------------------------

class TestAuxiliaresNotas:
    @pytest.mark.parametrize("nota,esperado", [
        ("Reb", True), ("Mib", True), ("Solb", True), ("Lab", True), ("Sib", True),
        ("Do", False), ("Re", False), ("Mi", False), ("Si", False), ("Fa", False),
    ])
    def test_nota_es_bemol(self, nota, esperado):
        assert nota_es_bemol(nota) == esperado

    @pytest.mark.parametrize("nota,esperado", [
        ("Reb", "Re"), ("Mib", "Mi"), ("Solb", "Sol"), ("Lab", "La"), ("Sib", "Si"),
        ("Do", "Do"), ("Sol", "Sol"), ("La", "La"),
    ])
    def test_nota_base_para_gesto(self, nota, esperado):
        assert nota_base_para_gesto(nota) == esperado

    @pytest.mark.parametrize("latina,anglo", [
        ("Do", "C"), ("Reb", "Db"), ("Re", "D"), ("Mib", "Eb"), ("Mi", "E"),
        ("Fa", "F"), ("Solb", "Gb"), ("Sol", "G"), ("Lab", "Ab"), ("La", "A"),
        ("Sib", "Bb"), ("Si", "B"),
    ])
    def test_nota_a_anglosajona(self, latina, anglo):
        assert nota_a_anglosajona(latina) == anglo


# ---------------------------------------------------------------------------
# 4. Parseo de nombres de acorde
# ---------------------------------------------------------------------------

class TestParseoNombreAcorde:
    @pytest.mark.parametrize("entrada,fund_esp,tipo_esp", [
        # Formatos normales
        ("Do Mayor",    "Do",  "mayor"),
        ("Do mayor",    "Do",  "mayor"),
        ("Do",          "Do",  "mayor"),   # sin sufijo = mayor por defecto
        ("Re menor",    "Re",  "menor"),
        ("Mi m",        "Mi",  "menor"),
        ("Fa 7",        "Fa",  "7"),
        ("Sol maj7",    "Sol", "maj7"),
        ("La m7",       "La",  "m7"),
        ("Sib dim7",    "Sib", "dim7"),
        ("Do aumentado","Do",  "aumentado"),
        ("Do aum",      "Do",  "aumentado"),
        ("Do aug",      "Do",  "aumentado"),
        ("Fa disminuido","Fa", "disminuido"),
        ("Fa dim",      "Fa",  "disminuido"),
        ("Do 9",        "Do",  "9"),
        ("Do m9",       "Do",  "m9"),
        # Bemoles válidos
        ("Reb Mayor",   "Reb", "mayor"),
        ("Mib menor",   "Mib", "menor"),
        ("Solb 7",      "Solb","7"),
        ("Lab m7",      "Lab", "m7"),
        ("Sib maj7",    "Sib", "maj7"),
    ])
    def test_parseo_normal(self, entrada, fund_esp, tipo_esp):
        fund, tipo = parsear_nombre_acorde(entrada)
        assert fund == fund_esp, f"'{entrada}': fundamental {fund!r} != {fund_esp!r}"
        assert tipo == tipo_esp, f"'{entrada}': tipo {tipo!r} != {tipo_esp!r}"

    @pytest.mark.parametrize("entrada,fund_esp", [
        # Sostenidos → normalizados a bemol
        ("Do# Mayor",  "Reb"),
        ("Re# menor",  "Mib"),
        ("Fa# 7",      "Solb"),
        ("Sol# m7",    "Lab"),
        ("La# Mayor",  "Sib"),
        # Enarmonías sin gesto → nota natural
        ("Mi# Mayor",  "Fa"),
        ("Si# Mayor",  "Do"),
        ("Dob Mayor",  "Si"),
        ("Fab Mayor",  "Mi"),
    ])
    def test_normalizacion_enarmonias(self, entrada, fund_esp):
        fund, _ = parsear_nombre_acorde(entrada)
        assert fund == fund_esp, f"'{entrada}': esperado {fund_esp!r}, obtenido {fund!r}"

    def test_entrada_invalida_devuelve_none(self):
        fund, tipo = parsear_nombre_acorde("XYZ nada")
        assert fund is None
        assert tipo is None


# ---------------------------------------------------------------------------
# 5. Gesto mano izquierda
# ---------------------------------------------------------------------------

class TestGestoManoIzquierda:
    @pytest.mark.parametrize("nota,ori_esp,gesto_esp", [
        ("Do",  "Arriba (↑)", "1 dedo (Índice)"),
        ("Re",  "Arriba (↑)", "2 dedos (Victoria)"),
        ("Mi",  "Arriba (↑)", "3 dedos (Pulgar, Índice, Medio)"),
        ("Fa",  "Arriba (↑)", "4 dedos (Índice, Medio, Anular, Meñique)"),
        ("Sol", "Arriba (↑)", "Mano abierta (5 dedos)"),
        ("La",  "Arriba (↑)", "1 dedo (Pulgar)"),
        ("Si",  "Arriba (↑)", "2 dedos (Pulgar + Índice)"),
    ])
    def test_notas_naturales_orientacion_arriba(self, nota, ori_esp, gesto_esp):
        g = determinar_gesto_mano_izquierda(nota)
        assert g["orientacion"] == ori_esp
        assert g["gesto"] == gesto_esp
        assert g["es_bemol"] is False if "es_bemol" in g else True  # campo opcional

    @pytest.mark.parametrize("nota,nota_natural_esp", [
        ("Reb", "Re"), ("Mib", "Mi"), ("Solb", "Sol"), ("Lab", "La"), ("Sib", "Si"),
    ])
    def test_bemoles_orientacion_abajo(self, nota, nota_natural_esp):
        g = determinar_gesto_mano_izquierda(nota)
        assert g["orientacion"] == "Abajo (↓)"
        assert g["nota_natural_del_gesto"] == nota_natural_esp

    def test_nota_devuelta_es_la_original(self):
        """La mano izquierda devuelve la nota original (incluso si es bemol)."""
        g = determinar_gesto_mano_izquierda("Sib")
        assert g["nota"] == "Sib"


# ---------------------------------------------------------------------------
# 6. Inferencia de tipo de tríada superior
# ---------------------------------------------------------------------------

class TestInferirTipoTriada:
    @pytest.mark.parametrize("notas,tipo_esp", [
        (["Do", "Mi", "Sol"],   "mayor"),
        (["Do", "Mib", "Sol"],  "menor"),
        (["Do", "Mi", "Lab"],   "aumentado"),
        (["Do", "Mib", "Solb"], "disminuido"),
        # Tríadas superiores de acordes extendidos
        (["Mi", "Sol", "Sib"],  "disminuido"),   # Do 7
        (["Mi", "Sol", "Si"],   "menor"),         # Do maj7
        (["Si", "Re", "Fa"],    "disminuido"),    # Sol 7
        (["Fa", "La", "Do"],    "mayor"),         # Re m7
        (["Do", "Mib", "Solb"], "disminuido"),    # La dim7
        (["Re", "Fa", "La"],    "menor"),         # Sib maj7
    ])
    def test_inferir_triada(self, notas, tipo_esp):
        resultado = inferir_tipo_triada(notas)
        assert resultado == tipo_esp, f"{notas}: {resultado!r} != {tipo_esp!r}"

    def test_lista_corta_devuelve_none(self):
        assert inferir_tipo_triada(["Do", "Mi"]) is None

    def test_nota_invalida_devuelve_none(self):
        assert inferir_tipo_triada(["Do", "XX", "Sol"]) is None


# ---------------------------------------------------------------------------
# 7. Gestos mano derecha — altura y orientación
# ---------------------------------------------------------------------------

class TestGestoManoDerecha:
    @pytest.mark.parametrize("tipo,altura_esp,ori_esp", [
        ("mayor",      "Pecho",  "Arriba (↑)"),
        ("menor",      "Pecho",  "Abajo (↓)"),
        ("aumentado",  "Cabeza", "Arriba (↑)"),
        ("disminuido", "Cabeza", "Abajo (↓)"),
    ])
    def test_triadas_simples(self, tipo, altura_esp, ori_esp):
        g = determinar_gesto_mano_derecha(tipo, False)
        assert g["altura"] == altura_esp
        assert g["orientacion"] == ori_esp
        assert g["agitacion_lateral"] == "No"

    @pytest.mark.parametrize("nombre_acorde,altura_esp,ori_esp,triada_esp", [
        ("Do 7",    "Cabeza", "Abajo (↓)",  "disminuido"),
        ("Do maj7", "Pecho",  "Abajo (↓)",  "menor"),
        ("Sol 7",   "Cabeza", "Abajo (↓)",  "disminuido"),
        ("Re m7",   "Pecho",  "Arriba (↑)", "mayor"),
        ("La dim7", "Cabeza", "Abajo (↓)",  "disminuido"),
        ("Sib maj7","Pecho",  "Abajo (↓)",  "menor"),
    ])
    def test_acordes_extendidos_via_analizar(self, nombre_acorde, altura_esp, ori_esp, triada_esp):
        """Verifica altura/orientación/triada de la mano derecha en acordes extendidos."""
        r = analizar_acorde_gestual(nombre_acorde)
        assert not r.get("error"), f"Error al analizar '{nombre_acorde}': {r.get('mensaje')}"
        der = r["mano_derecha"]
        assert der["altura"] == altura_esp, f"{nombre_acorde} altura: {der['altura']!r}"
        assert der["orientacion"] == ori_esp, f"{nombre_acorde} ori: {der['orientacion']!r}"
        assert der["tipo_triada_derecha"] == triada_esp, f"{nombre_acorde} triada: {der['tipo_triada_derecha']!r}"

    def test_agitacion_lateral_activa_cuando_bemol(self):
        g = determinar_gesto_mano_derecha("mayor", True)
        assert g["agitacion_lateral"].startswith("Sí")

    def test_agitacion_lateral_inactiva_cuando_natural(self):
        g = determinar_gesto_mano_derecha("mayor", False)
        assert g["agitacion_lateral"] == "No"


# ---------------------------------------------------------------------------
# 8. Nota de la mano derecha (fundamental vs 3ª)
# ---------------------------------------------------------------------------

class TestCalcularNotaManoDerecha:
    @pytest.mark.parametrize("fundamental,tipo,nota_esp", [
        # Tríadas: mano derecha = fundamental
        ("Do", "mayor",      "Do"),
        ("Re", "menor",      "Re"),
        ("Mi", "aumentado",  "Mi"),
        ("Fa", "disminuido", "Fa"),
        # Cuatríadas extendidas: mano derecha = notas[1] (3ª del acorde)
        ("Do", "7",    "Mi"),
        ("Do", "maj7", "Mi"),
        ("Do", "m7",   "Mib"),
        ("Re", "m7",   "Fa"),
        ("Sol","7",    "Si"),
        ("Sib","maj7", "Re"),
        ("La", "dim7", "Do"),
        # Novenas: mano derecha = notas[2] (5ª del acorde)
        ("Do", "9",    "Sol"),
        ("Do", "m9",   "Sol"),
        ("Re", "9",    "La"),
        ("Sol","9",    "Re"),
    ])
    def test_nota_mano_derecha(self, fundamental, tipo, nota_esp):
        notas = obtener_notas_acorde(fundamental, tipo)
        resultado = calcular_nota_mano_derecha(fundamental, tipo, notas)
        assert resultado == nota_esp, f"{fundamental} {tipo}: {resultado!r} != {nota_esp!r}"


# ---------------------------------------------------------------------------
# 9. Inversiones
# ---------------------------------------------------------------------------

class TestInversiones:
    def test_inversiones_posibles_triada(self):
        notas = ["Do", "Mi", "Sol"]
        inv = calcular_inversiones_posibles(notas)
        assert len(inv) == 3
        assert inv[0]["bajo"] == "Do"
        assert inv[1]["bajo"] == "Mi"
        assert inv[2]["bajo"] == "Sol"

    def test_inversiones_posibles_cuatriada(self):
        notas = ["Sol", "Si", "Re", "Fa"]
        inv = calcular_inversiones_posibles(notas)
        assert len(inv) == 4
        assert inv[3]["bajo"] == "Fa"

    def test_inversion_valida_primera(self):
        r = validar_inversion(["Do", "Mi", "Sol"], 1)
        assert r["valida"] is True
        assert r["datos"]["bajo"] == "Mi"
        assert "1ª inversión" in r["mensaje"].lower()

    def test_inversion_valida_segunda(self):
        r = validar_inversion(["Do", "Mi", "Sol"], 2)
        assert r["valida"] is True
        assert r["datos"]["bajo"] == "Sol"

    def test_inversion_invalida_tercera_en_triada(self):
        r = validar_inversion(["Do", "Mi", "Sol"], 3)
        assert r["valida"] is False
        assert "3ª inversión" in r["mensaje"]
        assert "tríada" in r["mensaje"]

    def test_inversion_invalida_negativa(self):
        r = validar_inversion(["Do", "Mi", "Sol"], -1)
        assert r["valida"] is False

    def test_inversion_fundamental_siempre_valida(self):
        r = validar_inversion(["Do", "Mi", "Sol"], 0)
        assert r["valida"] is True
        assert r["datos"]["bajo"] == "Do"

    def test_inversion_via_analizar(self):
        r = analizar_acorde_gestual("Do Mayor", inversion=1)
        assert r["inversion"]["valida"] is True
        assert r["inversion"]["datos"]["bajo"] == "Mi"

    def test_inversion_invalida_via_analizar(self):
        r = analizar_acorde_gestual("Do Mayor", inversion=5)
        assert r["inversion"]["valida"] is False


# ---------------------------------------------------------------------------
# 10. Función principal — estructura de salida
# ---------------------------------------------------------------------------

class TestAnalizarAcordeGestual:
    def test_estructura_completa(self):
        r = analizar_acorde_gestual("Re menor")
        assert r["error"] is False
        # Secciones principales
        for seccion in ["acorde", "notas", "mano_izquierda", "mano_derecha",
                        "inversion", "inversiones_posibles", "observaciones"]:
            assert seccion in r, f"Falta sección '{seccion}'"

    def test_acorde_nombres(self):
        r = analizar_acorde_gestual("Re menor")
        assert r["acorde"]["fundamental"] == "Re"
        assert r["acorde"]["tipo"] == "menor"
        assert r["acorde"]["nombre_anglosajona"] == "Dm"

    def test_notas_latinas_y_anglosajonas(self):
        r = analizar_acorde_gestual("Do Mayor")
        assert r["notas"]["latinas"] == ["Do", "Mi", "Sol"]
        assert r["notas"]["anglosajonas"] == ["C", "E", "G"]
        assert r["notas"]["num_notas"] == 3

    def test_mano_izquierda_campos(self):
        r = analizar_acorde_gestual("Sol 7")
        izq = r["mano_izquierda"]
        for campo in ["nota", "gesto_dedos", "orientacion", "nota_natural_gesto", "es_bemol"]:
            assert campo in izq, f"Falta campo '{campo}' en mano_izquierda"
        assert izq["nota"] == "Sol"
        assert izq["es_bemol"] is False

    def test_mano_derecha_campos(self):
        r = analizar_acorde_gestual("Sol 7")
        der = r["mano_derecha"]
        for campo in ["nota", "nota_natural_gesto", "es_bemol", "gesto_dedos",
                      "altura", "orientacion", "agitacion_lateral", "tipo_triada_derecha"]:
            assert campo in der, f"Falta campo '{campo}' en mano_derecha"

    def test_observacion_automatica_presente(self):
        r = analizar_acorde_gestual("Do Mayor")
        obs = r["observaciones"]
        assert obs["automatica"]
        assert obs["mostrar"]
        assert obs["manual"] is None

    def test_observacion_manual_sobreescribe(self):
        r = analizar_acorde_gestual("Do Mayor", observacion_manual="Mi nota personalizada")
        assert r["observaciones"]["mostrar"] == "Mi nota personalizada"
        assert r["observaciones"]["manual"] == "Mi nota personalizada"

    def test_inversion_none_cuando_no_se_pide(self):
        r = analizar_acorde_gestual("Do Mayor")
        assert r["inversion"] is None

    def test_bemol_en_fundamental_activa_agitacion_derecha(self):
        r = analizar_acorde_gestual("Sib Mayor")
        assert r["mano_izquierda"]["es_bemol"] is True
        assert r["mano_derecha"]["agitacion_lateral"].startswith("Sí")

    def test_nota_natural_activa_sin_agitacion(self):
        r = analizar_acorde_gestual("Do Mayor")
        assert r["mano_izquierda"]["es_bemol"] is False
        assert r["mano_derecha"]["agitacion_lateral"] == "No"

    @pytest.mark.parametrize("nombre", [
        "Do Mayor", "Re menor", "Mi aumentado", "Fa disminuido",
        "Sol 7", "La maj7", "Si m7", "Reb Mayor", "Mib menor",
        "Solb 7", "Lab m7", "Sib maj7", "Do dim7", "Re 9", "Do m9",
    ])
    def test_todos_los_acordes_basicos_sin_error(self, nombre):
        r = analizar_acorde_gestual(nombre)
        assert r.get("error") is False, f"Error inesperado en '{nombre}': {r.get('mensaje')}"


# ---------------------------------------------------------------------------
# 11. Casos de error y entradas inválidas
# ---------------------------------------------------------------------------

class TestErrores:
    def test_acorde_vacio(self):
        r = analizar_acorde_gestual("")
        assert r.get("error") is True

    def test_acorde_completamente_invalido(self):
        r = analizar_acorde_gestual("XYZ fusion")
        assert r.get("error") is True
        assert "mensaje" in r

    def test_error_contiene_mensaje_util(self):
        r = analizar_acorde_gestual("Foo bar")
        assert len(r["mensaje"]) > 0

    def test_nota_invalida_en_inferir_triada(self):
        assert inferir_tipo_triada(["Do", "XX", "Sol"]) is None

    def test_obtener_notas_fundamental_invalida(self):
        assert obtener_notas_acorde("H", "mayor") is None

    def test_obtener_notas_tipo_invalido(self):
        assert obtener_notas_acorde("Do", "inventado") is None

    @pytest.mark.parametrize("nombre", [
        "Do sus4", "Re sus2", "Mi 6", "Sol m6",
    ])
    def test_tipos_no_gesturales_devuelven_error(self, nombre):
        """sus4, sus2, 6 y m6 no son representables gestualmente: deben devolver error."""
        r = analizar_acorde_gestual(nombre)
        assert r.get("error") is True, f"'{nombre}' debería devolver error pero no lo hizo"
        assert "mensaje" in r
        assert len(r["mensaje"]) > 0


# ---------------------------------------------------------------------------
# 12. Casos de regresión específicos del método
# ---------------------------------------------------------------------------

class TestRegresion:
    """Casos concretos documentados en logica_metodo.md que no deben romperse."""

    def test_do_7_triada_superior_disminuido(self):
        r = analizar_acorde_gestual("Do 7")
        assert r["notas"]["latinas"] == ["Do", "Mi", "Sol", "Sib"]
        assert r["mano_derecha"]["tipo_triada_derecha"] == "disminuido"
        assert r["mano_derecha"]["altura"] == "Cabeza"
        assert r["mano_derecha"]["orientacion"] == "Abajo (↓)"

    def test_do_maj7_triada_superior_menor(self):
        r = analizar_acorde_gestual("Do maj7")
        assert r["notas"]["latinas"] == ["Do", "Mi", "Sol", "Si"]
        assert r["mano_derecha"]["tipo_triada_derecha"] == "menor"
        assert r["mano_derecha"]["altura"] == "Pecho"

    def test_re_m7_triada_superior_mayor(self):
        r = analizar_acorde_gestual("Re m7")
        assert r["notas"]["latinas"] == ["Re", "Fa", "La", "Do"]
        assert r["mano_derecha"]["tipo_triada_derecha"] == "mayor"
        assert r["mano_derecha"]["altura"] == "Pecho"
        assert r["mano_derecha"]["orientacion"] == "Arriba (↑)"

    def test_sol_7_triada_superior_disminuido(self):
        r = analizar_acorde_gestual("Sol 7")
        assert r["notas"]["latinas"] == ["Sol", "Si", "Re", "Fa"]
        assert r["mano_derecha"]["tipo_triada_derecha"] == "disminuido"
        assert r["mano_derecha"]["altura"] == "Cabeza"

    def test_la_dim7_triada_superior_disminuido(self):
        r = analizar_acorde_gestual("La dim7")
        assert r["mano_derecha"]["tipo_triada_derecha"] == "disminuido"
        assert r["mano_derecha"]["altura"] == "Cabeza"

    def test_sib_maj7_triada_superior_menor(self):
        r = analizar_acorde_gestual("Sib maj7")
        assert r["mano_derecha"]["tipo_triada_derecha"] == "menor"
        assert r["mano_derecha"]["altura"] == "Pecho"

    def test_dob_se_normaliza_a_si(self):
        fund, tipo = parsear_nombre_acorde("Dob Mayor")
        assert fund == "Si"

    def test_fab_se_normaliza_a_mi(self):
        fund, tipo = parsear_nombre_acorde("Fab menor")
        assert fund == "Mi"

    def test_mi_sostenido_se_normaliza_a_fa(self):
        fund, tipo = parsear_nombre_acorde("Mi# Mayor")
        assert fund == "Fa"

    def test_si_sostenido_se_normaliza_a_do(self):
        fund, tipo = parsear_nombre_acorde("Si# Mayor")
        assert fund == "Do"

    def test_do_mayor_triada_mano_derecha_igual_fundamental(self):
        """En tríadas, la mano derecha muestra la fundamental (mismo gesto que izquierda)."""
        r = analizar_acorde_gestual("Do Mayor")
        assert r["mano_derecha"]["nota"] == r["mano_izquierda"]["nota"]

    def test_inversiones_posibles_do_mayor(self):
        r = analizar_acorde_gestual("Do Mayor")
        inv = r["inversiones_posibles"]
        assert inv[0]["bajo"] == "Do"
        assert inv[1]["bajo"] == "Mi"
        assert inv[2]["bajo"] == "Sol"
        assert 3 not in inv  # tríada: máximo 3 inversiones (0,1,2)

    def test_do_9_mano_derecha_es_quinta(self):
        """Do 9: notas = [Do, Mi, Sol, Sib, Re] → mano derecha = Sol (notas[2])."""
        r = analizar_acorde_gestual("Do 9")
        assert not r.get("error"), f"Error inesperado: {r.get('mensaje')}"
        assert r["notas"]["latinas"] == ["Do", "Mi", "Sol", "Sib", "Re"]
        assert r["mano_derecha"]["nota"] == "Sol"

    def test_do_9_triada_superior_menor(self):
        """Do 9: tríada superior Sol-Sib-Re → menor → Pecho ↓."""
        r = analizar_acorde_gestual("Do 9")
        assert r["mano_derecha"]["tipo_triada_derecha"] == "menor"
        assert r["mano_derecha"]["altura"] == "Pecho"
        assert r["mano_derecha"]["orientacion"] == "Abajo (↓)"

    def test_do_m9_mano_derecha_es_quinta(self):
        """Do m9: notas = [Do, Mib, Sol, Sib, Re] → mano derecha = Sol (notas[2])."""
        r = analizar_acorde_gestual("Do m9")
        assert not r.get("error"), f"Error inesperado: {r.get('mensaje')}"
        assert r["notas"]["latinas"] == ["Do", "Mib", "Sol", "Sib", "Re"]
        assert r["mano_derecha"]["nota"] == "Sol"

    def test_do_m9_triada_superior_menor(self):
        """Do m9: tríada superior Sol-Sib-Re → menor → Pecho ↓."""
        r = analizar_acorde_gestual("Do m9")
        assert r["mano_derecha"]["tipo_triada_derecha"] == "menor"
        assert r["mano_derecha"]["altura"] == "Pecho"
        assert r["mano_derecha"]["orientacion"] == "Abajo (↓)"
