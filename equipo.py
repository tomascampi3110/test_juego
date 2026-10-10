from jugador import Jugador

class Equipo:
  def __init__(
    self,
    nombre: str,
    estadio: str,
    dt: str,
    liga
  ):
    self.nombre = nombre
    self.estadio = estadio
    self.dt = dt
    self.liga = liga

    self.presupuesto = 0
    self.trofeos = 0
    self.valoracion = 0

    self.jugadores = []
    self.alineacion = []

    self.gf = 0
    self.gc = 0
    self.pts = 0
    self.pj = 0
    self.g = 0
    self.e = 0
    self.p = 0

  def incorporar_jugador(
    self,
    jugador: Jugador,
    otro_equipo: "Equipo"
  ):
    if jugador not in otro_equipo.jugadores:
      return

    if jugador in self.jugadores:
      return

    self.jugadores.append(jugador)
    otro_equipo.jugadores.remove(jugador)

    jugador.equipo = self
    jugador.habilitado = True

    return self.jugadores

  def vender_jugador(
    self,
    jugador: Jugador,
    otro_equipo: "Equipo"
  ):
    if jugador not in self.jugadores:
      return

    otro_equipo.incorporar_jugador(
      jugador,
      self
    )

  def agregar_jugador(
    self,
    jugador: Jugador
  ):
    if jugador in self.jugadores:
      return

    self.jugadores.append(jugador)
    jugador.equipo = self
    jugador.habilitado = True

  def eliminar_jugador(
    self,
    jugador: Jugador
  ):
    if jugador not in self.jugadores:
      return

    self.jugadores.remove(jugador)

    if jugador.equipo == self:
      jugador.equipo = None

  def obtener_jugadores_disponibles(self):
    disponibles = []

    for jugador in self.jugadores:
      if jugador.esta_disponible():
        disponibles.append(jugador)

    return disponibles

  def puede_comprar(self, monto):
    return self.presupuesto >= monto

  def pagar_transferencia(self, monto):
    if monto <= 0:
      return False

    if self.presupuesto < monto:
      return False

    self.presupuesto -= monto
    return True

  def cobrar_transferencia(self, monto):
    if monto <= 0:
      return False

    self.presupuesto += monto
    return True

  def actualizar_valoracion(self):
    if not self.jugadores:
      self.valoracion = 0
      return

    suma = 0

    for jugador in self.jugadores:
      suma += jugador.valoracion

    self.valoracion = round(
      suma / len(self.jugadores)
    )


