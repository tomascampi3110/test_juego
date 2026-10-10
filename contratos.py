from jugador import Jugador

class Contrato:
  def __init__(
    self,
    jugador,
    club,
    salario_semanal,
    duracion_semanas,
    clausula_rescision=0
  ):
    self.jugador = jugador
    self.club = club

    self.salario_semanal = salario_semanal

    self.duracion_semanas = (
      duracion_semanas
    )

    self.semanas_restantes = (
      duracion_semanas
    )

    self.clausula_rescision = (
      clausula_rescision
    )

    self.bonos = {}

    self.activo = True

  def agregar_bono(
    self,
    nombre,
    cantidad
  ):
    if cantidad <= 0:
      return

    self.bonos[nombre] = cantidad

  def eliminar_bono(
    self,
    nombre
  ):
    if nombre in self.bonos:
      del self.bonos[nombre]

  def obtener_bono(
    self,
    nombre
  ):
    return self.bonos.get(
      nombre,
      0
    )

  def cobrar_salario(
    self
  ):
    if not self.activo:
      return 0

    self.jugador.dinero += (
      self.salario_semanal
    )

    return self.salario_semanal

  def cobrar_bono(
    self,
    nombre
  ):
    cantidad = self.obtener_bono(
      nombre
    )

    if cantidad <= 0:
      return 0

    self.jugador.dinero += cantidad

    return cantidad

  def avanzar_semana(
    self
  ):
    if not self.activo:
      return

    self.cobrar_salario()

    self.semanas_restantes -= 1

    if self.semanas_restantes <= 0:
      self.semanas_restantes = 0
      self.activo = False

  def esta_vigente(
    self
  ):
    return self.activo

  def __str__(
    self
  ):
    return (
      f"Club: {self.club.nombre}\n"
      f"Salario semanal: "
      f"${self.salario_semanal}\n"
      f"Semanas restantes: "
      f"{self.semanas_restantes}\n"
      f"Cláusula de rescisión: "
      f"${self.clausula_rescision}"
    )


class Representante:
  def __init__(
    self,
    nombre,
    nivel=1,
    comision=5
  ):
    self.nombre = nombre
    self.nivel = nivel
    self.comision = comision

    self.negociacion = 10
    self.bonos = 10
    self.sponsors = 10
    self.reputacion = 10

    self.jugador = None

  def asignar_jugador(
    self,
    jugador
  ):
    self.jugador = jugador

  def calcular_comision(
    self,
    contrato
  ):
    valor_contrato = (
      contrato.salario_semanal
      * contrato.duracion_semanas
    )

    return (
      valor_contrato
      * self.comision
      / 100
    )

  def cobrar_comision(
    self,
    contrato
  ):
    if self.jugador is None:
      return 0

    comision = self.calcular_comision(
      contrato
    )

    if self.jugador.dinero < comision:
      return 0

    self.jugador.dinero -= comision

    return comision

  def mejorar_habilidad(
    self,
    habilidad,
    cantidad
  ):
    if cantidad <= 0:
      return

    if not hasattr(
      self,
      habilidad
    ):
      return

    valor_actual = getattr(
      self,
      habilidad
    )

    nuevo_valor = (
      valor_actual
      + cantidad
    )

    nuevo_valor = min(
      nuevo_valor,
      100
    )

    setattr(
      self,
      habilidad,
      nuevo_valor
    )

  def subir_nivel(
    self
  ):
    if self.nivel >= 100:
      return

    self.nivel += 1

  def obtener_habilidad(
    self,
    habilidad
  ):
    return getattr(
      self,
      habilidad,
      0
    )

  def __str__(
    self
  ):
    return (
      f"Representante: "
      f"{self.nombre}\n"
      f"Nivel: {self.nivel}\n"
      f"Comisión: "
      f"{self.comision}%\n"
      f"Negociación: "
      f"{self.negociacion}\n"
      f"Bonos: "
      f"{self.bonos}\n"
      f"Sponsors: "
      f"{self.sponsors}\n"
      f"Reputación: "
      f"{self.reputacion}"
    )

