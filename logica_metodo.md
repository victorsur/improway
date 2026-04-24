# Método de Dirección Armónica Gestual

Este documento describe la lógica de codificación para la dirección de orquestas e improvisación mediante señas manuales.

---

## 1. Coordenadas Espaciales (Eje Y)
La altura de las manos respecto al cuerpo define la cualidad de la tríada:
* **Altura del Pecho:** Acordes de tríada mayor/menor y extensiones cuya tríada superior es mayor o menor (7, maj7, m7, 9, m9, etc.).
* **Encima de la Cabeza:** Acordes cuya tríada superior es aumentada o disminuida (aumentado, disminuido, dim7, y la mayoría de los dominantes 7).

## 2. Orientación de los Dedos (Vectores)
La dirección hacia la que apuntan los dedos define la modalidad o alteración de la nota.

Ambas manos usan **exactamente la misma configuración de dedos** (ver sección 3). La diferencia está en lo que significa la orientación en cada mano:

### Mano Izquierda (Bajo / Nota fundamental)
* **Hacia Arriba (↑):** Nota natural.
* **Hacia Abajo (↓):** Nota bemol (b).
* **Sin agitación lateral** — la mano izquierda nunca agita.
* Ejemplos:
    * 2 dedos (Victoria) ↑ = **Re**
    * 2 dedos (Victoria) ↓ = **Reb**
    * Pulgar ↑ = **La**
    * Pulgar ↓ = **Lab**

### Mano Derecha (Armonía / Tipo de acorde)
* **Hacia Arriba (↑):** Acorde Mayor (en pecho) o Aumentado (en cabeza).
* **Hacia Abajo (↓):** Acorde Menor (en pecho) o Disminuido (en cabeza).
* **Agitación Lateral (↔):** La nota que muestra la mano derecha es bemol. Se combina con cualquier orientación ↑ o ↓.

> **Nota anatómica:** En los acordes menores y disminuidos, la mano derecha nunca se muestra con la palma hacia afuera ni con los dedos apuntando hacia el exterior del cuerpo, ya que esto sería un movimiento antinatural. En estos casos, la mano derecha se representa igual que la izquierda pero rotada 180°, con la palma hacia el cuerpo y los dedos junto al cuerpo.
>
> **Regla visual específica para Mi y Si en la mano derecha:** cuando la armonía se representa con gesto de **Mi** (pulgar + índice + medio) o **Si** (pulgar + índice), la mano derecha se dibuja siempre como si ambas manos se "enfrentaran". En pantalla, los dedos horizontales apuntan siempre **hacia el centro del cuerpo del director**; si la mano está sobre la cabeza (acorde disminuido o tríada superior disminuida), siguen apuntando hacia la cabeza/cuerpo. En los acordes menores y disminuidos **solo cambia el eje vertical** (la mano se pone boca abajo), pero **no** el lateral: el pulgar queda en el lado exterior y los dedos hacia el interior.

* Ejemplos:
    * 2 dedos ↑ en pecho = **Re Mayor**
    * 2 dedos ↑ en pecho + agitación ↔ = **Reb Mayor**
    * 2 dedos ↓ en pecho + agitación ↔ = **Reb menor**

#### Nota mostrada por la mano derecha

La nota que gesticula la mano derecha varía según la complejidad del acorde:

* **Tríadas** (mayor, menor, aumentado, disminuido): muestra la **fundamental** — el mismo gesto que la mano izquierda. La orientación y la altura describen el tipo.
  * Ejemplo: Do Mayor → izq = Do, der = Do (pecho ↑)

* **Cuatríadas extendidas** (7, m7, maj7, dim7): muestra la **3ª del acorde** (notas[1]). Esa nota encabeza la tríada superior (3ª-5ª-7ª) que "rellena" el acorde sobre el bajo.
  * Ejemplo: Re m7 (Re-Fa-La-Do) → izq = Re, der = Fa (porque Fa-La-Do forma la tríada superior)

* **Acordes de 9ª** (9, m9): muestra la **5ª del acorde** (notas[2]). Esa nota encabeza la tríada superior (5ª-7ª-9ª). La 3ª queda implícita por los armónicos del bajo.
  * Ejemplo: Do 9 (Do-Mi-Sol-Sib-Re) → izq = Do, der = Sol (porque Sol-Sib-Re forma la tríada superior menor → Pecho ↓)

