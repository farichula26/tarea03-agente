"""Chequeos mínimos de la lógica del agente. Ejecutar: uv run python -m tests.test_agente"""
from agent.ambiente import AVANZAR, BORDE, CLARO, OSCURO, ROTAR_DER, ROTAR_IZQ, aplicar_accion, generar_ambiente, percibir
from agent.reglas import decidir, numero_caso, tabla_percepcion_accion
from agent.simulacion import estadisticas, nuevo_estado, paso, siguiente


def p(piso, izq, centro, der, contacto=False):
    return {"orientacion": 0, "contacto": contacto, "piso": piso, "izq": izq, "centro": centro, "der": der}


def main():
    # Numeración de casos según la página 2 del enunciado
    assert numero_caso(p(CLARO, CLARO, CLARO, CLARO)) == 1
    assert numero_caso(p(CLARO, CLARO, CLARO, OSCURO)) == 2
    assert numero_caso(p(CLARO, CLARO, CLARO, BORDE)) == 3
    assert numero_caso(p(CLARO, OSCURO, CLARO, CLARO)) == 10
    assert numero_caso(p(OSCURO, BORDE, BORDE, BORDE)) == 54
    assert [f[0] for f in tabla_percepcion_accion()] == list(range(1, 55))

    # Reglas
    assert decidir(p(CLARO, CLARO, CLARO, CLARO, contacto=True)) == ("R1", (ROTAR_DER,))
    assert decidir(p(OSCURO, CLARO, OSCURO, OSCURO))[0] == "R2"
    assert decidir(p(OSCURO, OSCURO, OSCURO, CLARO))[0] == "R3"
    assert decidir(p(OSCURO, OSCURO, OSCURO, OSCURO)) == ("R4", (AVANZAR,))
    assert decidir(p(CLARO, OSCURO, CLARO, CLARO)) == ("R5", (AVANZAR, ROTAR_IZQ))
    assert decidir(p(CLARO, CLARO, CLARO, OSCURO))[0] == "R6"
    assert decidir(p(OSCURO, BORDE, BORDE, BORDE)) == ("R7", (ROTAR_DER,))
    assert decidir(p(OSCURO, CLARO, CLARO, CLARO)) == ("R8", (AVANZAR,))

    # Cámaras relativas a la orientación (▶ en la esquina superior izquierda)
    g = [[CLARO, OSCURO], [CLARO, CLARO]]
    assert percibir(g, (0, 0), 1, False) == {"orientacion": 1, "contacto": False, "piso": CLARO,
                                                  "izq": BORDE, "centro": OSCURO, "der": CLARO}
    # Choque con el borde
    assert aplicar_accion(g, (0, 0), 0, AVANZAR) == ((0, 0), 0, True)

    # siguiente() anticipa el próximo paso sin modificar el estado
    e = nuevo_estado(generar_ambiente(8, 10, 3), (0, 0), 1)
    d, antes = siguiente(e), (e["pos"], e["orient"], e["iter"])
    assert (e["pos"], e["orient"], e["iter"]) == antes
    r = paso(e)
    assert (r["regla"], r["caso"], r["acciones"]) == (d["regla"], d["caso"], d["acciones"])

    # Siempre termina en bucle y las 12 preguntas tienen respuesta
    for semilla in range(30):
        grid = generar_ambiente(8, 10, semilla)
        e = nuevo_estado(grid, (0, 0), 1)
        while paso(e):
            assert e["iter"] <= 8 * 8 * 10
        assert e["bucle"] and len(estadisticas(e)) == 12
    print("OK")


if __name__ == "__main__":
    main()
