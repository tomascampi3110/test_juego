from equipamiento import Equipamiento


class TiendaEquipamiento:
  CATALOGO = [
    {
      "id": "botines_precision",
      "nombre": "Botines de precisión",
      "espacio": "botines",
      "precio": 45000,
      "atributos": {"precision": 3, "control": 1},
      "durabilidad": 50
    },
    {
      "id": "botines_velocidad",
      "nombre": "Botines ligeros",
      "espacio": "botines",
      "precio": 50000,
      "atributos": {"velocidad": 3, "regate": 1},
      "durabilidad": 50
    },
    {
      "id": "canilleras_reforzadas",
      "nombre": "Canilleras reforzadas",
      "espacio": "canilleras",
      "precio": 30000,
      "atributos": {"equilibrio": 1},
      "durabilidad": 50,
      "reduccion_lesion": 0.20
    },
    {
      "id": "canilleras_pro",
      "nombre": "Canilleras profesionales",
      "espacio": "canilleras",
      "precio": 65000,
      "atributos": {"equilibrio": 2},
      "durabilidad": 50,
      "reduccion_lesion": 0.35
    }
  ]

  @classmethod
  def listar(cls):
    return [dict(item) for item in cls.CATALOGO]

  @classmethod
  def comprar_y_equipar(cls, jugador, identificador, precio_final=None):
    item = next(
      (item for item in cls.CATALOGO if item["id"] == identificador),
      None
    )
    if item is None:
      return {"ok": False, "mensaje": "Ese artículo no existe."}

    precio = item["precio"] if precio_final is None else max(0, int(precio_final))
    if jugador.dinero < precio:
      return {"ok": False, "mensaje": "No tenés dinero suficiente."}

    nuevo = Equipamiento(
      item["nombre"],
      item["espacio"],
      precio,
      item["atributos"],
      item["durabilidad"],
      item.get("reduccion_lesion", 0)
    )

    jugador.dinero -= precio
    anterior = jugador.equipamiento.get(nuevo.espacio)
    jugador.equipamiento[nuevo.espacio] = nuevo

    return {
      "ok": True,
      "mensaje": f"Equipaste {nuevo.nombre}.",
      "objeto": nuevo,
      "objeto_anterior": anterior
    }


class BolsaEquipamiento:
  def __init__(self):
    self.ofertas = []
    self.ultima_actualizacion = 0

  def actualizar(self, semana, cantidad=3):
    import random

    if semana == self.ultima_actualizacion:
      return self.ofertas

    catalogo = TiendaEquipamiento.CATALOGO.copy()
    random.shuffle(catalogo)
    self.ofertas = []

    for item in catalogo[:cantidad]:
      descuento = random.choice([0, 5, 10, 15])
      oferta = dict(item)
      oferta["precio_original"] = item["precio"]
      oferta["descuento"] = descuento
      oferta["precio"] = round(item["precio"] * (1 - descuento / 100))
      oferta["stock"] = 1
      oferta["semana"] = semana
      self.ofertas.append(oferta)

    self.ultima_actualizacion = semana
    return self.ofertas

  def comprar(self, jugador, indice):
    if not 0 <= indice < len(self.ofertas):
      return {"ok": False, "mensaje": "La oferta no existe."}

    oferta = self.ofertas[indice]
    if oferta["stock"] <= 0:
      return {"ok": False, "mensaje": "La oferta ya se agotó."}

    resultado = TiendaEquipamiento.comprar_y_equipar(
      jugador,
      oferta["id"],
      precio_final=oferta["precio"]
    )
    if resultado["ok"]:
      oferta["stock"] -= 1
      resultado["mensaje"] = f"Compraste {oferta['nombre']} con {oferta['descuento']}% de descuento."

    return resultado
