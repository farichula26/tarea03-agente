"""Dibujo de la malla, las marcas R/C/# por casilla y el agente."""
import math

from agent.ambiente import BORDE, DELTAS, OSCURO, camaras, dentro
from agent.simulacion import celdas_del_ciclo
from ui import tema
from ui.simbolos import dibujar_celda


def geometria(canvas, grid):
    margen = 28 * float(canvas.winfo_fpixels("1i")) / 96  # espacio para los números de fila/columna
    n, m = len(grid), len(grid[0])
    ancho, alto = max(canvas.winfo_width(), 200), max(canvas.winfo_height(), 200)
    # m + 2 y n + 2: marco de pared rayada alrededor de la malla
    lado = max(12, min((ancho - margen - 12) / (m + 2), (alto - margen - 12) / (n + 2)))
    x0 = margen + (ancho - margen - lado * (m + 2)) / 2 + lado
    y0 = margen + (alto - margen - lado * (n + 2)) / 2 + lado
    return x0, y0, lado


def celda_en(canvas, grid, x, y):
    x0, y0, lado = geometria(canvas, grid)
    r, c = int((y - y0) // lado), int((x - x0) // lado)
    return (r, c) if dentro(grid, r, c) and x >= x0 and y >= y0 else None


def dibujar_tablero(canvas, e, fuentes, seleccion=None):
    canvas.delete("all")
    grid = e["grid"]
    x0, y0, lado = geometria(canvas, grid)
    ciclo = celdas_del_ciclo(e)
    tam_marca = -int(lado / 4.4)  # negativo = píxeles: tres líneas caben en la celda
    mostrar_marcas = lado >= 33

    def caja(r, c, inset=0):
        return (x0 + c * lado + inset, y0 + r * lado + inset,
                x0 + (c + 1) * lado - inset, y0 + (r + 1) * lado - inset)

    n, m = len(grid), len(grid[0])
    for r in range(-1, n + 1):
        for c in range(-1, m + 1):
            if not dentro(grid, r, c):
                dibujar_celda(canvas, x0 + c * lado, y0 + r * lado, lado, BORDE)

    for r, fila in enumerate(grid):
        canvas.create_text(x0 - lado - 8, y0 + (r + .5) * lado, text=r, anchor="e",
                           fill=tema.TEXTO_SUAVE, font=(fuentes["mono"], 8))
        for c, v in enumerate(fila):
            oscuro = v == OSCURO
            dibujar_celda(canvas, x0 + c * lado, y0 + r * lado, lado, v)
            if (r, c) in ciclo:
                canvas.create_rectangle(*caja(r, c, 2), outline=tema.CICLO, width=3)
            marca = e["marcas"].get((r, c))
            if marca and mostrar_marcas:
                canvas.create_text(x0 + c * lado + lado * .1, y0 + r * lado + lado * .06, anchor="nw",
                                   text=f"{marca['regla']}\nC{marca['caso']}\n#{marca['iter']}",
                                   fill=tema.MARCA_OSCURA if oscuro else tema.MARCA_CLARA,
                                   font=(fuentes["mono"], tam_marca))
    for c in range(len(grid[0])):
        canvas.create_text(x0 + (c + .5) * lado, y0 - lado - 8, text=c, anchor="s",
                           fill=tema.TEXTO_SUAVE, font=(fuentes["mono"], 8))

    # Campo de la cámara 2: las tres celdas de adelante
    for r, c in camaras(e["pos"], e["orient"]):
        if -1 <= r <= n and -1 <= c <= m:
            canvas.create_rectangle(*caja(r, c, 2), outline=tema.CAMARA, width=3, dash=(6, 3))

    if seleccion:
        canvas.create_rectangle(*caja(*seleccion, 1), outline=tema.SELECCION, width=3)

    _dibujar_agente(canvas, e, x0, y0, lado)


def _dibujar_agente(canvas, e, x0, y0, lado):
    r, c = e["pos"]
    cx, cy = x0 + (c + .5) * lado, y0 + (r + .5) * lado
    medio = lado * math.sqrt(.75) / 2  # el cuerpo ocupa el 75 % del área de la celda
    canvas.create_rectangle(cx - medio, cy - medio, cx + medio, cy + medio, fill=tema.PCB,
                            outline=tema.CHOQUE if e["contacto"] else tema.PCB_BORDE,
                            width=4 if e["contacto"] else 2)
    fr, fc = DELTAS[e["orient"]]
    lr, lc = DELTAS[(e["orient"] + 3) % 4]
    punta = (cx + fc * medio * .75, cy + fr * medio * .75)
    base_izq = (cx - fc * medio * .45 + lc * medio * .5, cy - fr * medio * .45 + lr * medio * .5)
    base_der = (cx - fc * medio * .45 - lc * medio * .5, cy - fr * medio * .45 - lr * medio * .5)
    canvas.create_polygon(*punta, *base_izq, *base_der, fill="white", outline="")
    # Las tres cámaras al frente del cuerpo
    radio = max(2, lado * .06)
    for k in (-1, 0, 1):
        px = cx + fc * medio + lc * medio * .7 * k
        py = cy + fr * medio + lr * medio * .7 * k
        canvas.create_oval(px - radio, py - radio, px + radio, py + radio, fill=tema.CAMARA, outline=tema.PCB_BORDE)
