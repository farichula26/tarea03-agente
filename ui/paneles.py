"""Panel derecho: paso actual con la tabla percepción-acción, historial y reglas explicadas."""
import tkinter as tk
from tkinter import ttk

from agent.ambiente import BORDE, CLARO, NOMBRE_VALOR, ORIENTACIONES, OSCURO
from agent.reglas import DESCRIPCION, REGLAS, decodificar_caso, tabla_percepcion_accion
from agent.simulacion import siguiente
from ui import tema
from ui.simbolos import dibujar_caso, imagen_caso


# Explicación en lenguaje simple de cada regla: (se usa cuando, por qué, caso de ejemplo)
EXPLICACION = {
    "R1": ("el sensor de contacto indica que el cuerpo del agente chocó con la pared.",
           "no puede avanzar hacia la pared, así que gira para probar otra dirección. Con estas reglas nunca "
           "se activa: R7 gira antes de chocar porque la cámara ve el borde.", None),
    "R2": ("hay línea en el centro y a la derecha, pero no a la izquierda.",
           "la línea dobla a la derecha: avanza a la celda del centro (la esquina) y gira para quedar "
           "mirando hacia donde sigue la línea.", 32),
    "R3": ("hay línea en el centro y a la izquierda, pero no a la derecha.",
           "es el espejo de R2: la línea dobla a la izquierda.", 40),
    "R4": ("hay línea en el centro (y no se cumplió R2 ni R3).",
           "la línea sigue recta delante del agente, así que solo avanza.", 31),
    "R5": ("el centro es piso claro y hay línea en la diagonal izquierda.",
           "la línea está en diagonal: avanza a la celda clara del centro y gira a la izquierda; "
           "así queda justo de frente a la celda oscura que vio.", 37),
    "R6": ("el centro es piso claro y hay línea en la diagonal derecha.",
           "es el espejo de R5, hacia la derecha.", 29),
    "R7": ("la celda del centro es borde (pared).",
           "avanzar sería chocar, así que gira a la derecha antes de tocar la pared.", 27),
    "R8": ("no se cumplió ninguna regla anterior: no hay línea adelante.",
           "la línea terminó o está cortada; el enunciado pide seguir por las celdas claras hasta "
           "encontrar una nueva línea, así que avanza recto.", 28),
}

INTRO = ("En cada iteración el agente:\n"
         "1. Percibe 6 valores: orientación, contacto, piso (cámara 1) y las celdas izquierda, centro "
         "y derecha de adelante (cámara 2).\n"
         "2. Revisa las reglas en orden, de R1 a R8, y aplica la primera cuya condición se cumple. "
         "Por eso R4 dice «y no se cumplió R2 ni R3».\n"
         "3. Ejecuta 1 o 2 acciones, una después de la otra.\n\n"
         "La orientación no influye: las cámaras siempre miran «adelante» respecto del agente. "
         "Rotar +90 es girar a la izquierda y Rotar -90 es girar a la derecha.")


