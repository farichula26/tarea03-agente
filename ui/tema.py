"""Paleta y fuentes: símbolos del enunciado (negro, blanco, pared rayada) y robot verde PCB."""
import tkinter.font as tkfont

TAPETE = "#FFFFFF"       # no-línea (blanco, como en el enunciado)
TINTA = "#000000"        # línea (negro)
REJILLA = "#33339A"      # contorno azul marino de las celdas del enunciado
FONDO = "#F3F5F1"        # fondo de la ventana
TEXTO = "#26322D"
TEXTO_SUAVE = "#66736C"
RESALTE = "#F2DFA4"      # fila del caso actual en la tabla
CICLO = "#C4372B"        # borde de las celdas del bucle
PCB = "#1D6A4E"          # cuerpo del agente
PCB_BORDE = "#0E3B2B"
CAMARA = "#E09B00"       # campo de visión de la cámara 2
MARCA_CLARA = "#5A4710"  # texto R/C/# sobre celda clara
MARCA_OSCURA = "#F2C14E"  # texto R/C/# sobre celda oscura
SELECCION = "#2F6DB0"
CHOQUE = "#C4372B"


def elegir(familias, preferidas, defecto):
    return next((f for f in preferidas if f in familias), defecto)


def fuentes(root):
    familias = set(tkfont.families(root))
    ui = elegir(familias, ("Noto Sans", "Segoe UI", "Helvetica Neue", "DejaVu Sans"), "TkDefaultFont")
    mono = elegir(familias, ("Source Code Pro", "Noto Sans Mono", "Consolas", "Menlo", "DejaVu Sans Mono"), "TkFixedFont")
    # Factor respecto de una pantalla de 96 ppp, para medidas en píxeles
    return {"ui": ui, "mono": mono, "esc": root.winfo_fpixels("1i") / 96}
