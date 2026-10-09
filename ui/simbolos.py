"""Símbolos de la página 2 del enunciado: negro = línea, blanco = no-línea, rayado = pared."""
import tkinter as tk

from agent.ambiente import BORDE, OSCURO
from ui import tema


def _rayas(lado):
    """Desplazamientos verticales de las rayas horizontales de una pared."""
    paso = max(3, lado / 7)
    k, ys = paso / 2, []
    while k < lado - 1:
        ys.append(k)
        k += paso
    return ys


def dibujar_celda(canvas, x, y, lado, valor):
    canvas.create_rectangle(x, y, x + lado, y + lado, outline=tema.REJILLA,
                            fill=tema.TINTA if valor == OSCURO else tema.TAPETE)
    if valor == BORDE:
        for k in _rayas(lado):
            canvas.create_line(x + 1, y + k, x + lado, y + k, fill=tema.TINTA, width=max(1, lado / 28))


def dibujar_caso(canvas, x0, y0, lado, piso, izq, centro, der):
    """Las tres celdas de adelante y, debajo de la del centro, la celda del agente con la X."""
    for i, v in enumerate((izq, centro, der)):
        dibujar_celda(canvas, x0 + i * lado, y0, lado, v)
    dibujar_celda(canvas, x0 + lado, y0 + lado, lado, piso)
    canvas.create_text(x0 + 1.5 * lado, y0 + 1.5 * lado, text="X", font=("TkDefaultFont", -int(lado * .45)),
                       fill=tema.TAPETE if piso == OSCURO else tema.TINTA)


def imagen_caso(root, lado, piso, izq, centro, der):
    """El mismo dibujo como PhotoImage, para mostrarlo dentro de un Treeview."""
    lado = int(lado)
    img = tk.PhotoImage(master=root, width=3 * lado + 1, height=2 * lado + 1)

    def celda(cx, cy, valor):
        x, y = cx * lado, cy * lado
        img.put(tema.REJILLA, to=(x, y, x + lado + 1, y + lado + 1))
        img.put(tema.TINTA if valor == OSCURO else tema.TAPETE, to=(x + 1, y + 1, x + lado, y + lado))
        if valor == BORDE:
            for k in _rayas(lado):
                img.put(tema.TINTA, to=(x + 1, y + int(k), x + lado, y + int(k) + 1))

    for i, v in enumerate((izq, centro, der)):
        celda(i, 0, v)
    celda(1, 1, piso)
    # X pequeña dibujada píxel a píxel
    color = tema.TAPETE if piso == OSCURO else tema.TINTA
    m = lado // 4
    for d in range(lado // 2 + 1):
        for x, y in ((lado + m + d, lado + m + d), (2 * lado - m - d, lado + m + d)):
            img.put(color, to=(x, y, x + 2, y + 2))
    return img