def crear_paneles(padre, fuentes, al_elegir_historial, al_exportar, al_copiar_tabla, al_guardar_tabla):
    esc = fuentes["esc"]
    w = {"esc": esc}
    libro = ttk.Notebook(padre)
    libro.pack(fill="both", expand=True)

    # --- Paso actual (arriba) y tabla percepción-acción (abajo) ---
    f = ttk.Frame(libro, padding=12, style="Panel.TFrame")
    libro.add(f, text="Paso actual")
    w["titulo"] = ttk.Label(f, style="Titulo.TLabel")
    w["titulo"].pack(anchor="w")
    w["regla"] = ttk.Label(f, style="Regla.TLabel", wraplength=int(420 * esc), justify="left")
    w["regla"].pack(anchor="w", pady=(4, 10))

    fila = ttk.Frame(f, style="Panel.TFrame")
    fila.pack(fill="x")
    w["mini"] = tk.Canvas(fila, width=int(120 * esc), height=int(84 * esc), bg=tema.FONDO, highlightthickness=0)
    w["mini"].pack(side="left", anchor="n", padx=(0, 16))
    sensores_f = ttk.Frame(fila, style="Panel.TFrame")
    sensores_f.pack(side="left", anchor="n")
    w["sensores"] = {}
    sensores = (("Orientación", "orientacion", "Propioceptor"), ("Contacto", "contacto", "Contacto"),
                ("Piso", "piso", "Cámara 1"), ("Piso izquierda", "izq", "Cámara 2"),
                ("Piso centro", "centro", "Cámara 2"), ("Piso derecha", "der", "Cámara 2"))
    for i, (nombre, clave, sensor) in enumerate(sensores):
        ttk.Label(sensores_f, text=sensor, style="Suave.TLabel").grid(row=i, column=0, sticky="w")
        ttk.Label(sensores_f, text=nombre, style="Panel.TLabel").grid(row=i, column=1, sticky="w", padx=10)
        w["sensores"][clave] = ttk.Label(sensores_f, style="Valor.TLabel")
        w["sensores"][clave].grid(row=i, column=2, sticky="w")

    w["acciones"] = ttk.Label(f, style="Dato.TLabel", wraplength=int(420 * esc), justify="left")
    w["acciones"].pack(anchor="w", pady=(10, 0))
    w["anterior"] = ttk.Label(f, style="Suave.TLabel", wraplength=int(420 * esc), justify="left")
    w["anterior"].pack(anchor="w", pady=(6, 0))

    ttk.Separator(f).pack(fill="x", pady=10)
    ttk.Label(f, text="Tabla percepción → acción", style="Seccion.TLabel").pack(anchor="w")
    ttk.Label(f, text="Negro = línea, blanco = no-línea, rayado = pared; X = agente. "
                      "Con Contacto, cualquier caso usa R1.",
              style="Suave.TLabel", wraplength=int(420 * esc)).pack(anchor="w", pady=(2, 6))
    botones = ttk.Frame(f, style="Panel.TFrame")
    botones.pack(side="bottom", fill="x", pady=(6, 0))
    ttk.Button(botones, text="Copiar imagen", command=al_copiar_tabla).pack(side="left")
    ttk.Button(botones, text="Guardar PNG", command=al_guardar_tabla).pack(side="left", padx=8)
    cols = (("caso", "Caso", 50), ("regla", "Regla", 50), ("acciones", "Acciones", 170))
    lado = int(16 * esc)
    w["tabla"] = _arbol(f, cols, esc, imagen=3 * lado + int(40 * esc))
    w["imagenes"] = []  # Tk necesita conservar la referencia de cada imagen
    for caso, piso, izq, centro, der, rid, acc in tabla_percepcion_accion():
        img = imagen_caso(f, lado, piso, izq, centro, der)
        w["imagenes"].append(img)
        w["tabla"].insert("", "end", iid=str(caso), image=img, values=(f"C{caso}", rid, ", ".join(acc)))
    w["tabla"].tag_configure("actual", background=tema.RESALTE)

    # --- Historial ---
    f = ttk.Frame(libro, padding=8, style="Panel.TFrame")
    libro.add(f, text="Historial")
    arriba = ttk.Frame(f, style="Panel.TFrame")
    arriba.pack(fill="x", pady=(0, 6))
    ttk.Button(arriba, text="Descargar Excel", command=al_exportar).pack(side="right", anchor="n")
    ttk.Label(arriba, text="O = oscuro, -O = no oscuro, P = pared;  C / -C = contacto / sin contacto.\n"
                           "Amarillo = pasos ejecutados; fila blanca = lo que hará al pulsar Paso.",
              style="Suave.TLabel", wraplength=int(340 * esc), justify="left").pack(side="left", anchor="w")
    cols = (("n", "N", 34), ("pos", "Pos", 46), ("ori", "Ori", 32), ("cont", "Cont", 38), ("piso", "Piso", 38),
            ("izq", "Izq", 34), ("cen", "Cen", 34), ("der", "Der", 34), ("caso", "Caso", 42), ("regla", "Regla", 42),
            ("acciones", "Acción", 120), ("pos2", "→ Pos", 50), ("ori2", "→ Ori", 44), ("obs", "Obs.", 110))
    w["historial"] = _arbol(f, cols, esc, horizontal=True)
    w["historial"].tag_configure("hecho", background=tema.RESALTE)
    w["historial"].bind("<<TreeviewSelect>>", lambda _: al_elegir_historial(w["historial"].selection()))

    # --- Reglas ---
    f = ttk.Frame(libro, padding=8, style="Panel.TFrame")
    libro.add(f, text="Reglas")
    _crear_reglas(f, fuentes, w)
    return w


