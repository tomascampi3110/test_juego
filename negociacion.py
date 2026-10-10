import random
from contratos import Contrato


class NegociacionContrato:
  def __init__(self, jugador, club, salario_ofrecido, duracion_semanas=52):
    self.jugador = jugador
    self.club = club
    self.salario_ofrecido = max(1000, int(salario_ofrecido))
    self.duracion_semanas = duracion_semanas
    self.intento = jugador.intentos_negociacion + 1
    self.flexibilidad = self._calcular_flexibilidad()
    self.objetivo = self._calcular_objetivo()
    self.finalizada = False

  def _calcular_flexibilidad(self):
    valor = 0.12
    valor += max(0, self.jugador.vinculos.get("club", 50) - 50) / 500
    valor += max(0, self.jugador.vinculos.get("entrenador", 50) - 50) / 700
    valor += max(0, self.jugador.vinculos.get("gerente", 50) - 50) / 800
    valor += max(0, self.jugador.forma - 50) / 1000
    valor += min(0.12, self.jugador.semanas_desde_ultimo_contrato / 520)
    valor -= self.jugador.negociaciones_fallidas * 0.04

    if self.jugador.contrato is not None and self.jugador.contrato.esta_vigente():
      if self.jugador.contrato.semanas_restantes > 39:
        valor -= 0.08

    return max(0.03, min(0.35, valor))

  def _calcular_objetivo(self):
    objetivo = 50 + (self.jugador.forma - 50) * 0.35
    objetivo += (self.jugador.vinculos.get("club", 50) - 50) * 0.15
    objetivo += (self.jugador.vinculos.get("gerente", 50) - 50) * 0.05
    return max(25, min(75, objetivo))

  def intentar_acuerdo(self, posicion_mano):
    if self.finalizada:
      return {"ok": False, "mensaje": "La negociación ya terminó."}

    posicion_mano = max(0, min(100, float(posicion_mano)))
    self.jugador.intentos_negociacion += 1

    objetivo = self.objetivo
    margen = 7 + self.flexibilidad * 35
    distancia = abs(posicion_mano - objetivo)

    if distancia > margen:
      self.jugador.negociaciones_fallidas += 1
      self.finalizada = True
      return {
        "ok": False,
        "mensaje": "El club no acepta las condiciones. Podés intentarlo más adelante.",
        "objetivo": round(objetivo, 1),
        "margen": round(margen, 1)
      }

    mejora = 1 + (self.flexibilidad * (1 - distancia / max(margen, 1)))
    salario = round(self.salario_ofrecido * mejora)
    contrato = Contrato(
      self.jugador,
      self.club,
      salario,
      self.duracion_semanas
    )

    self.jugador.contrato = contrato
    self.jugador.semanas_desde_ultimo_contrato = 0
    self.jugador.intentos_negociacion = 0
    self.jugador.negociaciones_fallidas = 0
    self.jugador.vinculos["club"] = min(
      100,
      self.jugador.vinculos.get("club", 50) + 2
    )
    self.finalizada = True

    return {
      "ok": True,
      "mensaje": "¡Se estrecharon las manos! Contrato firmado.",
      "salario_semanal": salario,
      "contrato": contrato,
      "objetivo": round(objetivo, 1)
    }

  def pedir_renovacion(self):
    if self.jugador.semanas_desde_ultimo_contrato < 8:
      return {
        "ok": False,
        "mensaje": "El club considera que es demasiado pronto para renegociar."
      }

    if self.jugador.historial_notas and sum(self.jugador.historial_notas[-5:]) / len(self.jugador.historial_notas[-5:]) < 4.5:
      return {
        "ok": False,
        "mensaje": "El club quiere ver una mejora en tu rendimiento antes de renovar."
      }

    return {"ok": True, "mensaje": "El club acepta abrir una negociación."}

  def pedir_lista_transferibles(self):
    self.jugador.solicitar_lista_transferibles()
    return {
      "ok": True,
      "mensaje": "Solicitaste quedar en la lista de transferibles. La dirigencia evaluará la petición."
    }
