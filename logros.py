class Logro:
  def __init__(self, identificador, nombre, descripcion, dinero=0, xp=0):
    self.identificador = identificador
    self.nombre = nombre
    self.descripcion = descripcion
    self.dinero = dinero
    self.xp = xp


class SistemaLogros:
  LOGROS = [
    Logro("debut", "Debut profesional", "Jugaste tu primer partido.", 1000, 5),
    Logro("hat_trick", "Hat-trick", "Marcaste tres goles en un partido.", 5000, 20),
    Logro("nota_10", "Partido perfecto", "Conseguiste una nota de 10.", 3000, 15),
    Logro("primer_sponsor", "Imagen de marca", "Firmaste tu primer patrocinio.", 1500, 10),
    Logro("primer_millon", "Millonario", "Acumulaste un millón de dinero virtual.", 10000, 25),
    Logro("vinculo_hinchada", "Ídolo de la hinchada", "Llegaste a 90 de vínculo con la hinchada.", 5000, 20),
    Logro("campeon", "Campeón", "Ganaste un título con tu club.", 15000, 40)
  ]

  def actualizar(self, jugador, contexto=None):
    contexto = contexto or {}
    desbloqueados = []

    for logro in self.LOGROS:
      if logro.identificador in jugador.logros:
        continue

      if not self._cumple(jugador, logro.identificador, contexto):
        continue

      jugador.logros.add(logro.identificador)
      jugador.dinero += logro.dinero
      bonificador = getattr(jugador, "bonificadores", {}).get("experiencia", 1.0)
      puntos = round(logro.xp * bonificador)
      jugador.puntos_xp += puntos
      jugador.puntos_mejora += puntos
      desbloqueados.append(logro)

    return desbloqueados

  def _cumple(self, jugador, identificador, contexto):
    if identificador == "debut":
      return jugador.partidos_jugados >= 1
    if identificador == "hat_trick":
      return contexto.get("goles", 0) >= 3
    if identificador == "nota_10":
      return contexto.get("nota", 0) >= 9.95
    if identificador == "primer_sponsor":
      return len(jugador.sponsors) >= 1
    if identificador == "primer_millon":
      return jugador.dinero >= 1_000_000
    if identificador == "vinculo_hinchada":
      return jugador.vinculos.get("hinchada", 0) >= 90
    if identificador == "campeon":
      return jugador.titulos >= 1
    return False