#### Inferencia del tipo de acorde para extendidos

La altura y orientación de la mano derecha en acordes extendidos **no** se determinan por el nombre del acorde, sino por el **tipo de la tríada superior**, calculado a partir de sus intervalos reales:

| Tríada superior | Altura | Orientación |
| :--- | :--- | :--- |
| Mayor | Pecho | ↑ |
| Menor | Pecho | ↓ |
| Aumentado | Cabeza | ↑ |
| Disminuido | Cabeza | ↓ |

Ejemplos verificados:
| Acorde | Notas | Tríada superior | Resultado der |
| :--- | :--- | :--- | :--- |
| Do 7 | Do-Mi-Sol-Sib | Mi-Sol-Sib = **disminuido** | Cabeza ↓ |
| Do maj7 | Do-Mi-Sol-Si | Mi-Sol-Si = **menor** | Pecho ↓ |
| Sol 7 | Sol-Si-Re-Fa | Si-Re-Fa = **disminuido** | Cabeza ↓ |
| Re m7 | Re-Fa-La-Do | Fa-La-Do = **mayor** | Pecho ↑ |
| Do 9 | Do-Mi-Sol-Sib-Re | Sol-Sib-Re = **menor** | Pecho ↓ |
| Do m9 | Do-Mib-Sol-Sib-Re | Sol-Sib-Re = **menor** | Pecho ↓ |

## 3. Configuración de Dedos
| Dedos | Forma | Nota / Acorde |
| :--- | :--- | :--- |
| 1 dedo (Índice) | Índice extendido | Do |
| 2 dedos (Victoria) | Índice + Medio en V | Re |
| 3 dedos (Pulgar, Índice, Medio) | Tres dedos abiertos | Mi |
| 4 dedos (Índice, Medio, Anular, Meñique) | Sin pulgar | Fa |
| 5 dedos (Mano completa) | Mano abierta | Sol |
| 1 dedo (Pulgar) | Solo pulgar | La |
| 2 dedos (Pulgar + Índice) | Pulgar e índice | Si |

> **Detalle anatómico:** Para los gestos de La, Mi y Si, el pulgar se coloca hacia arriba y el dedo índice (si está presente) se representa en posición horizontal, simulando la postura natural de la mano en estos casos.
>
> En la **mano derecha**, los gestos de **Mi** y **Si** conservan siempre ese apuntamiento horizontal hacia el centro del cuerpo. Por eso, en acordes como **Mi Mayor / Mi menor / Mi disminuido** y **Si Mayor / Si menor / Si disminuido**, así como en extendidos donde la mano derecha muestra **Mi** o **Si** (por ejemplo `Do 7` o `Sol 7`), la imagen debe verse como el reflejo especular de la postura antinatural hacia afuera.

## 4. Tabla de Correspondencia Rápida
| Posición | Orientación | Significado Armónico |
| :--- | :--- | :--- |
| Pecho | Arriba (↑) | Mayor |
| Pecho | Abajo (↓) | Menor |
| Cabeza | Arriba (↑) | Aumentado |
| Cabeza | Abajo (↓) | Disminuido |

---

## 5. Gestión de Bemoles

Los bemoles se expresan gestualmente de dos formas distintas según la mano:

### Mano Izquierda (Bajo)
- Los dedos apuntan **hacia abajo (↓)** para indicar que la nota es bemol.
- La mano izquierda **nunca agita** — la orientación de los dedos es la única señal.
- Ejemplo: Pulgar + Índice ↑ = Si / Pulgar + Índice ↓ = Sib.

### Mano Derecha (Acorde)
- Se añade **agitación lateral (↔)** para indicar que la fundamental del acorde es bemol.
- La agitación se combina con la orientación ↑ o ↓ y con la altura (pecho/cabeza).
- Ejemplo: 2 dedos (Victoria) ↑ en pecho = Re Mayor / ídem + agitación ↔ = Reb Mayor.

### Tabla de equivalencias bemoles
| Bemol | Nota natural del gesto | Mano izquierda | Mano derecha |
| :--- | :--- | :--- | :--- |
| Reb | Re | 2 dedos (Victoria) ↓ | 2 dedos (Victoria) + ↔ |
| Mib | Mi | 3 dedos ↓ | 3 dedos + ↔ |
| Solb | Sol | Mano abierta ↓ | Mano abierta + ↔ |
| Lab | La | Pulgar ↓ | Pulgar + ↔ |
| Sib | Si | Pulgar + Índice ↓ | Pulgar + Índice + ↔ |

