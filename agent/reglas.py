"""Tabla percepción → acción del agente reflejo simple."""
from agent.ambiente import AVANZAR, BORDE, CLARO, OSCURO, ROTAR_DER, ROTAR_IZQ

# (id, descripción, condición, acciones). Se evalúan en orden: gana la primera que se cumple.
# La orientación no interviene: las cámaras son relativas al agente.
REGLAS = (
    ("R1", "Chocó con la pared: girar a la derecha",
     lambda p: p["contacto"], (ROTAR_DER,)),
    ("R2", "Curva a la derecha: avanzar y girar a la derecha",
     lambda p: p["centro"] == OSCURO and p["der"] == OSCURO and p["izq"] != OSCURO, (AVANZAR, ROTAR_DER)),
    ("R3", "Curva a la izquierda: avanzar y girar a la izquierda",
     lambda p: p["centro"] == OSCURO and p["izq"] == OSCURO and p["der"] != OSCURO, (AVANZAR, ROTAR_IZQ)),
    ("R4", "Línea al centro: seguir recto",
     lambda p: p["centro"] == OSCURO, (AVANZAR,)),
    ("R5", "Línea en diagonal izquierda: avanzar y girar a la izquierda",
     lambda p: p["centro"] == CLARO and p["izq"] == OSCURO, (AVANZAR, ROTAR_IZQ)),
    ("R6", "Línea en diagonal derecha: avanzar y girar a la derecha",
     lambda p: p["centro"] == CLARO and p["der"] == OSCURO, (AVANZAR, ROTAR_DER)),
    ("R7", "Borde adelante: girar a la derecha",
     lambda p: p["centro"] == BORDE, (ROTAR_DER,)),
    ("R8", "Sin línea adelante (fin o corte): avanzar por celdas claras buscando línea",
     lambda p: True, (AVANZAR,)),
)
DESCRIPCION = {rid: desc for rid, desc, _, _ in REGLAS}


def numero_caso(p):
    """Caso C1..C54 en el orden de la página 2 del enunciado (claro, oscuro, pared)."""
    return p["piso"] * 27 + p["izq"] * 9 + p["centro"] * 3 + p["der"] + 1


def decodificar_caso(caso):
    """Inverso de numero_caso: (piso, izq, centro, der)."""
    k = caso - 1
    return k // 27, k // 9 % 3, k // 3 % 3, k % 3


def decidir(p):
    for rid, _, condicion, acciones in REGLAS:
        if condicion(p):
            return rid, acciones


def tabla_percepcion_accion():
    """Una fila por caso (sin contacto): (caso, piso, izq, centro, der, regla, acciones)."""
    filas = []
    for caso in range(1, 55):
        piso, izq, centro, der = decodificar_caso(caso)
        rid, acciones = decidir({"contacto": False, "piso": piso, "izq": izq, "centro": centro, "der": der})
        filas.append((caso, piso, izq, centro, der, rid, acciones))
    return filas
