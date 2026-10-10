from partido import Partido

class Competicion:
  def __init__(self, nombre, equipos):
    self.nombre = nombre
    self.equipos = equipos
    self.partidos = []
    self.estado = "pendiente"
    self.calendario = {}

  def iniciar(self):
    if self.estado == "pendiente":
      self.estado = "en juego"

  def finalizar(self):
    if self.estado == "en juego":
      self.estado = "terminada"

  def agregar_equipo(self, equipo):
    if equipo not in self.equipos:
      self.equipos.append(equipo)

  def eliminar_equipo(self, equipo):
    if equipo in self.equipos:
      self.equipos.remove(equipo)

  def agregar_partido(self, partido):
    if partido not in self.partidos:
      self.partidos.append(partido)

  def buscar_equipo(self, nombre, indice=0):
    if indice == len(self.equipos):
      return None

    if self.equipos[indice].nombre == nombre:
      return self.equipos[indice]

    return self.buscar_equipo(
      nombre,
      indice + 1
    )

  def cantidad_equipos(self):
    return len(self.equipos)

  def asignar_partido_semana(
    self,
    partido,
    semana,
    dia
  ):
    if semana not in self.calendario:
      self.calendario[semana] = {}

    if dia not in self.calendario[semana]:
      self.calendario[semana][dia] = []

    self.calendario[semana][dia].append(
      partido
    )

  def obtener_partidos_semana(self, semana):
    partidos = []

    if semana not in self.calendario:
      return partidos

    for dia in self.calendario[semana]:
      partidos.extend(
        self.calendario[semana][dia]
      )

    return partidos


