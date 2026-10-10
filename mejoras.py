class MejoraCarrera:
  CATALOGO = {
    "inversiones_plus": {
      "nombre": "Asesor financiero",
      "descripcion": "Aumenta los ingresos semanales de todas tus inversiones.",
      "precio": 25000,
      "bonificador": "inversiones",
      "incremento": 0.05,
      "max_nivel": 10
    },
    "sponsors_plus": {
      "nombre": "Agente de imagen",
      "descripcion": "Aumenta los pagos semanales y bonos de tus patrocinadores.",
      "precio": 35000,
      "bonificador": "sponsors",
      "incremento": 0.05,
      "max_nivel": 10
    },
    "espacio_sponsor": {
      "nombre": "Equipo de representación ampliado",
      "descripcion": "Desbloquea un espacio adicional para contratar un sponsor.",
      "precio": 125000,
      "bonificador": None,
      "incremento": 0,
      "max_nivel": 1
    },
    "experiencia_plus": {
      "nombre": "Plan de formación personal",
      "descripcion": "Aumenta los puntos de mejora obtenidos mediante logros.",
      "precio": 30000,
      "bonificador": "experiencia",
      "incremento": 0.05,
      "max_nivel": 10
    }
  }

  @classmethod
  def nivel(cls, jugador, identificador):
    if identificador == "espacio_sponsor":
      return 1 if identificador in jugador.mejoras_carrera else 0
    return jugador.niveles_mejoras.get(identificador, 0)

  @classmethod
  def costo_siguiente_nivel(cls, jugador, identificador):
    mejora = cls.CATALOGO[identificador]
    nivel = cls.nivel(jugador, identificador)
    return mejora["precio"] * (nivel + 1)

  @classmethod
  def comprar(cls, jugador, identificador):
    if identificador not in cls.CATALOGO:
      return False

    mejora = cls.CATALOGO[identificador]
    nivel = cls.nivel(jugador, identificador)
    if nivel >= mejora["max_nivel"]:
      return False

    precio = cls.costo_siguiente_nivel(jugador, identificador)
    if jugador.dinero < precio:
      return False

    jugador.dinero -= precio
    nuevo_nivel = nivel + 1

    if identificador == "espacio_sponsor":
      jugador.mejoras_carrera.add(identificador)
      jugador.espacios_sponsor += 1
    else:
      jugador.niveles_mejoras[identificador] = nuevo_nivel
      clave = mejora["bonificador"]
      jugador.bonificadores[clave] += mejora["incremento"]

    return True
