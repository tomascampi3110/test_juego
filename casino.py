import random


class Casino:
  """Juegos de azar con dinero virtual de la carrera."""

  def __init__(self, apuesta_minima=100, apuesta_maxima=10000):
    self.apuesta_minima = apuesta_minima
    self.apuesta_maxima = apuesta_maxima
    self.historial = []

  def jugar_ruleta(self, jugador, apuesta, eleccion):
    opciones = {"rojo": (18, 2), "negro": (18, 2), "par": (18, 2), "impar": (18, 2)}
    if eleccion not in opciones and not (eleccion.isdigit() and 0 <= int(eleccion) <= 36):
      return {"ok": False, "mensaje": "Elegí rojo, negro, par, impar o un número del 0 al 36."}
    if not self._apuesta_valida(jugador, apuesta):
      return {"ok": False, "mensaje": "La apuesta no es válida."}
    numero = random.randint(0, 36)
    rojo = numero in {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    color = "verde" if numero == 0 else ("rojo" if rojo else "negro")
    gana = (eleccion == color or (eleccion == "par" and numero != 0 and numero % 2 == 0) or (eleccion == "impar" and numero % 2 == 1) or (eleccion.isdigit() and int(eleccion) == numero))
    multiplicador = 36 if eleccion.isdigit() else (2 if eleccion in ("rojo", "negro", "par", "impar") else 0)
    return self._resolver(jugador, apuesta, "ruleta", eleccion, f"Salió {numero} ({color}).", apuesta * multiplicador if gana else 0)

  def jugar_tragamonedas(self, jugador, apuesta):
    if not self._apuesta_valida(jugador, apuesta):
      return {"ok": False, "mensaje": "La apuesta no es válida."}
    simbolos = ["🍒", "🍋", "🔔", "⭐", "7️⃣"]
    resultado = [random.choice(simbolos) for _ in range(3)]
    if resultado[0] == resultado[1] == resultado[2]:
      mult = {"🍒": 3, "🍋": 4, "🔔": 6, "⭐": 10, "7️⃣": 20}[resultado[0]]
    elif len(set(resultado)) == 2:
      mult = 1
    else:
      mult = 0
    return self._resolver(jugador, apuesta, "tragamonedas", "girar", "Resultado: " + " | ".join(resultado), apuesta * mult)

  def jugar_carrera_caballos(self, jugador, apuesta, caballo):
    if not self._apuesta_valida(jugador, apuesta):
      return {"ok": False, "mensaje": "La apuesta no es válida."}
    caballos = {"Relámpago": 2.2, "Tormenta": 3.0, "Centella": 4.0, "Sombra": 5.0}
    if caballo not in caballos:
      return {"ok": False, "mensaje": "Elegí un caballo disponible."}
    ganador = random.choices(list(caballos), weights=[1 / caballos[n] for n in caballos], k=1)[0]
    return self._resolver(jugador, apuesta, "caballos", caballo, f"Ganó {ganador}.", round(apuesta * caballos[caballo]) if ganador == caballo else 0)

  def apostar_partido(self, jugador, apuesta, favorito, probabilidad=None):
    if not self._apuesta_valida(jugador, apuesta):
      return {"ok": False, "mensaje": "La apuesta no es válida."}
    probabilidad = max(0.15, min(0.85, float(probabilidad if probabilidad is not None else 0.5)))
    gana = random.random() < probabilidad
    cuota = round(1 / probabilidad, 2)
    return self._resolver(jugador, apuesta, "apuesta_deportiva", favorito, f"El resultado favoreció a {favorito}." if gana else f"No se dio el resultado esperado para {favorito}.", round(apuesta * cuota) if gana else 0)

  def jugar_moneda(self, jugador, apuesta, eleccion):
    if eleccion not in ("cara", "cruz"):
      return {"ok": False, "mensaje": "Elegí cara o cruz."}
    if not self._apuesta_valida(jugador, apuesta):
      return {"ok": False, "mensaje": "La apuesta no es válida."}
    resultado = random.choice(["cara", "cruz"])
    return self._resolver(jugador, apuesta, "moneda", eleccion, f"Salió {resultado}.", apuesta * 2 if resultado == eleccion else 0)

  def jugar_dados(self, jugador, apuesta, objetivo=4):
    if not self._apuesta_valida(jugador, apuesta) or not 2 <= objetivo <= 6:
      return {"ok": False, "mensaje": "La apuesta o el objetivo no son válidos."}
    dado = random.randint(1, 6)
    gana = dado >= objetivo
    multiplicador = 6 / (7 - objetivo) if gana else 0
    return self._resolver(jugador, apuesta, "dados", objetivo, f"El dado marcó {dado}.", round(apuesta * multiplicador) if gana else 0)

  def _resolver(self, jugador, apuesta, juego, eleccion, mensaje, ganancia):
    jugador.dinero -= apuesta
    jugador.dinero += ganancia
    registro = {"juego": juego, "apuesta": apuesta, "eleccion": eleccion, "resultado": mensaje, "ganancia": ganancia, "neto": ganancia - apuesta}
    self.historial.append(registro)
    return {"ok": True, "mensaje": mensaje, **registro, "dinero": jugador.dinero}

  def _apuesta_valida(self, jugador, apuesta):
    return isinstance(apuesta, int) and self.apuesta_minima <= apuesta <= self.apuesta_maxima and apuesta <= jugador.dinero