def _rueda(widget, destino, esc):
    """La rueda del mouse sobre `widget` desplaza `destino` por píxeles.
    Hace falta porque las tarjetas incrustadas no pasan el evento al Text, y el Text
    por sí solo saltaría una tarjeta entera por cada línea."""
    paso = int(40 * esc)

    def mover(sentido):
        destino.yview_scroll(sentido * paso, "pixels")
        return "break"

    widget.bind("<MouseWheel>", lambda ev: mover(-1 if ev.delta > 0 else 1))  # Windows, macOS, Tk 9
    widget.bind("<Button-4>", lambda ev: mover(-1))  # X11 con Tk 8.6
    widget.bind("<Button-5>", lambda ev: mover(1))


def _crear_reglas(padre, fuentes, w):
    """Una tarjeta por regla dentro de un Text de solo lectura (para tener scroll)."""
    esc = fuentes["esc"]
    texto = tk.Text(padre, wrap="word", relief="flat", bg=tema.FONDO, fg=tema.TEXTO, padx=10, pady=8,
                    font=(fuentes["ui"], 10), spacing3=6, cursor="arrow")
    barra = ttk.Scrollbar(padre, orient="vertical", command=texto.yview)
    texto.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    texto.pack(fill="both", expand=True)
    _rueda(texto, texto, esc)
    texto.insert("end", "Cómo decide el agente\n", "h")
    texto.tag_configure("h", font=(fuentes["ui"], 13, "bold"), spacing3=6)
    texto.insert("end", INTRO + "\n\n")

    casos = {}
    for caso, *_, rid, _acc in tabla_percepcion_accion():
        casos.setdefault(rid, []).append(f"C{caso}")

    ancho_texto = int(300 * esc)
    w["tarjetas"], w["usos"] = {}, {}
    for rid, desc, _, acciones in REGLAS:
        cuando, por_que, ejemplo = EXPLICACION[rid]
        tarjeta = tk.Frame(texto, bg=tema.TAPETE, highlightbackground=tema.REJILLA, highlightthickness=1,
                           padx=int(10 * esc), pady=int(8 * esc))
        partes = []
        tarjeta.grid_columnconfigure(1, minsize=int(94 * esc))  # mismo ancho con o sin dibujo
        if ejemplo:
            mini = tk.Canvas(tarjeta, width=int(84 * esc), height=int(60 * esc), bg=tema.TAPETE, highlightthickness=0)
            dibujar_caso(mini, 2 * esc, 2 * esc, 26 * esc, *decodificar_caso(ejemplo))
            mini.grid(row=0, column=1, rowspan=5, sticky="ne", padx=(10, 0))
            partes.append(mini)
        filas = (
            (f"{rid}  {desc}", (fuentes["ui"], 11, "bold"), tema.PCB),
            ("Se usa cuando " + cuando, (fuentes["ui"], 10), tema.TEXTO),
            ("Hace: " + " y luego ".join(acciones) + ".", (fuentes["ui"], 10, "bold"), tema.TEXTO),
            ("Por qué: " + por_que, (fuentes["ui"], 10), tema.TEXTO),
            ("Casos que cubre: " + (", ".join(casos.get(rid, [])) or "cualquier caso con Contacto")
             + (f"  (ejemplo dibujado: C{ejemplo})" if ejemplo else ""), (fuentes["ui"], 9), tema.TEXTO_SUAVE),
        )
        for i, (contenido, fuente, color) in enumerate(filas):
            etiqueta = tk.Label(tarjeta, text=contenido, font=fuente, fg=color, bg=tema.TAPETE,
                                wraplength=ancho_texto, justify="left", anchor="w")
            etiqueta.grid(row=i, column=0, sticky="w", pady=1)
            partes.append(etiqueta)
        w["usos"][rid] = tk.Label(tarjeta, font=(fuentes["ui"], 9, "bold"), fg=tema.TEXTO_SUAVE, bg=tema.TAPETE)
        w["usos"][rid].grid(row=5, column=0, sticky="w", pady=(2, 0))
        partes.append(w["usos"][rid])
        w["tarjetas"][rid] = (tarjeta, partes)
        for widget in (tarjeta, *partes):
            _rueda(widget, texto, esc)
        texto.window_create("end", window=tarjeta, pady=int(4 * esc))
        texto.insert("end", "\n")
    texto.configure(state="disabled")