### Enarmonías excluidas del sistema gestual

Algunas notas tienen nombre de bemol o sostenido pero **comparten tecla con una nota natural**. En este método se expresan directamente con el gesto de esa nota natural, sin bemol ni agitación:

| Nombre teórico | Se expresa como | Motivo |
| :--- | :--- | :--- |
| Dob | **Si** | Misma tecla. Gesto de Si (Pulgar + Índice) ↑, sin agitación. |
| Fab | **Mi** | Misma tecla. Gesto de Mi (3 dedos) ↑, sin agitación. |
| Mi# | **Fa** | Misma tecla. Gesto de Fa (4 dedos) ↑, sin agitación. |
| Si# | **Do** | Misma tecla. Gesto de Do (Índice) ↑, sin agitación. |

> **Regla general:** si un bemol no tiene tecla negra propia en el piano (Dob, Fab) o un sostenido tampoco (Mi#, Si#), se usa directamente el nombre y gesto de la nota natural equivalente.

---

## 6. Tipos de Acordes Soportados

El motor armónico soporta **10 tipos de acorde**, todos representables con el sistema de 1 bajo + 1 tríada superior:

| Tipo | Intervalos (semitonos) | Ejemplo (Do) | Notación Anglo |
| :--- | :--- | :--- | :--- |
| Mayor | 0-4-7 | Do-Mi-Sol | C |
| Menor | 0-3-7 | Do-Mib-Sol | Cm |
| Aumentado | 0-4-8 | Do-Mi-Lab | Caug |
| Disminuido | 0-3-6 | Do-Mib-Solb | Cdim |
| 7ª dominante | 0-4-7-10 | Do-Mi-Sol-Sib | C7 |
| 7ª mayor | 0-4-7-11 | Do-Mi-Sol-Si | Cmaj7 |
| Menor 7ª | 0-3-7-10 | Do-Mib-Sol-Sib | Cm7 |
| Disminuido 7ª | 0-3-6-9 | Do-Mib-Solb-La | Cdim7 |
| 9ª | 0-4-7-10-14 | Do-Mi-Sol-Sib-Re | C9 |
| Menor 9ª | 0-3-7-10-14 | Do-Mib-Sol-Sib-Re | Cm9 |

### Tipos no gesturales (eliminados del sistema)

Los siguientes tipos **no pueden representarse** con la estructura de 1 nota de bajo + 1 tríada superior porque no tienen una tríada de 3 notas que encabece la segunda mano de forma unívoca:

| Tipo eliminado | Motivo |
| :--- | :--- |
| Sus4 (0-5-7) | La tríada implícita Fa-Sol no es una tríada estándar de 3 notas con tercera. |
| Sus2 (0-2-7) | Ídem: Re-Sol no forma una tríada canónica. |
| 6ª (0-4-7-9) | La nota añadida (6ª) no genera una tríada superior identificable. |
| Menor 6ª (0-3-7-9) | Ídem. |

Solicitar cualquiera de estos tipos devuelve un error con un mensaje explicativo.

---

## 7. Inversiones

Una inversión cambia qué nota del acorde se coloca en el bajo (la más grave).

### Reglas
- **Estado fundamental (inversión 0):** La fundamental está en el bajo.
- **1ª inversión:** La 3ª del acorde en el bajo.
- **2ª inversión:** La 5ª del acorde en el bajo.
- **3ª inversión:** Solo para acordes de 4+ notas (la 7ª en el bajo).

### Validación
El sistema valida automáticamente si la inversión solicitada es posible:
- Una **tríada** (3 notas) admite inversiones 0, 1 y 2.
- Una **cuatríada** (4 notas) admite inversiones 0, 1, 2 y 3.
- Solicitar una inversión imposible devuelve un mensaje específico.

### Ejemplo: Do Mayor
| Inversión | Bajo | Notas (grave a agudo) |
| :--- | :--- | :--- |
| Fundamental | Do | Do - Mi - Sol |
| 1ª inversión | Mi | Mi - Sol - Do |
| 2ª inversión | Sol | Sol - Do - Mi |

### Ejemplo: Sol7
| Inversión | Bajo | Notas (grave a agudo) |
| :--- | :--- | :--- |
| Fundamental | Sol | Sol - Si - Re - Fa |
| 1ª inversión | Si | Si - Re - Fa - Sol |
| 2ª inversión | Re | Re - Fa - Sol - Si |
| 3ª inversión | Fa | Fa - Sol - Si - Re |

### Mensajes de validación
- Inversión válida: `"1ª inversión válida: Mi en el bajo. Notas de grave a agudo: Mi - Sol - Do."`
- Inversión no válida: `"No existe 3ª inversión para una tríada. Máximo: 2ª inversión (bajo en Sol)."`

---

## 8. Notación Anglosajona

El sistema mantiene la correspondencia entre notación latina y anglosajona:

| Latina | Anglosajona |
| :--- | :--- |
| Do | C |
| Reb | Db |
| Re | D |
| Mib | Eb |
| Mi | E |
| Fa | F |
| Solb | Gb |
| Sol | G |
| Lab | Ab |
| La | A |
| Sib | Bb |
| Si | B |

La salida del motor incluye siempre ambas notaciones para cada acorde y sus notas.

---

## 9. Observaciones Didácticas

El sistema genera observaciones automáticas para cada tipo de acorde:
- Describen la sonoridad y el uso armónico típico.
- Para notas bemol, se incluye una nota sobre el gesto correspondiente.
- Las observaciones pueden ser **sobreescritas** manualmente pasando `observacion_manual` a la función.

---

## 10. Estructura de Salida

La función `analizar_acorde_gestual()` devuelve un diccionario con esta estructura:

```python
{
    "error": False,
    "acorde": {
        "entrada_original": "Re menor",
        "nombre_latino": "Re menor",
        "nombre_anglosajona": "Dm",
        "fundamental": "Re",
        "tipo": "menor",
    },
    "notas": {
        "latinas": ["Re", "Fa", "La"],
        "anglosajonas": ["D", "F", "A"],
        "num_notas": 3,
    },
    "mano_izquierda": {
        "funcion": "Bajo / Nota fundamental",
        "nota": "Re",
        "gesto_dedos": "2 dedos (Victoria)",
        "orientacion": "Arriba (↑)",
        "nota_natural_gesto": "Re",
        "es_bemol": False,
    },
    "mano_derecha": {
        "funcion": "Armonía / Tipo de acorde",
        "nota": "Re",
        "nota_natural_gesto": "Re",
        "es_bemol": False,
        "gesto_dedos": "2 dedos (Victoria)",
        "altura": "Pecho",
        "orientacion": "Abajo (↓)",
        "agitacion_lateral": "No",
        "tipo_triada_derecha": "menor",  # para tríadas = tipo del propio acorde; para extendidos = tipo de la tríada superior
    },
    "inversion": {  # None si no se solicita
        "valida": True,
        "mensaje": "1ª inversión válida: Fa en el bajo...",
        "datos": {"nombre": "1ª inversión", "bajo": "Fa", "notas_ordenadas": [...]},
    },
    "inversiones_posibles": {
        0: {"nombre": "Estado fundamental", "bajo": "Re", "notas_ordenadas": [...]},
        1: {"nombre": "1ª inversión", "bajo": "Fa", "notas_ordenadas": [...]},
        2: {"nombre": "2ª inversión", "bajo": "La", "notas_ordenadas": [...]},
    },
    "observaciones": {
        "automatica": "Acorde menor: sonoridad oscura...",
        "manual": None,  # o texto personalizado
        "mostrar": "...",  # la que se muestra (manual si existe, si no auto)
    },
}
```

---

## 11. Extensibilidad y Portabilidad

### Futuras extensiones previstas
- **Acordes adicionales:** 11ª, 13ª, add9, etc. Solo requiere añadir entradas a `TIPOS_ACORDE`.
- **Notación anglosajona como entrada:** Parsear "Cm7" además de "Do m7".
- **Bajo diferente de la fundamental:** Acordes como Do/Mi (slash chords).

### Exportación multiplataforma
La estructura de diccionario de la salida facilita la conversión directa a:
- **JSON** para APIs web o almacenamiento.
- **Dart/Flutter** para apps Android/iOS/Windows (mapas y listas equivalentes).
- **Bases de datos** para catálogos de acordes.

El archivo `motor_armonico.py` actúa como la fuente de verdad de la lógica, que se puede portar o consumir desde cualquier entorno.
