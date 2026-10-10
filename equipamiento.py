class Equipamiento:
  ESPACIOS_VALIDOS = {
    "botines",
    "canilleras",
    "accesorio"
  }

  def __init__(
    self,
    nombre,
    espacio,
    precio,
    atributos=None,
    durabilidad_partidos=10,
    reduccion_riesgo_lesion=0,
    duracion_semanas=None
  ):
    if espacio not in self.ESPACIOS_VALIDOS:
      raise ValueError("Espacio de equipamiento no válido")

    self.nombre = nombre
    self.espacio = espacio
    self.precio = max(0, int(precio))
    self.atributos = dict(atributos or {})
    self.durabilidad_maxima = max(1, int(durabilidad_partidos))
    self.durabilidad = self.durabilidad_maxima
    self.reduccion_riesgo_lesion = max(
      0,
      min(0.90, float(reduccion_riesgo_lesion))
    )
    self.duracion_semanas = duracion_semanas
    self.semanas_restantes = duracion_semanas
    self.activo = True

  def desgastar(self, cantidad=1):
    if not self.activo:
      return False

    self.durabilidad = max(0, self.durabilidad - cantidad)
    if self.durabilidad == 0:
      self.activo = False

    return self.activo

  def avanzar_semana(self):
    if not self.activo or self.semanas_restantes is None:
      return

    self.semanas_restantes -= 1
    if self.semanas_restantes <= 0:
      self.semanas_restantes = 0
      self.activo = False

  def obtener_reduccion_lesion(self):
    if not self.activo or self.espacio != "canilleras":
      return 0

    return self.reduccion_riesgo_lesion

  def __str__(self):
    return (
      f"{self.nombre} | {self.espacio} | "
      f"durabilidad {self.durabilidad}/{self.durabilidad_maxima}"
    )