class Liga(Competicion):
  def __init__(
    self,
    nombre,
    equipos,
    division
  ):
    super().__init__(
      nombre,
      equipos
    )

    self.division = division
    self.jornadas = []
    self.campeon = None
    self.descendidos = []
    self.promovidos = []

  def tabla(self):
    return sorted(
      self.equipos,
      key=lambda equipo: (
        equipo.pts,
        equipo.gf - equipo.gc,
        equipo.gf
      ),
      reverse=True
    )

  def obtener_campeon(self):
    tabla = self.tabla()

    if not tabla:
      return None

    return tabla[0]

  def obtener_descendidos(self, cantidad=2):
    tabla = self.tabla()

    return tabla[-cantidad:]

  def obtener_promovidos(self, cantidad=2):
    tabla = self.tabla()

    return tabla[:cantidad]

  def cerrar_temporada(self):
    if self.estado != "en juego":
      return

    self.campeon = self.obtener_campeon()
    self.descendidos = (
      self.obtener_descendidos()
    )
    self.promovidos = (
      self.obtener_promovidos()
    )

    self.finalizar()

  def generar_jornadas(self):
    self.jornadas = []
    self.partidos = []
    self.calendario = {}

    equipos = self.equipos.copy()

    if len(equipos) < 2:
      return

    if len(equipos) % 2 != 0:
      equipos.append(None)

    cantidad = len(equipos)

    for _ in range(cantidad - 1):
      jornada = []

      for i in range(cantidad // 2):
        local = equipos[i]
        visitante = equipos[-(i + 1)]

        if (
          local is not None
          and visitante is not None
        ):
          partido = Partido(
            local,
            visitante,
            local.estadio,
            "liga",
            False
          )

          jornada.append(partido)
          self.partidos.append(partido)

      self.jornadas.append(jornada)

      equipos = (
        [equipos[0]]
        + [equipos[-1]]
        + equipos[1:-1]
      )

    ida = self.jornadas.copy()

    for jornada in ida:
      vuelta = []

      for partido in jornada:
        nuevo = Partido(
          partido.visitante,
          partido.local,
          partido.visitante.estadio,
          "liga",
          False
        )

        vuelta.append(nuevo)
        self.partidos.append(nuevo)

      self.jornadas.append(vuelta)

  def obtener_partidos_semana(self, semana):
    if semana < 1:
      return []

    if semana > len(self.jornadas):
      return []

    return self.jornadas[semana - 1]


class Grupo:
  def __init__(
    self,
    nombre,
    participantes
  ):
    self.nombre = nombre
    self.participantes = participantes
    self.partidos = []
    self.tabla = {}

    self.reiniciar_tabla()

  def reiniciar_tabla(self):
    self.tabla = {}

    for participante in self.participantes:
      self.tabla[participante] = {
        "pts": 0,
        "pj": 0,
        "g": 0,
        "e": 0,
        "p": 0,
        "gf": 0,
        "gc": 0
      }

  def generar_partidos(self):
    self.partidos = []

    for i in range(
      len(self.participantes)
    ):
      for j in range(
        i + 1,
        len(self.participantes)
      ):
        local = self.participantes[i]
        visitante = self.participantes[j]

        partido = Partido(
          local,
          visitante,
          getattr(
            local,
            "estadio",
            None
          ),
          "grupo",
          False
        )

        self.partidos.append(partido)

        partido = Partido(
          visitante,
          local,
          getattr(
            visitante,
            "estadio",
            None
          ),
          "grupo",
          False
        )

        self.partidos.append(partido)

  def actualizar_tabla(self):
    self.reiniciar_tabla()

    for partido in self.partidos:
      if partido.estado != "terminado":
        continue

      local = partido.local
      visitante = partido.visitante

      goles_local = len(
        partido.goles_local
      )

      goles_visitante = len(
        partido.goles_visitante
      )

      self.tabla[local]["pj"] += 1
      self.tabla[visitante]["pj"] += 1

      self.tabla[local]["gf"] += (
        goles_local
      )

      self.tabla[local]["gc"] += (
        goles_visitante
      )

      self.tabla[visitante]["gf"] += (
        goles_visitante
      )

      self.tabla[visitante]["gc"] += (
        goles_local
      )

      if goles_local > goles_visitante:
        self.tabla[local]["pts"] += 3
        self.tabla[local]["g"] += 1
        self.tabla[visitante]["p"] += 1

      elif goles_visitante > goles_local:
        self.tabla[visitante]["pts"] += 3
        self.tabla[visitante]["g"] += 1
        self.tabla[local]["p"] += 1

      else:
        self.tabla[local]["pts"] += 1
        self.tabla[visitante]["pts"] += 1
        self.tabla[local]["e"] += 1
        self.tabla[visitante]["e"] += 1

  def obtener_tabla(self):
    self.actualizar_tabla()

    return sorted(
      self.participantes,
      key=lambda equipo: (
        self.tabla[equipo]["pts"],
        self.tabla[equipo]["gf"]
        - self.tabla[equipo]["gc"],
        self.tabla[equipo]["gf"]
      ),
      reverse=True
    )

  def obtener_clasificados(self, cantidad):
    tabla = self.obtener_tabla()

    return tabla[:cantidad]

  def todos_los_partidos_terminados(self):
    for partido in self.partidos:
      if partido.estado != "terminado":
        return False

    return True


class Seleccion:
  def __init__(
    self,
    nombre,
    jugadores=None
  ):
    self.nombre = nombre
    self.estadio = None

    if jugadores is None:
      self.jugadores = []
    else:
      self.jugadores = jugadores

    self.alineacion = []

  def agregar_jugador(self, jugador):
    if jugador not in self.jugadores:
      self.jugadores.append(jugador)
      jugador.habilitado = True

  def eliminar_jugador(self, jugador):
    if jugador in self.jugadores:
      self.jugadores.remove(jugador)

  def obtener_jugadores_disponibles(self):
    disponibles = []

    for jugador in self.jugadores:
      if jugador.esta_disponible():
        disponibles.append(jugador)

    return disponibles


class CopaNacional(Competicion):
  def __init__(
    self,
    nombre,
    equipos
  ):
    super().__init__(
      nombre,
      equipos
    )

    self.divisiones = []
    self.rondas = []
    self.equipos_esperando = []
    self.ronda_actual = 0
    self.campeon = None

  def sortear_equipos(self, equipos):
    equipos = equipos.copy()

    random.shuffle(equipos)

    return equipos

  def generar_copa(self, divisiones):
    self.divisiones = divisiones
    self.rondas = []
    self.partidos = []
    self.equipos_esperando = []
    self.ronda_actual = 0
    self.campeon = None

    if not divisiones:
      return

    self.equipos_esperando = (
      self.sortear_equipos(
        divisiones[0]
      )
    )

    self.generar_ronda_actual()

  def generar_ronda_actual(self):
    equipos = self.equipos_esperando

    if (
      len(equipos) == 1
      and self.ronda_actual + 1
      < len(self.divisiones)
    ):
      self.equipos_esperando = (
        self.divisiones[
          self.ronda_actual + 1
        ]
        + equipos
      )

      self.ronda_actual += 1

      self.generar_ronda_actual()

      return

    equipos = self.sortear_equipos(
      equipos
    )

    partidos = []
    quedan = []

    limite = len(equipos) - (
      len(equipos) % 2
    )

    for i in range(
      0,
      limite,
      2
    ):
      local = equipos[i]
      visitante = equipos[i + 1]

      partido = Partido(
        local,
        visitante,
        local.estadio,
        "copa",
        True
      )

      partidos.append(partido)
      self.partidos.append(partido)

    if len(equipos) % 2 != 0:
      quedan.append(
        equipos[-1]
      )

    self.rondas.append(partidos)
    self.equipos_esperando = quedan

  def ronda_terminada(self):
    if not self.rondas:
      return False

    ronda = self.rondas[-1]

    for partido in ronda:
      if partido.estado != "terminado":
        return False

    return True

  def avanzar_ronda(self):
    if not self.ronda_terminada():
      return

    ronda = self.rondas[-1]

    clasificados = []

    for partido in ronda:
      if partido.ganador is not None:
        clasificados.append(
          partido.ganador
        )

    clasificados.extend(
      self.equipos_esperando
    )

    siguiente_division = (
      self.ronda_actual + 1
    )

    if siguiente_division < len(
      self.divisiones
    ):
      clasificados.extend(
        self.divisiones[
          siguiente_division
        ]
      )

      self.ronda_actual = (
        siguiente_division
      )

    if len(clasificados) == 1:
      self.campeon = clasificados[0]
      self.estado = "terminada"
      return

    self.equipos_esperando = (
      self.sortear_equipos(
        clasificados
      )
    )

    self.generar_ronda_actual()


class CopaClubes(Competicion):
  def __init__(
    self,
    nombre,
    equipos,
    cantidad_grupos=8
  ):
    super().__init__(
      nombre,
      equipos
    )

    self.cantidad_grupos = (
      cantidad_grupos
    )

    self.equipos_preliminar = []
    self.equipos_directos_grupos = []

    self.rondas_preliminares = []
    self.grupos = []
    self.rondas = []

    self.ronda_actual = 0
    self.fase = "pendiente"
    self.campeon = None

  def sortear_equipos(self, equipos):
    equipos = equipos.copy()

    random.shuffle(equipos)

    return equipos

  def generar_copa(
    self,
    equipos_preliminar=None,
    equipos_directos_grupos=None
  ):
    self.partidos = []
    self.rondas_preliminares = []
    self.grupos = []
    self.rondas = []
    self.ronda_actual = 0
    self.campeon = None

    if (
      equipos_preliminar is None
      and equipos_directos_grupos is None
    ):
      equipos = self.equipos.copy()

      if len(equipos) <= 32:
        self.equipos_preliminar = []
        self.equipos_directos_grupos = (
          equipos
        )

      else:
        cantidad_preliminar = (
          2 * (len(equipos) - 32)
        )

        if cantidad_preliminar > len(
          equipos
        ):
          raise ValueError(
            "Hay demasiados equipos "
            "para esta estructura."
          )

        equipos = self.sortear_equipos(
          equipos
        )

        self.equipos_preliminar = (
          equipos[:cantidad_preliminar]
        )

        self.equipos_directos_grupos = (
          equipos[cantidad_preliminar:]
        )

    else:
      self.equipos_preliminar = (
        equipos_preliminar or []
      )

      self.equipos_directos_grupos = (
        equipos_directos_grupos or []
      )

    if self.equipos_preliminar:
      equipos = self.sortear_equipos(
        self.equipos_preliminar
      )

      partidos = []

      limite = len(equipos) - (
        len(equipos) % 2
      )

      for i in range(
        0,
        limite,
        2
      ):
        partido = Partido(
          equipos[i],
          equipos[i + 1],
          equipos[i].estadio,
          "preliminar",
          True
        )

        partidos.append(partido)
        self.partidos.append(partido)

      self.rondas_preliminares.append(
        partidos
      )

      self.fase = "preliminar"

    else:
      self.crear_grupos(
        self.equipos_directos_grupos
      )

      self.fase = "grupos"

  def crear_grupos(self, equipos):
    if (
      len(equipos)
      % self.cantidad_grupos != 0
    ):
      raise ValueError(
        "La cantidad de equipos debe "
        "ser divisible por la cantidad "
        "de grupos."
      )

    cantidad_por_grupo = (
      len(equipos)
      // self.cantidad_grupos
    )

    if cantidad_por_grupo < 2:
      raise ValueError(
        "Cada grupo debe tener al "
        "menos 2 equipos."
      )

    equipos = self.sortear_equipos(
      equipos
    )

    self.grupos = []

    for i in range(
      self.cantidad_grupos
    ):
      inicio = (
        i * cantidad_por_grupo
      )

      fin = (
        inicio
        + cantidad_por_grupo
      )

      participantes = equipos[
        inicio:fin
      ]

      grupo = Grupo(
        f"Grupo {i + 1}",
        participantes
      )

      grupo.generar_partidos()

      self.grupos.append(grupo)

      for partido in grupo.partidos:
        self.partidos.append(
          partido
        )

  def grupos_terminados(self):
    if not self.grupos:
      return False

    for grupo in self.grupos:
      if not grupo.todos_los_partidos_terminados():
        return False

    return True

  def obtener_clasificados_grupos(self):
    clasificados = []

    for grupo in self.grupos:
      clasificados.extend(
        grupo.obtener_clasificados(2)
      )

    return clasificados

  def generar_ronda_eliminacion(
    self,
    equipos
  ):
    equipos = self.sortear_equipos(
      equipos
    )

    ronda = []

    limite = len(equipos) - (
      len(equipos) % 2
    )

    for i in range(
      0,
      limite,
      2
    ):
      partido = Partido(
        equipos[i],
        equipos[i + 1],
        equipos[i].estadio,
        "copa_clubes",
        True
      )

      ronda.append(partido)
      self.partidos.append(partido)

    self.rondas.append(ronda)

  def avanzar_fase(self):
    if self.fase == "preliminar":
      ronda = (
        self.rondas_preliminares[0]
      )

      for partido in ronda:
        if partido.estado != "terminado":
          return

      clasificados = []

      for partido in ronda:
        if partido.ganador is not None:
          clasificados.append(
            partido.ganador
          )

      equipos = (
        self.equipos_directos_grupos
        + clasificados
      )

      self.crear_grupos(equipos)
      self.fase = "grupos"

      return

    if self.fase == "grupos":
      if not self.grupos_terminados():
        return

      clasificados = (
        self.obtener_clasificados_grupos()
      )

      self.rondas = []
      self.ronda_actual = 0

      self.generar_ronda_eliminacion(
        clasificados
      )

      self.fase = "eliminacion"

      return

    if self.fase == "eliminacion":
      if not self.rondas:
        return

      ronda = self.rondas[
        self.ronda_actual
      ]

      for partido in ronda:
        if partido.estado != "terminado":
          return

      clasificados = []

      for partido in ronda:
        if partido.ganador is not None:
          clasificados.append(
            partido.ganador
          )

      if len(clasificados) == 1:
        self.campeon = clasificados[0]
        self.fase = "terminada"
        self.estado = "terminada"

        return

      self.ronda_actual += 1

      self.generar_ronda_eliminacion(
        clasificados
      )


class Internacional(Competicion):
  def __init__(
    self,
    nombre,
    selecciones,
    cantidad_grupos=8
  ):
    super().__init__(
      nombre,
      selecciones
    )

    self.cantidad_grupos = (
      cantidad_grupos
    )

    self.grupos = []
    self.rondas = []

    self.ronda_actual = 0
    self.fase = "pendiente"
    self.campeon = None

  def sortear_selecciones(
    self,
    selecciones
  ):
    selecciones = selecciones.copy()

    random.shuffle(selecciones)

    return selecciones

  def generar_competencia(self):
    self.partidos = []
    self.grupos = []
    self.rondas = []

    self.ronda_actual = 0
    self.campeon = None

    if (
      len(self.equipos)
      % self.cantidad_grupos != 0
    ):
      raise ValueError(
        "La cantidad de selecciones "
        "debe ser divisible por la "
        "cantidad de grupos."
      )

    cantidad_por_grupo = (
      len(self.equipos)
      // self.cantidad_grupos
    )

    if cantidad_por_grupo < 2:
      raise ValueError(
        "Cada grupo debe tener al "
        "menos 2 selecciones."
      )

    selecciones = (
      self.sortear_selecciones(
        self.equipos
      )
    )

    for i in range(
      self.cantidad_grupos
    ):
      inicio = (
        i * cantidad_por_grupo
      )

      fin = (
        inicio
        + cantidad_por_grupo
      )

      participantes = selecciones[
        inicio:fin
      ]

      grupo = Grupo(
        f"Grupo {i + 1}",
        participantes
      )

      grupo.generar_partidos()

      self.grupos.append(grupo)

      for partido in grupo.partidos:
        self.partidos.append(
          partido
        )

    self.fase = "grupos"

  def grupos_terminados(self):
    if not self.grupos:
      return False

    for grupo in self.grupos:
      if not grupo.todos_los_partidos_terminados():
        return False

    return True

  def obtener_clasificados_grupos(self):
    clasificados = []

    for grupo in self.grupos:
      clasificados.extend(
        grupo.obtener_clasificados(2)
      )

    return clasificados

  def generar_ronda_eliminacion(
    self,
    selecciones
  ):
    selecciones = (
      self.sortear_selecciones(
        selecciones
      )
    )

    ronda = []

    limite = len(selecciones) - (
      len(selecciones) % 2
    )

    for i in range(
      0,
      limite,
      2
    ):
      partido = Partido(
        selecciones[i],
        selecciones[i + 1],
        None,
        "internacional",
        True
      )

      ronda.append(partido)
      self.partidos.append(partido)

    self.rondas.append(ronda)

  def avanzar_fase(self):
    if self.fase == "grupos":
      if not self.grupos_terminados():
        return

      clasificados = (
        self.obtener_clasificados_grupos()
      )

      self.rondas = []
      self.ronda_actual = 0

      self.generar_ronda_eliminacion(
        clasificados
      )

      self.fase = "eliminacion"

      return

    if self.fase == "eliminacion":
      ronda = self.rondas[
        self.ronda_actual
      ]

      for partido in ronda:
        if partido.estado != "terminado":
          return

      clasificados = []

      for partido in ronda:
        if partido.ganador is not None:
          clasificados.append(
            partido.ganador
          )

      if len(clasificados) == 1:
        self.campeon = clasificados[0]
        self.fase = "terminada"
        self.estado = "terminada"

        return

      self.ronda_actual += 1

      self.generar_ronda_eliminacion(
        clasificados
      )