def _arbol(padre, cols, esc, imagen=None, horizontal=False):
    """Treeview con barra de desplazamiento. Con `imagen` (ancho en px), la columna #0 muestra un dibujo;
    con `horizontal`, las columnas no se estiran y se añade barra horizontal."""
    marco = ttk.Frame(padre, style="Panel.TFrame")
    marco.pack(fill="both", expand=True)
    arbol = ttk.Treeview(marco, columns=[c[0] for c in cols], selectmode="browse",
                         show="tree headings" if imagen else "headings",
                         style="Casos.Treeview" if imagen else "Treeview")
    if imagen:
        arbol.heading("#0", text="Percepción", anchor="w")
        arbol.column("#0", width=imagen, stretch=False)
    for clave, titulo, ancho in cols:
        arbol.heading(clave, text=titulo, anchor="w")
        arbol.column(clave, width=int(ancho * esc), minwidth=int(ancho * esc), anchor="w",
                     stretch=clave == "acciones" and not horizontal)
    barra = ttk.Scrollbar(marco, orient="vertical", command=arbol.yview)
    arbol.configure(yscrollcommand=barra.set)
    arbol.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")
    if horizontal:
        barra_x = ttk.Scrollbar(marco, orient="horizontal", command=arbol.xview)
        arbol.configure(xscrollcommand=barra_x.set)
        barra_x.grid(row=1, column=0, sticky="ew")
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)
    return arbol


SENSOR = {CLARO: "-O", OSCURO: "O", BORDE: "P"}
ORI_ASCII = "^>v<"


def _fila(n, pos, ori, p, caso, regla, acciones, pos_fin=None, ori_fin=None, obs=""):
    """Valores de una fila del Historial, con la notación de letras."""
    return (n, f"{pos[0]},{pos[1]}", ORI_ASCII[ori], "C" if p["contacto"] else "-C",
            SENSOR[p["piso"]], SENSOR[p["izq"]], SENSOR[p["centro"]], SENSOR[p["der"]], f"C{caso}", regla,
            ", ".join(a.replace("Rotar", "Rot") for a in acciones),
            f"{pos_fin[0]},{pos_fin[1]}" if pos_fin else "", ORI_ASCII[ori_fin] if ori_fin is not None else "", obs)


def _obs(r, bucle):
    obs = ["Choque"] if r["choco"] else []
    if bucle and r["iter"] == bucle["entrada"] + 1:
        obs.append("Inicio del bucle")
    if bucle and r["iter"] == bucle["detectado"]:
        obs.append("Bucle detectado")
    return ", ".join(obs)


def _celda(pos, orient):
    return f"({pos[0]}, {pos[1]}) {ORIENTACIONES[orient]}"


