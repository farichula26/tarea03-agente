"""Ventana principal del simulador (solo funciones; el estado vive en el dict `app`)."""
import random
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk

from agent.ambiente import CLARO, OSCURO, generar_ambiente, posicion_inicial
from agent.simulacion import nuevo_estado, paso
from ui import tema
from ui.exportar import copiar_tabla_portapapeles, exportar_historial, guardar_tabla_png
from ui.paneles import actualizar_paneles, crear_paneles
from ui.tablero import celda_en, dibujar_tablero


def crear_app():
    root = tk.Tk()
    root.title("Agente seguidor de líneas")
    root.configure(bg=tema.FONDO)
    fuentes = tema.fuentes(root)
    esc = fuentes["esc"]
    ancho, alto = int(root.winfo_screenwidth() * .85), int(root.winfo_screenheight() * .85)
    root.geometry(f"{ancho}x{alto}")
    root.minsize(int(1000 * esc), int(640 * esc))
    _estilos(root, fuentes)

    app = {"root": root, "fuentes": fuentes, "corriendo": False, "seleccion": None, "tarea": None}
    app["filas"], app["columnas"] = tk.IntVar(value=12), tk.IntVar(value=16)
    app["semilla"], app["velocidad"] = tk.StringVar(value="7"), tk.IntVar(value=250)

    # Barra superior
    barra = ttk.Frame(root, padding=(16, 12), style="Barra.TFrame")
    barra.pack(fill="x")
    for texto, var, ancho in (("Filas", app["filas"], 4), ("Columnas", app["columnas"], 4)):
        ttk.Label(barra, text=texto, style="Barra.TLabel").pack(side="left", padx=(0, 6))
        ttk.Spinbox(barra, from_=3, to=40, textvariable=var, width=ancho).pack(side="left", padx=(0, 14))
    ttk.Label(barra, text="Semilla", style="Barra.TLabel").pack(side="left", padx=(0, 6))
    ttk.Entry(barra, textvariable=app["semilla"], width=8).pack(side="left", padx=(0, 10))
    ttk.Button(barra, text="Generar ambiente", command=lambda: generar(app)).pack(side="left")

    ttk.Separator(barra, orient="vertical").pack(side="left", fill="y", padx=18)
    ttk.Button(barra, text="Paso", style="Accion.TButton", command=lambda: un_paso(app)).pack(side="left")
    app["btn_play"] = ttk.Button(barra, text="Reproducir", command=lambda: alternar(app))
    app["btn_play"].pack(side="left", padx=8)
    ttk.Button(barra, text="Reiniciar", command=lambda: reiniciar(app)).pack(side="left")
    ttk.Label(barra, text="Rápido", style="Barra.TLabel").pack(side="left", padx=(18, 4))
    ttk.Scale(barra, from_=30, to=1000, variable=app["velocidad"], length=int(140 * esc)).pack(side="left")
    ttk.Label(barra, text="Lento", style="Barra.TLabel").pack(side="left", padx=(4, 0))

    # Cuerpo: tablero a la izquierda, paneles a la derecha
    cuerpo = ttk.Frame(root, style="Panel.TFrame")
    cuerpo.pack(fill="both", expand=True)
    derecha = ttk.Frame(cuerpo, width=max(int(480 * esc), ancho // 3), style="Panel.TFrame")
    derecha.pack(side="right", fill="y", padx=(0, 12), pady=12)
    derecha.pack_propagate(False)
    app["canvas"] = tk.Canvas(cuerpo, bg=tema.FONDO, highlightthickness=0)
    app["canvas"].pack(side="left", fill="both", expand=True, padx=12, pady=12)
    app["paneles"] = crear_paneles(derecha, fuentes, lambda sel: elegir_historial(app, sel), lambda: exportar(app),
                                   lambda: copiar_tabla(app), lambda: guardar_tabla(app))

    app["estado_txt"] = tk.StringVar()
    ttk.Label(root, textvariable=app["estado_txt"], style="Estado.TLabel", padding=(16, 8)).pack(fill="x")

    app["canvas"].bind("<Configure>", lambda _: redibujar(app))
    app["canvas"].bind("<Button-1>", lambda ev: editar_celda(app, ev))
    app["canvas"].bind("<B1-Motion>", lambda ev: editar_celda(app, ev, arrastre=True))
    app["canvas"].bind("<Button-3>", lambda ev: colocar_agente(app, ev))
    root.bind("<space>", lambda _: un_paso(app))

    generar(app)
    root.mainloop()


def _estilos(root, f):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=tema.FONDO, foreground=tema.TEXTO, font=(f["ui"], 10))
    s.configure("Panel.TFrame", background=tema.FONDO)
    s.configure("Barra.TFrame", background=tema.TAPETE)
    s.configure("Barra.TLabel", background=tema.TAPETE)
    s.configure("Panel.TLabel", background=tema.FONDO)
    s.configure("Suave.TLabel", background=tema.FONDO, foreground=tema.TEXTO_SUAVE, font=(f["ui"], 9))
    s.configure("Valor.TLabel", background=tema.FONDO, font=(f["ui"], 10, "bold"))
    s.configure("Titulo.TLabel", background=tema.FONDO, font=(f["ui"], 18, "bold"))
    s.configure("Regla.TLabel", background=tema.FONDO, foreground=tema.PCB, font=(f["ui"], 12, "bold"))
    s.configure("Dato.TLabel", background=tema.FONDO, font=(f["ui"], 10))
    s.configure("Seccion.TLabel", background=tema.FONDO, font=(f["ui"], 12, "bold"))
    s.configure("Estado.TLabel", background=tema.TAPETE, foreground=tema.TEXTO)
    s.configure("Accion.TButton", background=tema.PCB, foreground="white", font=(f["ui"], 10, "bold"))
    s.map("Accion.TButton", background=[("active", tema.PCB_BORDE)])
    s.configure("Treeview", rowheight=int(24 * f["esc"]), fieldbackground="white")
    s.configure("Treeview.Heading", font=(f["ui"], 9, "bold"))
    s.map("Treeview", background=[("selected", tema.SELECCION)])
    s.configure("Casos.Treeview", rowheight=int(40 * f["esc"]), fieldbackground="white")
    s.map("Casos.Treeview", background=[("selected", tema.SELECCION)])


# --- Acciones de la interfaz ---

def generar(app):
    texto = app["semilla"].get().strip()
    if not texto.lstrip("-").isdigit():
        texto = str(random.randrange(10_000))
        app["semilla"].set(texto)  # se muestra para poder reproducir el mismo ambiente
    n = min(40, max(3, _entero(app["filas"], 12)))
    m = min(40, max(3, _entero(app["columnas"], 16)))
    app["grid"] = generar_ambiente(n, m, int(texto))
    app["inicio"] = posicion_inicial(app["grid"])
    reiniciar(app)


def _entero(var, defecto):
    try:
        return var.get()
    except tk.TclError:
        return defecto


def reiniciar(app):
    pausar(app)
    app["estado"] = nuevo_estado(app["grid"], *app["inicio"])
    app["seleccion"] = None
    refrescar(app)


def un_paso(app):
    if not paso(app["estado"]):
        pausar(app)
    app["seleccion"] = None
    refrescar(app)
    return not app["estado"]["bucle"]


def alternar(app):
    if app["corriendo"]:
        pausar(app)
    elif not app["estado"]["bucle"]:
        app["corriendo"] = True
        app["btn_play"].configure(text="Pausar")
        _tic(app)


def _tic(app):
    if app["corriendo"] and un_paso(app):
        app["tarea"] = app["root"].after(app["velocidad"].get(), lambda: _tic(app))
    else:
        pausar(app)


def pausar(app):
    app["corriendo"] = False
    if app["tarea"]:
        app["root"].after_cancel(app["tarea"])
        app["tarea"] = None
    if "btn_play" in app:
        app["btn_play"].configure(text="Reproducir")


def editar_celda(app, ev, arrastre=False):
    """Clic izquierdo: pinta o borra línea. Al arrastrar, repite el mismo trazo."""
    if not arrastre:
        app["trazo"] = None
    celda = celda_en(app["canvas"], app["grid"], ev.x, ev.y)
    if not celda:
        return
    r, c = celda
    # El trazo lo decide la primera celda de la malla que se toca (el clic puede empezar sobre el marco)
    if app.get("trazo") is None:
        app["trazo"] = CLARO if app["grid"][r][c] == OSCURO else OSCURO
    if app["grid"][r][c] != app["trazo"]:
        app["grid"][r][c] = app["trazo"]
        reiniciar(app)


def colocar_agente(app, ev):
    """Clic derecho: coloca el agente; sobre el agente, lo gira 90° a la derecha."""
    celda = celda_en(app["canvas"], app["grid"], ev.x, ev.y)
    if celda:
        pos, orient = app["inicio"]
        app["inicio"] = (pos, (orient + 1) % 4) if celda == pos else (celda, orient)
        reiniciar(app)


def elegir_historial(app, seleccion):
    if seleccion and seleccion[0] != "pendiente":  # la fila pendiente aún no es un paso del historial
        reg = app["estado"]["historial"][int(seleccion[0]) - 1]
        app["seleccion"] = reg["desde"]
        dibujar_tablero(app["canvas"], app["estado"], app["fuentes"], app["seleccion"])
        actualizar_paneles(app["paneles"], app["estado"], reg["iter"])


def exportar(app):
    """Guarda la tabla del Historial, tal como se ve ahora, en un .xlsx elegido por el usuario."""
    pausar(app)
    ruta = filedialog.asksaveasfilename(
        parent=app["root"], title="Descargar historial", defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")],
        initialfile=f"historial_s{app['semilla'].get().strip()}_it{app['estado']['iter']}.xlsx")
    if not ruta:
        return
    try:
        exportar_historial(app["paneles"]["historial"], ruta)
    except OSError as error:  # p. ej. el archivo está abierto en Excel
        app["estado_txt"].set(f"No se pudo guardar el Excel: {error}")
    else:
        app["estado_txt"].set(f"Historial guardado en {ruta}")


def copiar_tabla(app):
    """Deja la tabla percepción-acción como imagen en el portapapeles (para pegarla en una diapositiva)."""
    try:
        copiada = copiar_tabla_portapapeles()
    except (OSError, subprocess.SubprocessError) as error:
        app["estado_txt"].set(f"No se pudo copiar la imagen: {error}")
        return
    app["estado_txt"].set("Tabla copiada como imagen: pégala con Ctrl+V." if copiada else
                          "No se encontró wl-copy ni xclip para copiar imágenes; usa «Guardar PNG».")


def guardar_tabla(app):
    ruta = filedialog.asksaveasfilename(
        parent=app["root"], title="Guardar tabla percepción-acción", defaultextension=".png",
        filetypes=[("Imagen PNG", "*.png")], initialfile="tabla_percepcion_accion.png")
    if not ruta:
        return
    try:
        guardar_tabla_png(ruta)
    except OSError as error:
        app["estado_txt"].set(f"No se pudo guardar la imagen: {error}")
    else:
        app["estado_txt"].set(f"Tabla guardada en {ruta}")


def redibujar(app):
    if "estado" in app:
        dibujar_tablero(app["canvas"], app["estado"], app["fuentes"], app["seleccion"])


def refrescar(app):
    e = app["estado"]
    redibujar(app)
    actualizar_paneles(app["paneles"], e)
    if e["bucle"]:
        b = e["bucle"]
        texto = (f"Bucle infinito: el agente entra al ciclo en la iteración {b['entrada']} "
                 f"y se repite cada {b['longitud']} iteraciones. Las celdas del ciclo tienen borde rojo.")
    else:
        pos, ori = e["pos"], "▲▶▼◀"[e["orient"]]
        texto = (f"Iteración {e['iter']}   Agente en ({pos[0]}, {pos[1]}) {ori}.   "
                 "Clic izquierdo pinta o borra línea, clic derecho coloca o gira el agente, Espacio da un paso.")
    app["estado_txt"].set(texto)
