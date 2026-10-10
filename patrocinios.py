import random
from economia import Sponsor


class OfertaSponsor:
  def __init__(self, sponsor, requisito_reputacion=0, bono_firma=0):
    self.sponsor = sponsor
    self.requisito_reputacion = requisito_reputacion
    self.bono_firma = bono_firma
    self.estado = "disponible"

  def aceptar(self, jugador):
    if self.estado != "disponible":
      return False

    if jugador.vinculos.get("hinchada", 0) < self.requisito_reputacion:
      return False

    if not jugador.agregar_sponsor(self.sponsor):
      return False

    jugador.dinero += self.bono_firma
    self.estado = "aceptada"
    return True

  def rechazar(self):
    if self.estado != "disponible":
      return False
    self.estado = "rechazada"
    return True


class BolsaSponsors:
  CATALOGO = [
    ("Marca deportiva local", "local", "indumentaria", 1200, 26, 0, 0),
    ("Marca de botines", "deportivo", "calzado", 3500, 40, 10, 5000),
    ("Marca de bebidas", "local", "bebidas", 1800, 30, 5, 2000),
    ("Marca tecnológica", "deportivo", "tecnologia", 4200, 36, 15, 7000),
    ("Marca de automóviles", "deluxe", "automoviles", 9000, 52, 35, 15000),
    ("Marca de indumentaria premium", "deluxe", "indumentaria", 10000, 52, 50, 20000)
  ]

  def __init__(self):
    self.ofertas = []
    self.ultima_actualizacion = 0

  def actualizar(self, semana, cantidad=3):
    if semana == self.ultima_actualizacion:
      return self.ofertas

    disponibles = self.CATALOGO.copy()
    random.shuffle(disponibles)
    seleccionadas = disponibles[:cantidad]
    self.ofertas = []

    for nombre, nivel, categoria, pago, duracion, reputacion, bono in seleccionadas:
      sponsor = Sponsor(
        nombre,
        nivel,
        pago,
        duracion,
        categoria_comercial=categoria
      )
      self.ofertas.append(
        OfertaSponsor(sponsor, reputacion, bono)
      )

    self.ultima_actualizacion = semana
    return self.ofertas
