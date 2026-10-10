class Objeto:
  TIPOS = {
    "coleccionable": {
      "valor_base": 100
    },
    "vehiculo": {
      "valor_base": 1000
    },
    "lujo": {
      "valor_base": 500
    },
    "especial": {
      "valor_base": 250
    }
  }

  def __init__(
    self,
    nombre,
    tipo,
    valor
  ):
    if tipo not in self.TIPOS:
      tipo = "especial"

    self.nombre = nombre
    self.tipo = tipo
    self.valor = valor

    self.vendido = False

  def vender(
    self,
    jugador
  ):
    if self.vendido:
      return 0

    if self not in jugador.inventario:
      return 0

    jugador.dinero += self.valor
    jugador.inventario.remove(self)

    if self.tipo == "lujo":
      if self in jugador.lujo:
        jugador.lujo.remove(self)
      jugador.nivel_lujo = max(0, jugador.nivel_lujo - 1)

    self.vendido = True
    return self.valor

  def __str__(
    self
  ):
    return (
      f"Objeto: {self.nombre}\n"
      f"Tipo: {self.tipo}\n"
      f"Valor: ${self.valor}"
    )

