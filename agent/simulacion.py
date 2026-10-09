"""Ciclo percibir → decidir → actuar y estadísticas de la hoja ESTADÍSTICOS."""
from agent.ambiente import AVANZAR, OSCURO, ROTAR_DER, ROTAR_IZQ, aplicar_accion, percibir
from agent.reglas import REGLAS, decidir, numero_caso


def nuevo_estado(grid, pos, orient):
    return {
        "grid": grid, "inicio": pos, "orient_inicio": orient,
        "pos": pos, "orient": orient, "contacto": False, "iter": 0,
        "historial": [], "marcas": {},
        "vistos": {(pos, orient, False): 0}, "bucle": None,
        "visitadas": {pos}, "toco_linea": grid[pos[0]][pos[1]] == OSCURO,
        "avances": 0, "rot_izq": 0, "rot_der": 0, "choques": 0, "choques_antes_linea": 0,
    }


def siguiente(e):
    """Lo que el agente percibe ahora y la regla que aplicará en el próximo paso (no modifica el estado)."""
    p = percibir(e["grid"], e["pos"], e["orient"], e["contacto"])
    regla, acciones = decidir(p)
    return {"percepcion": p, "caso": numero_caso(p), "regla": regla, "acciones": acciones}


def paso(e):
    """Ejecuta una iteración. Devuelve el registro, o None si ya se detectó el bucle."""
    if e["bucle"]:
        return None
    d = siguiente(e)
    p, regla, acciones = d["percepcion"], d["regla"], d["acciones"]
    desde, orient_desde = e["pos"], e["orient"]
    contacto = False
    for accion in acciones:  # una o dos acciones, siempre una luego de la otra
        e["pos"], e["orient"], choco = aplicar_accion(e["grid"], e["pos"], e["orient"], accion)
        if choco:
            contacto = True
            e["choques"] += 1
            e["choques_antes_linea"] += not e["toco_linea"]
        elif accion == AVANZAR:
            e["avances"] += 1
        e["rot_izq"] += accion == ROTAR_IZQ
        e["rot_der"] += accion == ROTAR_DER
        e["visitadas"].add(e["pos"])
        e["toco_linea"] |= e["grid"][e["pos"][0]][e["pos"][1]] == OSCURO
    e["contacto"] = contacto
    e["iter"] += 1
    registro = {"iter": e["iter"], "desde": desde, "orient_desde": orient_desde, "percepcion": p,
                "caso": d["caso"], "regla": regla, "acciones": acciones,
                "pos": e["pos"], "orient": e["orient"], "choco": contacto}
    e["historial"].append(registro)
    e["marcas"][desde] = registro  # la casilla muestra la regla/caso con que se decidió ahí

    # Agente determinista + ambiente estático: si el estado se repite, se repetirá para siempre.
    clave = (e["pos"], e["orient"], e["contacto"])
    if clave in e["vistos"]:
        entrada = e["vistos"][clave]
        e["bucle"] = {"entrada": entrada, "detectado": e["iter"], "longitud": e["iter"] - entrada}
    else:
        e["vistos"][clave] = e["iter"]
    return registro


def celdas_del_ciclo(e):
    """Casillas desde las que se decide dentro del bucle (para resaltarlas)."""
    if not e["bucle"]:
        return set()
    return {r["desde"] for r in e["historial"][e["bucle"]["entrada"]:]}


def estadisticas(e):
    """Lista (pregunta, respuesta) en el orden de la hoja ESTADÍSTICOS del enunciado."""
    grid = e["grid"]
    n, m = len(grid), len(grid[0])
    reglas = sorted({r["regla"] for r in e["historial"]}, key=lambda rid: int(rid[1:]))
    total_linea = sum(fila.count(OSCURO) for fila in grid)
    linea_visitada = sum(grid[r][c] == OSCURO for r, c in e["visitadas"])
    pct = 100 * linea_visitada / total_linea if total_linea else 0
    retorno = next((r["iter"] for r in e["historial"] if r["pos"] == e["inicio"] and r["desde"] != e["inicio"]), None)
    b = e["bucle"]

    return [
        ("Número de reglas que ha usado al menos 1 vez",
         f"{len(reglas)}: {', '.join(reglas) or '—'}"),
        ("Número de veces que el agente choca con la pared antes de llegar a la línea por primera vez",
         f"{e['choques_antes_linea']} (choques totales: {e['choques']}). "
         "Se interpreta «succionar basura» como «llegar a la línea»."),
        ("Número de veces que el agente avanza (sin contar rotaciones)", str(e["avances"])),
        ("Número de veces que el agente rota +90 o -90",
         f"{e['rot_izq'] + e['rot_der']} (+90: {e['rot_izq']}, -90: {e['rot_der']})"),
        ("Desempeño del agente",
         f"{linea_visitada} de {total_linea} celdas de línea recorridas = {pct:.1f} %. "
         "Desempeño = celdas oscuras distintas pisadas ÷ total de celdas oscuras × 100."),
        ("¿El agente retorna a su posición inicial?",
         f"Sí, en la iteración {retorno}." if retorno else "No, hasta esta iteración."),
        ("¿El ambiente es dinámico?",
         "No. Es estático: la malla no cambia mientras el agente actúa; solo cambia la posición del agente."),
        ("¿El ambiente es episódico?",
         "No. Es secuencial: cada acción cambia la posición y con ella las percepciones siguientes. "
         "El agente, por ser reflejo simple, decide como si cada percepción fuera un episodio aislado."),
        ("¿El ambiente es accesible?",
         "No. Es parcialmente accesible: el agente solo percibe su celda y las 3 celdas de adelante."),
        ("Número de iteraciones hasta que el agente entra en bucle infinito",
         f"Entra al bucle en la iteración {b['entrada']}; se confirma en la {b['detectado']} "
         f"(ciclo de {b['longitud']} iteraciones)." if b else f"Aún no detectado (iteración {e['iter']})."),
        ("Complejidad del agente (hasta que termina su operación)",
         f"Cada decisión es O(1): evalúa a lo sumo {len(REGLAS)} reglas fijas. Como el estado es "
         f"(fila, columna, orientación, contacto), hay como máximo 8·N·M = {8 * n * m} estados, "
         f"así que el agente entra en bucle en O(N·M) iteraciones. Aquí: {e['iter']} iteraciones."),
        ("Si el agente entra en bucle infinito, ¿cómo se hace el cálculo?",
         "El agente no puede saberlo (no tiene memoria). El simulador guarda cada estado "
         "(fila, columna, orientación, contacto) con la iteración en que apareció. Como el agente es "
         "determinista y el ambiente estático, si un estado reaparece todo se repetirá: entrada = iteración "
         "guardada, longitud del ciclo = iteración actual − entrada."),
    ]