def actualizar_paneles(w, e, seleccion_iter=None):
    """Sin selección: la decisión que el agente tomará ahora. Con selección: ese paso del historial."""
    hist = e["historial"]
    if seleccion_iter:
        d = reg = hist[seleccion_iter - 1]
        w["titulo"].configure(text=f"Iteración {reg['iter']} (historial)")
        w["acciones"].configure(text=f"Caso C{reg['caso']} en {_celda(reg['desde'], reg['orient_desde'])}.\n"
                                     f"Aplicó: {' y luego '.join(reg['acciones'])}; pasó a {_celda(reg['pos'], reg['orient'])}"
                                     + ("  (chocó con la pared)" if reg["choco"] else "") + ".")
        w["anterior"].configure(text="Pulsa Paso para volver a la decisión actual del agente.")
    else:
        d = siguiente(e)
        w["titulo"].configure(text=f"Iteración {e['iter'] + 1}: antes de actuar")
        w["acciones"].configure(text=f"Caso C{d['caso']} en {_celda(e['pos'], e['orient'])}.\n"
                                     f"Aplicará: {' y luego '.join(d['acciones'])}.")
        if hist:
            r = hist[-1]
            anterior = (f"Paso anterior #{r['iter']}: {r['regla']}, C{r['caso']} en "
                        f"{_celda(r['desde'], r['orient_desde'])} → {_celda(r['pos'], r['orient'])}.")
        else:
            anterior = "Todavía no hay pasos. Pulsa Paso para que el agente aplique esta regla."
        if e["bucle"]:
            anterior += " El agente está en bucle: seguirá repitiendo el mismo ciclo."
        w["anterior"].configure(text=anterior)
    w["regla"].configure(text=f"{d['regla']}  {DESCRIPCION[d['regla']]}")
    p = d["percepcion"]
    lado = 36 * w["esc"]
    w["mini"].delete("all")
    dibujar_caso(w["mini"], 6 * w["esc"], 6 * w["esc"], lado, p["piso"], p["izq"], p["centro"], p["der"])
    for clave, etiqueta in w["sensores"].items():
        if clave == "orientacion":
            texto = ORIENTACIONES[p[clave]]
        elif clave == "contacto":
            texto = "Contacto" if p[clave] else "No contacto"
        else:
            texto = NOMBRE_VALOR[p[clave]]
        etiqueta.configure(text=texto)

    # Historial: agrega solo las filas nuevas y rehace la fila pendiente (blanca) al final
    arbol = w["historial"]
    if arbol.exists("pendiente"):
        arbol.delete("pendiente")
    existentes = len(arbol.get_children())
    if existentes > len(hist):
        arbol.delete(*arbol.get_children())
        existentes = 0
    for r in hist[existentes:]:
        arbol.insert("", "end", iid=str(r["iter"]), tags=("hecho",), values=_fila(
            r["iter"], r["desde"], r["orient_desde"], r["percepcion"], r["caso"], r["regla"], r["acciones"],
            r["pos"], r["orient"], _obs(r, e["bucle"])))
    if e["bucle"]:  # la entrada al ciclo es una fila anterior: actualizar su observación
        r = hist[e["bucle"]["entrada"]]
        arbol.set(str(r["iter"]), "obs", _obs(r, e["bucle"]))
    pendiente = siguiente(e)
    arbol.insert("", "end", iid="pendiente", values=_fila(
        e["iter"] + 1, e["pos"], e["orient"], pendiente["percepcion"], pendiente["caso"], pendiente["regla"],
        pendiente["acciones"]))
    if not seleccion_iter:
        arbol.see("pendiente")

    # Caso actual resaltado en la tabla
    tabla = w["tabla"]
    for iid in tabla.tag_has("actual"):
        tabla.item(iid, tags=())
    tabla.item(str(d["caso"]), tags=("actual",))
    tabla.see(str(d["caso"]))

    # Reglas: usos acumulados y la regla del paso mostrado resaltada
    usos = {}
    for r in hist:
        usos[r["regla"]] = usos.get(r["regla"], 0) + 1
    for rid, (tarjeta, partes) in w["tarjetas"].items():
        n = usos.get(rid, 0)
        w["usos"][rid].configure(text=f"Usada {n} {'vez' if n == 1 else 'veces'}")
        color = tema.RESALTE if d["regla"] == rid else tema.TAPETE
        for widget in (tarjeta, *partes):
            widget.configure(bg=color)
