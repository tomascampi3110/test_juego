OPCIONES_APARIENCIA = {
  "peinado": ["clasico", "corto", "rapado", "rulos", "largo", "trenzas"],
  "color_pelo": ["negro", "castanio", "rubio", "pelirrojo", "gris"],
  "ojos": ["marrones", "azules", "verdes", "grises"],
  "rostro": ["ovalado", "redondo", "cuadrado", "alargado"],
  "piel": ["clara", "media", "oscura"]
}


def personalizar_jugador(jugador, atributo, valor):
  if atributo not in OPCIONES_APARIENCIA:
    return False

  if valor not in OPCIONES_APARIENCIA[atributo]:
    return False

  return jugador.cambiar_apariencia(atributo, valor)


def agregar_tatuaje(jugador, tatuaje, precio):
  if not tatuaje or precio < 0:
    return False

  if jugador.dinero < precio:
    return False

  if tatuaje in jugador.apariencia["tatuajes"]:
    return False

  jugador.dinero -= precio
  jugador.cambiar_apariencia("tatuajes", tatuaje)
  jugador.nivel_lujo += 1
  return True
