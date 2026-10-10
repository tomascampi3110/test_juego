import random
from duelo import Duelo

class Partido:
  def __init__(
    self,
    local,
    visitante,
    estadio,
    tipo="liga",
    permite_prorroga=False
  ):
    self.local = local
    self.visitante = visitante
    self.estadio = estadio
    self.tipo = tipo
    self.permite_prorroga = permite_prorroga

    self.goles_local = []
    self.goles_visitante = []
    self.asistencias = []
    self.eventos = []
    self.amonestados = []
    self.lesiones = []
    self.duelos = []

    self.resultado = (0, 0)
    self.estado = "pendiente"
    self.minuto = 0
    self.ganador = None
    self.tiempo_extra = False
    self.actuaciones = {}
    self.participantes = set()
    self.jugador_controlado = None


  def registrar_participacion(self, jugador, evento, puntos=0):
    if jugador not in self.actuaciones:
      self.actuaciones[jugador] = {
        "puntos": 0.0,
        "goles": 0,
        "asistencias": 0,
        "amonestaciones": 0,
        "duelos_ganados": 0,
        "duelos_jugados": 0
      }

    self.participantes.add(jugador)
    self.actuaciones[jugador]["puntos"] += puntos
    if evento in self.actuaciones[jugador]:
      self.actuaciones[jugador][evento] += 1


  def calcular_nota_jugador(self, jugador):
    datos = self.actuaciones.get(jugador, {})
    nota = 6.0 + datos.get("puntos", 0)
    nota += datos.get("goles", 0) * 1.2
    nota += datos.get("asistencias", 0) * 0.7
    nota += datos.get("duelos_ganados", 0) * 0.08
    nota -= datos.get("amonestaciones", 0) * 0.45
    return round(max(1.0, min(10.0, nota)), 2)


  def iniciar(self):
    if self.estado != "pendiente":
      return

    self.estado = "en juego"
    self.minuto = 0


  def obtener_jugadores_disponibles(self, equipo):
    if not hasattr(equipo, "jugadores"):
      return []

    jugadores = []

    for jugador in equipo.jugadores:
      if jugador.esta_disponible():
        jugadores.append(jugador)

    return jugadores


  def elegir_jugador(self, equipo):
    jugadores = self.obtener_jugadores_disponibles(equipo)

    if not jugadores:
      return None

    return random.choice(jugadores)


  def elegir_oponente(self, equipo):
    if equipo == self.local:
      return self.elegir_jugador(self.visitante)

    return self.elegir_jugador(self.local)


  def obtener_jugadores_por_posicion(
    self,
    equipo,
    posiciones
  ):
    jugadores = self.obtener_jugadores_disponibles(equipo)

    resultado = []

    for jugador in jugadores:
      posicion = jugador.obtener_posicion_normalizada()

      if posicion in posiciones:
        resultado.append(jugador)

    return resultado


  def elegir_arquero(self, equipo):
    arqueros = self.obtener_jugadores_por_posicion(
      equipo,
      ["arquero"]
    )

    if not arqueros:
      return self.elegir_jugador(equipo)

    return random.choice(arqueros)


  def agregar_duelo(
    self,
    jugador_1,
    jugador_2,
    tipo
  ):
    duelo = Duelo(
      jugador_1,
      jugador_2,
      tipo
    )

    duelo.resolver()

    self.duelos.append(duelo)
    self.registrar_participacion(jugador_1, "duelos_jugados")
    self.registrar_participacion(jugador_2, "duelos_jugados")

    if duelo.ganador is not None:
      self.registrar_participacion(
        duelo.ganador,
        "duelos_ganados"
      )
      self.actuaciones[duelo.ganador]["duelos_ganados"] += 1

    return duelo


  def agregar_gol(
    self,
    jugador,
    equipo
  ):
    gol = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    if equipo == self.local:
      self.goles_local.append(gol)

    else:
      self.goles_visitante.append(gol)

    jugador.goles += 1
    self.registrar_participacion(jugador, "goles")
    self.actuaciones[jugador]["puntos"] += 0.2


  def agregar_asistencia(
    self,
    jugador,
    equipo
  ):
    asistencia = {
      "jugador": jugador,
      "equipo": equipo,
      "minuto": self.minuto
    }

    self.asistencias.append(asistencia)

    jugador.asistencias += 1
    self.registrar_participacion(jugador, "asistencias")


  def agregar_amonestacion(self, jugador):
    amonestacion = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    self.amonestados.append(amonestacion)

    jugador.amonestado += 1
    self.registrar_participacion(jugador, "amonestaciones")


  def agregar_lesion(self, jugador):
    lesion = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    self.lesiones.append(lesion)

    jugador.lesion = True
    jugador.semanas_lesion = random.randint(1, 4)
    self.registrar_participacion(jugador, "puntos", -0.1)


  def generar_jugada_aerea(self):
    atacantes_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    atacantes_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not atacantes_local or not atacantes_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(atacantes_local)
      jugador_2 = random.choice(
        atacantes_visitante
      )
      equipo_1 = self.local
      equipo_2 = self.visitante

    else:
      jugador_1 = random.choice(atacantes_visitante)
      jugador_2 = random.choice(
        atacantes_local
      )
      equipo_1 = self.visitante
      equipo_2 = self.local

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "aereo"
    )

    if duelo.ganador == jugador_1:
      self.generar_remate(
        jugador_1,
        equipo_1
      )


  def generar_jugada_uno_contra_uno(self):
    jugadores_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    jugadores_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not jugadores_local or not jugadores_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(jugadores_local)
      jugador_2 = random.choice(
        jugadores_visitante
      )
      equipo = self.local

    else:
      jugador_1 = random.choice(jugadores_visitante)
      jugador_2 = random.choice(
        jugadores_local
      )
      equipo = self.visitante

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "uno_contra_uno"
    )

    if duelo.ganador == jugador_1:
      self.generar_remate(
        jugador_1,
        equipo
      )


  def generar_pelota_dividida(self):
    jugadores_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    jugadores_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not jugadores_local or not jugadores_visitante:
      return

    jugador_1 = random.choice(jugadores_local)
    jugador_2 = random.choice(
      jugadores_visitante
    )

    self.agregar_duelo(
      jugador_1,
      jugador_2,
      "pelota_dividida"
    )


  def generar_pase(self):
    mediocampistas_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["mediocampista", "delantero", "defensor"]
      )
    )

    mediocampistas_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["mediocampista", "delantero", "defensor"]
      )
    )

    if not mediocampistas_local or not mediocampistas_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(
        mediocampistas_local
      )
      jugador_2 = random.choice(
        mediocampistas_visitante
      )
      equipo = self.local

    else:
      jugador_1 = random.choice(
        mediocampistas_visitante
      )
      jugador_2 = random.choice(
        mediocampistas_local
      )
      equipo = self.visitante

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "pase"
    )

    if duelo.ganador == jugador_1:
      self.intentar_asistencia(
        jugador_1,
        equipo
      )


  def generar_remate(
    self,
    jugador,
    equipo
  ):
    arquero = self.elegir_arquero(
      self.visitante
      if equipo == self.local
      else self.local
    )

    if arquero is None:
      return

    duelo = self.agregar_duelo(
      jugador,
      arquero,
      "remate"
    )

    if duelo.ganador == jugador:
      self.agregar_gol(
        jugador,
        equipo
      )

      self.intentar_asistencia(
        jugador,
        equipo
      )


  def intentar_asistencia(
    self,
    jugador,
    equipo
  ):
    compañeros = (
      self.obtener_jugadores_disponibles(
        equipo
      )
    )

    compañeros = [
      compañero
      for compañero in compañeros
      if compañero != jugador
    ]

    if not compañeros:
      return

    if random.random() < 0.7:
      asistente = random.choice(
        compañeros
      )

      self.agregar_asistencia(
        asistente,
        equipo
      )


  def generar_amarilla(self):
    equipo = random.choice([
      self.local,
      self.visitante
    ])

    jugador = self.elegir_jugador(equipo)

    if jugador is None:
      return

    self.agregar_amonestacion(jugador)


  def generar_lesion(self):
    equipo = random.choice([
      self.local,
      self.visitante
    ])

    jugador = self.elegir_jugador(equipo)

    if jugador is None:
      return

    reduccion = 0
    for objeto in getattr(jugador, "equipamiento", {}).values():
      if getattr(objeto, "activo", False):
        reduccion += objeto.obtener_reduccion_lesion()

    probabilidad = max(0.02, 0.25 * (1 - min(0.90, reduccion)))
    if random.random() < probabilidad:
      self.agregar_lesion(jugador)


  def generar_evento(self):
    numero = random.random()

    if numero < 0.025:
      self.generar_jugada_aerea()

    elif numero < 0.070:
      self.generar_jugada_uno_contra_uno()

    elif numero < 0.090:
      self.generar_pelota_dividida()

    elif numero < 0.110:
      self.generar_pase()

    elif numero < 0.120:
      self.generar_amarilla()

    elif numero < 0.125:
      self.generar_lesion()


  def avanzar_minuto(self):
    if self.estado != "en juego":
      return

    self.minuto += 1

    self.generar_evento()


  def calcular_resultado(self):
    self.resultado = (
      len(self.goles_local),
      len(self.goles_visitante)
    )


  def determinar_ganador(self):
    if self.resultado[0] > self.resultado[1]:
      self.ganador = self.local

    elif self.resultado[1] > self.resultado[0]:
      self.ganador = self.visitante

    else:
      self.ganador = None


  def resolver_empate(self):
    if self.resultado[0] != self.resultado[1]:
      self.determinar_ganador()
      return

    jugador_local = self.elegir_jugador(
      self.local
    )

    jugador_visitante = self.elegir_jugador(
      self.visitante
    )

    if (
      jugador_local is None
      or jugador_visitante is None
    ):
      self.ganador = random.choice([
        self.local,
        self.visitante
      ])
      return

    duelo = self.agregar_duelo(
      jugador_local,
      jugador_visitante,
      "pelota_dividida"
    )

    if duelo.ganador == jugador_local:
      self.ganador = self.local

    else:
      self.ganador = self.visitante

    self.eventos.append({
      "tipo": "desempate",
      "jugador": duelo.ganador,
      "equipo": self.ganador,
      "minuto": self.minuto
    })


  def iniciar_prorroga(self):
    if not self.permite_prorroga:
      return

    if self.resultado[0] != self.resultado[1]:
      return

    self.tiempo_extra = True
    self.minuto = 90

    self.eventos.append({
      "tipo": "inicio_prorroga",
      "minuto": 90
    })


  def simular(self):
    if self.estado != "pendiente":
      return

    self.iniciar()

    while self.minuto < 90:
      self.avanzar_minuto()

    self.calcular_resultado()

    if (
      self.resultado[0] == self.resultado[1]
      and self.permite_prorroga
    ):
      self.iniciar_prorroga()

      while self.minuto < 120:
        self.avanzar_minuto()

      self.calcular_resultado()

      if self.resultado[0] == self.resultado[1]:
        self.resolver_empate()

    self.finalizar()


  def sumar_puntos(self):
    if self.tipo != "liga":
      return

    if self.resultado[0] > self.resultado[1]:
      self.local.pts += 3
      self.local.g += 1
      self.visitante.p += 1

    elif self.resultado[1] > self.resultado[0]:
      self.visitante.pts += 3
      self.visitante.g += 1
      self.local.p += 1

    else:
      self.local.pts += 1
      self.visitante.pts += 1
      self.local.e += 1
      self.visitante.e += 1


  def actualizar_estadisticas_equipos(self):
    if self.tipo != "liga":
      return

    self.local.pj += 1
    self.visitante.pj += 1

    self.local.gf += len(
      self.goles_local
    )

    self.local.gc += len(
      self.goles_visitante
    )

    self.visitante.gf += len(
      self.goles_visitante
    )

    self.visitante.gc += len(
      self.goles_local
    )


  def finalizar(self):
    if self.estado != "en juego":
      return

    if (
      self.jugador_controlado is not None
      and self.jugador_controlado in self.local.jugadores + self.visitante.jugadores
      and self.jugador_controlado.esta_disponible()
    ):
      self.registrar_participacion(
        self.jugador_controlado,
        "puntos"
      )

    self.calcular_resultado()

    if self.ganador is None:
      self.determinar_ganador()

    self.estado = "terminado"

    for jugador in list(self.participantes):
      datos = self.actuaciones.get(jugador, {})
      nota = self.calcular_nota_jugador(jugador)
      jugador.registrar_actuacion(nota, datos)

      from logros import SistemaLogros
      SistemaLogros().actualizar(
        jugador,
        {
          "nota": nota,
          "goles": datos.get("goles", 0)
        }
      )

      for objeto in list(getattr(jugador, "equipamiento", {}).values()):
        if getattr(objeto, "activo", False):
          objeto.desgastar()
        if not getattr(objeto, "activo", False):
          jugador.equipamiento.pop(objeto.espacio, None)

    self.sumar_puntos()
    self.actualizar_estadisticas_equipos()


