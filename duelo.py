import random

class Duelo:
  TIPOS = {
    "aereo": {
      "jugador_1": {
        "salto": 0.40,
        "fuerza": 0.25,
        "precision": 0.35
      },
      "jugador_2": {
        "salto": 0.35,
        "fuerza": 0.30,
        "marca": 0.35
      }
    },

    "uno_contra_uno": {
      "jugador_1": {
        "velocidad": 0.25,
        "regate": 0.40,
        "control": 0.20,
        "reaccion": 0.15
      },
      "jugador_2": {
        "velocidad": 0.25,
        "marca": 0.40,
        "reaccion": 0.20,
        "anticipacion": 0.15
      }
    },

    "cuerpo_a_cuerpo": {
      "jugador_1": {
        "fuerza": 0.50,
        "equilibrio": 0.20,
        "resistencia": 0.30
      },
      "jugador_2": {
        "fuerza": 0.50,
        "equilibrio": 0.20,
        "resistencia": 0.30
      }
    },

    "pelota_dividida": {
      "jugador_1": {
        "reaccion": 0.35,
        "velocidad": 0.30,
        "anticipacion": 0.35
      },
      "jugador_2": {
        "reaccion": 0.35,
        "velocidad": 0.30,
        "anticipacion": 0.35
      }
    },

    "pase": {
      "jugador_1": {
        "pase": 0.45,
        "vision": 0.35,
        "precision": 0.20
      },
      "jugador_2": {
        "anticipacion": 0.40,
        "reaccion": 0.25,
        "marca": 0.35
      }
    },

    "remate": {
      "jugador_1": {
        "precision": 0.30,
        "definicion": 0.45,
        "control": 0.25
      },
      "jugador_2": {
        "reaccion": 0.40,
        "marca": 0.20,
        "anticipacion": 0.40
      }
    }
  }

  def __init__(
    self,
    jugador_1,
    jugador_2,
    tipo
  ):
    self.jugador_1 = jugador_1
    self.jugador_2 = jugador_2
    self.tipo = tipo

    self.fuerza_1 = 0
    self.fuerza_2 = 0

    self.probabilidad_1 = 0
    self.probabilidad_2 = 0

    self.resultado_azar = None
    self.ganador = None

  def calcular_fuerza(
    self,
    jugador,
    atributos
  ):
    fuerza = 0

    for atributo, peso in atributos.items():
      valor = jugador.obtener_estadistica(
        atributo
      )

      fuerza += valor * peso

    return fuerza

  def calcular_probabilidades(self):
    if self.tipo not in self.TIPOS:
      return

    configuracion = self.TIPOS[self.tipo]

    self.fuerza_1 = self.calcular_fuerza(
      self.jugador_1,
      configuracion["jugador_1"]
    )

    self.fuerza_2 = self.calcular_fuerza(
      self.jugador_2,
      configuracion["jugador_2"]
    )

    total = (
      self.fuerza_1
      + self.fuerza_2
    )

    if total == 0:
      self.probabilidad_1 = 50
      self.probabilidad_2 = 50
      return

    self.probabilidad_1 = (
      self.fuerza_1 / total
    ) * 100

    self.probabilidad_2 = (
      self.fuerza_2 / total
    ) * 100

  def resolver(self):
    if self.tipo not in self.TIPOS:
      return None

    self.calcular_probabilidades()

    self.resultado_azar = random.uniform(
      0,
      100
    )

    if (
      self.resultado_azar
      < self.probabilidad_1
    ):
      self.ganador = self.jugador_1

    else:
      self.ganador = self.jugador_2

    return self.ganador

  def obtener_resultado(self):
    return {
      "jugador_1": self.jugador_1,
      "jugador_2": self.jugador_2,
      "tipo": self.tipo,
      "fuerza_1": self.fuerza_1,
      "fuerza_2": self.fuerza_2,
      "probabilidad_1": self.probabilidad_1,
      "probabilidad_2": self.probabilidad_2,
      "resultado_azar": self.resultado_azar,
      "ganador": self.ganador
    }


