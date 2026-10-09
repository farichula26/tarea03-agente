"""Ambiente: malla NxM con líneas oscuras generadas al azar."""
import random

CLARO, OSCURO, BORDE = 0, 1, 2
NOMBRE_VALOR = {CLARO: "Piso no oscuro", OSCURO: "Piso oscuro", BORDE: "Borde"}

# Orientaciones en sentido horario: índice 0..3
ORIENTACIONES = ("▲", "▶", "▼", "◀")
DELTAS = ((-1, 0), (0, 1), (1, 0), (0, -1))

AVANZAR, ROTAR_IZQ, ROTAR_DER = "Avanzar", "Rotar +90", "Rotar -90"


def dentro(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def celda(grid, r, c):
    return grid[r][c] if dentro(grid, r, c) else BORDE


def generar_ambiente(n, m, semilla=None):
    """Malla n x m con 1 o 2 líneas trazadas por caminata aleatoria (con curvas, cortes y ancho 1-2)."""
    rng = random.Random(semilla)
    grid = [[CLARO] * m for _ in range(n)]
    for _ in range(rng.randint(1, 2)):
        _trazar_linea(grid, rng)
    return grid


def _trazar_linea(grid, rng):
    n, m = len(grid), len(grid[0])
    d = rng.randrange(4)
    dr, dc = DELTAS[d]
    # Empieza en el borde opuesto a la dirección en que avanza
    r = n - 1 if dr == -1 else 0 if dr == 1 else rng.randrange(n)
    c = m - 1 if dc == -1 else 0 if dc == 1 else rng.randrange(m)
    ancho = 2 if rng.random() < 0.3 else 1
    hueco = tramo = 0
    for _ in range(3 * (n + m)):
        if not dentro(grid, r, c):
            break
        if hueco:
            hueco -= 1
        else:
            grid[r][c] = OSCURO
            if ancho == 2:
                lr, lc = r + DELTAS[(d + 1) % 4][0], c + DELTAS[(d + 1) % 4][1]
                if dentro(grid, lr, lc):
                    grid[lr][lc] = OSCURO
            if tramo > 2 and rng.random() < 0.06:
                hueco = rng.randint(1, 2)  # línea discontinua
        tramo += 1
        if tramo > 3 and rng.random() < 0.2:
            d = (d + rng.choice((1, 3))) % 4
            tramo = 0
        r, c = r + DELTAS[d][0], c + DELTAS[d][1]


def posicion_inicial(grid):
    """Primera celda oscura (orden de lectura) mirando hacia donde sigue la línea."""
    for r, fila in enumerate(grid):
        for c, v in enumerate(fila):
            if v == OSCURO:
                for o in range(4):
                    if celda(grid, r + DELTAS[o][0], c + DELTAS[o][1]) == OSCURO:
                        return (r, c), o
                return (r, c), 0
    return (len(grid) // 2, len(grid[0]) // 2), 0


def camaras(pos, orient):
    """Coordenadas (izquierda, centro, derecha) de la fila de adelante, relativas a la orientación."""
    r, c = pos
    fr, fc = DELTAS[orient]
    lr, lc = DELTAS[(orient + 3) % 4]
    cr, cc = r + fr, c + fc
    return (cr + lr, cc + lc), (cr, cc), (cr - lr, cc - lc)


def percibir(grid, pos, orient, contacto):
    izq, centro, der = (celda(grid, *p) for p in camaras(pos, orient))
    return {"orientacion": orient, "contacto": contacto, "piso": grid[pos[0]][pos[1]],
            "izq": izq, "centro": centro, "der": der}


def aplicar_accion(grid, pos, orient, accion):
    """Devuelve (pos, orient, choco)."""
    if accion == ROTAR_IZQ:
        return pos, (orient + 3) % 4, False
    if accion == ROTAR_DER:
        return pos, (orient + 1) % 4, False
    nr, nc = pos[0] + DELTAS[orient][0], pos[1] + DELTAS[orient][1]
    if not dentro(grid, nr, nc):
        return pos, orient, True
    return (nr, nc), orient, False
