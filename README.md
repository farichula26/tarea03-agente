# Agente seguidor de líneas

Simulador de un **agente reflejo simple** que sigue líneas oscuras en una malla de N×M celdas generada al azar.
Es la implementación de la *Tarea 3. Diseño de Agentes* ([enunciado en PDF](informe/)): el programa permite
ejecutar el agente paso a paso, ver qué regla y qué caso usa en cada celda, y obtener los datos para responder
las preguntas del informe (reglas usadas, choques, avances, rotaciones, desempeño y bucle infinito).

La lógica del agente (`agent/`) está separada de la interfaz gráfica en Tkinter (`ui/`). Todo el código usa solo
funciones, sin clases.

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Ejecución](#ejecución)
4. [Cómo usar el simulador](#cómo-usar-el-simulador)
5. [Cómo funciona el agente](#cómo-funciona-el-agente)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Pruebas](#pruebas)
8. [Problemas frecuentes](#problemas-frecuentes)

---

## Requisitos

| Requisito | Para qué |
|---|---|
| **Python 3.13 o superior** con **Tkinter** | Ejecutar el programa y su interfaz gráfica |
| [`openpyxl`](https://pypi.org/project/openpyxl/) | Botón «Descargar Excel» del Historial |
| [`pillow`](https://pypi.org/project/pillow/) | Botones «Copiar imagen» y «Guardar PNG» de la tabla percepción → acción |
| `wl-copy` (Wayland) o `xclip` (X11) — *opcional, solo Linux* | Copiar la tabla al portapapeles como imagen |

Se recomienda [**uv**](https://docs.astral.sh/uv/), que instala la versión correcta de Python y las dependencias
con un solo comando. También se puede usar `pip`.

## Instalación

### 1. Descargar el código

```bash
git clone https://github.com/farichula26/tarea03-agente.git
cd tarea03-agente
```

(O descarga el ZIP desde GitHub: **Code → Download ZIP** y descomprímelo.)

### 2a. Opción recomendada: con uv

Instala uv (una sola vez):

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Luego, dentro de la carpeta del proyecto:

```bash
uv sync
```

Esto crea el entorno virtual `.venv`, descarga Python 3.13 si no lo tienes e instala `openpyxl` y `pillow`
con las versiones exactas de `uv.lock`.

### 2b. Alternativa: con pip

Necesitas tener instalado Python 3.13 o superior.

```bash
python -m venv .venv

# Activar el entorno
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

pip install openpyxl pillow
```

### 3. Verificar Tkinter

Tkinter viene incluido con Python en **Windows** y **macOS** (instalador de python.org) y también en el Python que
descarga uv. Si usas el Python del sistema en **Linux**, puede que tengas que instalarlo aparte:

```bash
sudo dnf install python3-tkinter     # Fedora
sudo apt install python3-tk          # Ubuntu / Debian
sudo pacman -S tk                    # Arch
```

Para comprobarlo:

```bash
python -c "import tkinter; tkinter._test()"
```

Debe abrirse una pequeña ventana de prueba.

### 4. (Opcional, Linux) Copiar imágenes al portapapeles

```bash
sudo dnf install wl-clipboard        # Fedora (Wayland)
sudo apt install wl-clipboard xclip  # Ubuntu / Debian
```

Sin estas herramientas el programa funciona igual; solo el botón «Copiar imagen» te pedirá usar «Guardar PNG».

## Ejecución

```bash
uv run main.py          # con uv
python main.py          # con pip (con el entorno activado)
```

Se abre la ventana del simulador con un ambiente de 12 × 16 celdas generado con la semilla 7.

## Cómo usar el simulador

La ventana tiene tres zonas: la barra de controles arriba, el tablero a la izquierda y los paneles a la derecha.

### Barra superior

| Control | Qué hace |
|---|---|
| **Filas / Columnas** | Tamaño N × M de la malla (de 3 a 40). |
| **Semilla** | Número que fija el ambiente aleatorio: la misma semilla genera siempre el mismo mapa. Si lo dejas vacío o escribes algo que no es un número, se elige una semilla al azar y se muestra para poder repetirla. |
| **Generar ambiente** | Crea un mapa nuevo con el tamaño y la semilla indicados, y coloca al agente al inicio de la línea. |
| **Paso** (o tecla **Espacio**) | Ejecuta una iteración del agente: percibir → decidir → actuar. |
| **Reproducir / Pausar** | Ejecuta pasos automáticamente hasta que se detecta el bucle infinito. |
| **Reiniciar** | Vuelve al estado inicial con el mismo mapa. |
| **Rápido — Lento** | Velocidad de la reproducción automática. |

### Tablero

- **Negro** = línea (piso oscuro), **blanco** = sin línea (piso no oscuro), **rayado** = pared (fuera de la malla).
  Son los mismos símbolos del enunciado.
- El **agente** es el cuadrado verde con una flecha que indica hacia dónde mira. Las **celdas con borde naranja
  punteado** son las tres que ve su cámara (izquierda, centro y derecha).
- Cada celda donde el agente tomó una decisión muestra tres datos: la **regla** (`R4`), el **caso** (`C31`) y la
  **iteración** (`#12`). Si pasó varias veces, se muestra la última.
- Cuando se detecta el bucle, las celdas que forman el ciclo se marcan con **borde rojo**.
- **Clic izquierdo** sobre una celda: pinta o borra línea (puedes arrastrar para dibujar).
- **Clic derecho** sobre una celda: mueve el agente ahí; sobre el agente, lo gira 90° a la derecha.
- Cualquier edición reinicia la simulación.

### Pestaña «Paso actual»

- Muestra la **decisión pendiente**: qué percibe ahora el agente (los 6 valores de sus sensores), qué caso es, qué
  regla aplicará y con qué acciones, **antes** de pulsar Paso. Debajo aparece un resumen del paso anterior.
- Abajo está la **tabla percepción → acción** completa (54 casos), con el caso actual resaltado en amarillo.
- **Copiar imagen** / **Guardar PNG**: exportan la tabla completa como una imagen de 9 × 6 tarjetas, lista para
  pegar en una diapositiva.

### Pestaña «Historial»

Una fila por iteración, con la percepción de cada sensor:

| Columna | Significado | Valores |
|---|---|---|
| N | Número de iteración | 1, 2, 3, … |
| Pos | Celda (fila, columna) donde el agente decidió | 0…N-1, 0…M-1 |
| Ori | Orientación antes de actuar (propioceptor) | `^` `>` `v` `<` |
| Cont | Sensor de contacto | `C` / `-C` |
| Piso | Cámara 1 | `O` (oscuro) / `-O` (no oscuro) |
| Izq / Cen / Der | Cámara 2: celdas de adelante | `O` / `-O` / `P` (pared) |
| Caso | Caso del enunciado | C1 … C54 |
| Regla | Regla aplicada | R1 … R8 |
| Acción | Acciones ejecutadas, en orden | Avanzar, Rot +90, Rot -90 |
| → Pos / → Ori | Posición y orientación después de actuar | |
| Obs. | Eventos | Choque, Inicio del bucle, Bucle detectado |

- Filas **amarillas** = pasos ejecutados; la fila **blanca** final = lo que hará al pulsar Paso.
- Al hacer clic en una fila se resalta esa celda en el tablero y el panel muestra ese paso.
- **Descargar Excel**: guarda la tabla tal como se ve en ese momento en un archivo `.xlsx`.

### Pestaña «Reglas»

Explica cada regla con lenguaje sencillo: cuándo se usa, por qué hace lo que hace, un dibujo de ejemplo, los casos
que cubre y cuántas veces se ha usado en la simulación actual.

### Flujo sugerido para responder el informe

1. Elige tamaño y semilla, y pulsa **Generar ambiente**.
2. Pulsa **Reproducir** (o **Paso** varias veces) hasta que la barra inferior indique **«Bucle infinito»**.
3. Lee los datos en el **Historial** (o descárgalo en Excel) y en el tablero.
4. Repite con otras semillas para comparar casos.

---

## Cómo funciona el agente

### Ambiente

- Malla de N × M celdas: `0` = claro (sin línea), `1` = oscuro (línea). Fuera de la malla está la pared (`2`).
- Se generan **1 o 2 líneas** como una caminata aleatoria desde un borde, con:
  - ancho de 1 celda (70 %) o 2 celdas (30 %);
  - **curvas** de ±90°;
  - **cortes** de 1–2 celdas (líneas discontinuas).
- El agente empieza en la primera celda oscura, mirando hacia donde sigue la línea.
- El ambiente es **estático**: no cambia mientras el agente actúa.

### Sensores (6 percepciones)

| Sensor | Percepción | Valores |
|---|---|---|
| Propioceptor | Orientación | ▲ ▶ ▼ ◀ |
| Contacto | Contacto | Contacto / No contacto |
| Cámara 1 | Piso (celda del agente) | Oscuro / No oscuro |
| Cámara 2 | Piso izquierda, centro y derecha (fila de adelante) | Oscuro / No oscuro / Borde |

Las cámaras son **relativas al agente**: «adelante» depende de hacia dónde mira. Por eso las reglas no necesitan
usar la orientación.

### Acciones

- **Avanzar**: se mueve una celda hacia adelante; si saldría de la malla, no se mueve y se activa el sensor de contacto.
- **Rotar +90**: gira a la izquierda (sentido antihorario).
- **Rotar -90**: gira a la derecha (sentido horario).

En cada iteración el agente ejecuta **1 o 2 acciones, una después de la otra**.

### Los 54 casos

Cada combinación de *piso × izquierda × centro × derecha* es un caso, numerado en el mismo orden que la página 2
del enunciado:

```
Caso = piso·27 + izquierda·9 + centro·3 + derecha + 1      (claro = 0, oscuro = 1, pared = 2)
```

2 valores de piso × 3 × 3 × 3 = **54 casos** (C1–C27 con piso claro, C28–C54 con piso oscuro).

### Las 8 reglas

Se evalúan **en orden** y se aplica la **primera** que se cumple:

| Regla | Condición | Acciones | Significado |
|---|---|---|---|
| R1 | contacto | Rotar -90 | Chocó con la pared |
| R2 | centro = O y der = O y izq ≠ O | Avanzar, Rotar -90 | Curva a la derecha |
| R3 | centro = O y izq = O y der ≠ O | Avanzar, Rotar +90 | Curva a la izquierda |
| R4 | centro = O | Avanzar | Línea recta adelante |
| R5 | centro = -O y izq = O | Avanzar, Rotar +90 | Línea en diagonal izquierda |
| R6 | centro = -O y der = O | Avanzar, Rotar -90 | Línea en diagonal derecha |
| R7 | centro = P | Rotar -90 | Pared adelante: girar antes de chocar |
| R8 | siempre | Avanzar | Sin línea adelante: avanzar buscando una nueva |

R8 cumple lo que pide el enunciado para líneas discontinuas: *«intentar avanzar por las celdas claras hasta ubicar
una nueva línea»*. Como R7 gira antes de llegar a la pared, el agente nunca choca; R1 queda como regla de respaldo.

### Ciclo de una iteración

1. **Percibir**: lee los 6 sensores.
2. **Decidir**: calcula el caso y busca la primera regla que se cumple.
3. **Actuar**: ejecuta sus 1 o 2 acciones.
4. **Registrar** el paso en el historial y revisar si hay bucle.

### Detección del bucle infinito

El agente no tiene memoria, así que no puede saber que está en bucle; lo detecta el **simulador**. Guarda cada
estado `(fila, columna, orientación, contacto)` con la iteración en que apareció. Como el agente es determinista y
el ambiente estático, si un estado se repite todo lo demás se repetirá:

- **Entrada al bucle** = iteración en que ese estado apareció por primera vez.
- **Longitud del bucle** = iteración actual − entrada.

Hay como máximo 8·N·M estados distintos, así que el agente **siempre** termina en un bucle, en a lo sumo 8·N·M
iteraciones. Cada decisión cuesta O(1) (a lo sumo 8 reglas).

### Estadísticas que se pueden obtener

| Pregunta del informe | Cómo se obtiene |
|---|---|
| Reglas usadas al menos una vez | Columna Regla del Historial / pestaña Reglas |
| Choques antes de llegar a la línea | Columna Obs. («Choque») |
| Avances | Acciones «Avanzar» que movieron al agente |
| Rotaciones | Acciones «Rot +90» y «Rot -90» |
| Desempeño | Celdas oscuras distintas visitadas ÷ total de celdas oscuras × 100 |
| ¿Retorna a la posición inicial? | Si alguna fila termina (→ Pos) en la celda inicial |
| Iteraciones hasta el bucle | Barra inferior al detectar el bucle (iteración de entrada y longitud del ciclo) |

La función `estadisticas()` de `agent/simulacion.py` calcula todas estas respuestas a partir del estado de la
simulación.

---

## Estructura del proyecto

```
tarea03-agente/
├── main.py                 # Punto de entrada: abre la ventana
├── agent/                  # Lógica del agente (sin interfaz)
│   ├── ambiente.py         # Malla, generación aleatoria, percepción y acciones
│   ├── reglas.py           # Reglas R1–R8, numeración de casos, decidir(), tabla percepción → acción
│   └── simulacion.py       # Estado, paso(), detección del bucle y estadísticas
├── ui/                     # Interfaz gráfica en Tkinter
│   ├── app.py              # Ventana principal, barra de controles y eventos
│   ├── tablero.py          # Dibujo de la malla, marcas R/C/# y el agente
│   ├── paneles.py          # Pestañas Paso actual, Historial y Reglas
│   ├── simbolos.py         # Símbolos del enunciado (línea, no-línea, pared)
│   ├── exportar.py         # Exportación a Excel y a PNG / portapapeles
│   └── tema.py             # Colores y fuentes
├── tests/
│   └── test_agente.py      # Pruebas de la lógica del agente
├── informe/
│   └── Tarea 3. Diseño de Agentes (2) (1).pdf   # Enunciado
├── pyproject.toml          # Dependencias del proyecto
└── uv.lock                 # Versiones exactas de las dependencias
```

La lógica de `agent/` se puede usar sin la interfaz, por ejemplo:

```python
from agent.ambiente import generar_ambiente, posicion_inicial
from agent.simulacion import nuevo_estado, paso, estadisticas

grid = generar_ambiente(12, 16, semilla=7)
estado = nuevo_estado(grid, *posicion_inicial(grid))
while paso(estado):      # devuelve None cuando se detecta el bucle
    pass
for pregunta, respuesta in estadisticas(estado):
    print(pregunta, "→", respuesta)
```

## Pruebas

```bash
uv run python -m tests.test_agente      # con uv
python -m tests.test_agente             # con pip
```

Comprueban la numeración de los casos, cada regla, la percepción relativa de las cámaras, el choque con la pared y
que el agente siempre termine en un bucle. Deben terminar mostrando `OK`.

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | Instala Tkinter (ver [Verificar Tkinter](#3-verificar-tkinter)) o usa `uv run main.py`, que trae su propio Python con Tkinter. |
| `ModuleNotFoundError: No module named 'openpyxl'` o `'PIL'` | Ejecuta `uv sync` o `pip install openpyxl pillow` con el entorno activado. |
| La ventana o las letras se ven muy pequeñas | El programa se adapta a la escala de la pantalla; prueba maximizar la ventana. En Linux con el Python de uv las fuentes pueden verse menos suaves: usar el Python del sistema con `python3-tkinter` lo mejora. |
| «Copiar imagen» dice que no encontró wl-copy ni xclip | Instala `wl-clipboard` o `xclip` (Linux), o usa «Guardar PNG». En Windows y macOS usa «Guardar PNG». |
| «No se pudo guardar el Excel» | Cierra el archivo si está abierto en Excel y vuelve a intentarlo. |
