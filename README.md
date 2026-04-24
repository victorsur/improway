# Método Gestual Improway

Aplicación para codificar y visualizar los gestos manuales del 
**Método de Dirección Armónica Gestual**:
un sistema de señas con las manos que permite a un director de orquesta comunicar acordes, tipos armónicos e inversiones en tiempo real.

MVP en Python/Streamlit, diseñado desde el inicio para ser portable a Flutter/Dart (Android, iOS, Web).

---

## Estructura del proyecto

```
.
├── motor_armonico.py   # Lógica central: acordes, gestos, inversiones, bemoles
├── svg_gestos.py       # Generador SVG del cuerpo y las manos del director
├── app.py              # Interfaz Streamlit (UI interactiva)
├── logica_metodo.md    # Documentación completa del método gestual
└── tests/
    ├── test_motor_armonico.py  # 196 tests de lógica armónica
    └── test_svg_gestos.py      #  59 tests del generador SVG
```

---

## El método gestual

Cada acorde se comunica con **dos manos simultáneas**:

| Mano | Función | Color en la app |
| :--- | :--- | :--- |
| Izquierda del director (derecha en pantalla) | Nota del **bajo** / fundamental | Naranja |
| Derecha del director (izquierda en pantalla) | Tipo de **armonía** / acorde | Verde |

### Configuración de dedos (ambas manos)

| Gesto | Nota |
| :--- | :--- |
| 1 dedo (índice) | Do |
| 2 dedos (victoria) | Re |
| 3 dedos (pulgar, índice, medio) | Mi |
| 4 dedos (sin pulgar) | Fa |
| Mano abierta | Sol |
| Solo pulgar | La |
| Pulgar + índice | Si |

> **Nota anatómica:** En los acordes menores y disminuidos, la mano derecha nunca se muestra con la palma hacia afuera ni con los dedos apuntando hacia el exterior del cuerpo, ya que esto sería un movimiento antinatural. En estos casos, la mano derecha se representa igual que la izquierda pero rotada 180°, con la palma hacia el cuerpo y los dedos junto al cuerpo.
>
> Para los gestos de La, Mi y Si, el pulgar se coloca hacia arriba y el dedo índice (si está presente) se representa en posición horizontal, simulando la postura natural de la mano en estos casos.

### Reglas de orientación y altura

**Mano izquierda (bajo):**
- Dedos **↑** = nota natural
- Dedos **↓** = nota bemol

**Mano derecha (armonía):**

| Altura | Orientación | Significado |
| :--- | :--- | :--- |
| Pecho | ↑ | Mayor |
| Pecho | ↓ | Menor |
| Cabeza | ↑ | Aumentado |
| Cabeza | ↓ | Disminuido |

- **Agitación lateral ↔** en la mano derecha = la nota es bemol.
- Para acordes extendidos de 4 notas (7, m7, maj7, dim7) la mano derecha muestra la **3ª del acorde** y la altura/orientación se infieren del tipo de la tríada superior.
- Para acordes de **9ª** (9, m9) la mano derecha muestra la **5ª del acorde** (tríada superior: 5ª-7ª-9ª). La 3ª queda implícita por los armónicos del bajo.

### Bemoles gesturales (solo 5)

`Reb · Mib · Solb · Lab · Sib`

Las enarmonías sin tecla negra propia (Dob, Fab, Mi#, Si#) se normalizan directamente a su nota natural equivalente.

---

## Tipos de acorde soportados

10 tipos, todos representables con el sistema de 1 bajo + 1 tríada superior:

| Tipo | Sufijo | Ejemplo (Do) |
| :--- | :--- | :--- |
| Mayor | — | Do-Mi-Sol |
| Menor | m | Do-Mib-Sol |
| Aumentado | aum / aug | Do-Mi-Lab |
| Disminuido | dim | Do-Mib-Solb |
| 7ª dominante | 7 | Do-Mi-Sol-Sib |
| 7ª mayor | maj7 | Do-Mi-Sol-Si |
| Menor 7ª | m7 | Do-Mib-Sol-Sib |
| Disminuido 7ª | dim7 | Do-Mib-Solb-La |
| 9ª | 9 | Do-Mi-Sol-Sib-Re |
| Menor 9ª | m9 | Do-Mib-Sol-Sib-Re |

> Sus4, sus2, 6 y m6 no son representables gestualmente (no generan una tríada superior canónica) y devuelven error con mensaje explicativo.

---

## Requisitos

- Python 3.10+
- Dependencias: `streamlit` (UI), `pytest` (tests)

---

## Instalación

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar (Linux/macOS)
source .venv/bin/activate

# Instalar dependencias
pip install streamlit pytest
```

---

## Ejecutar la aplicación

```bash
.venv/bin/streamlit run app.py
```

La app abre en `http://localhost:8501` y tiene dos pestañas:

- **Acorde individual** — escribe un acorde (p.ej. `Sol 7`, `Sib maj7`, `Re menor`), opcionalmente indica inversión y/o observación manual, y visualiza el SVG del director con los gestos correctos.
- **Secuencia de acordes** — genera entre 1 y 8 acordes aleatorios o manuales, con filtro opcional de tonalidad.

---

## Ejecutar los tests

```bash
# Todos los tests (255 en total)
.venv/bin/python3 -m pytest tests/ -v

# Solo lógica armónica
.venv/bin/python3 -m pytest tests/test_motor_armonico.py -v

# Solo generador SVG
.venv/bin/python3 -m pytest tests/test_svg_gestos.py -v

# Resumen compacto (sin -v)
.venv/bin/python3 -m pytest tests/
```

Resultado esperado:

```
255 passed in ~1s
```

### Qué cubre la suite

**`test_motor_armonico.py`** (196 tests):
- Integridad de tablas de datos (escala cromática, DEDOS_MAP, bemoles)
- Notas correctas para los 10 tipos de acorde
- Parseo de nombres: formatos variados, sostenidos, enarmonías
- Gestos de mano izquierda (bajo) y mano derecha (armonía)
- Inferencia de tríada superior en acordes extendidos y de 9ª
- Inversiones válidas e inválidas
- Estructura completa del diccionario de salida
- Casos de error: entradas inválidas + tipos no gesturales (sus4/sus2/6/m6)
- Tests de regresión para los casos documentados en `logica_metodo.md`

**`test_svg_gestos.py`** (59 tests):
- SVG bien formado y con dimensiones correctas
- XML válido (parseado con `xml.etree.ElementTree`)
- Nombres de acorde y notas presentes en el SVG
- Orientación correcta de manos (director de frente al espectador)
- Altura Pecho/Cabeza según tipo de acorde
- Agitación lateral (zigzag rojo) solo cuando hay bemol
- Robustez: los 10 tipos gesturales + todos los bemoles + todas las notas naturales
- Verificación de que sus4/sus2/6/m6 generan SVG de error sin excepción

---

## Próximos pasos

- Imágenes realistas de manos (reemplazar SVG esquemático)
- Exportación web (Streamlit Cloud o Flutter Web)
- Exportación móvil Android/iOS (Flutter/Dart)
- Soporte de acordes adicionales: 11ª, 13ª, add9, slash chords
- Entrada en notación anglosajona (C, Dm, G7...)
