from mercado import MercadoPases
from competiciones import Liga, CopaNacional, CopaClubes, Internacional
from patrocinios import BolsaSponsors
from tienda import BolsaEquipamiento
from vida_social import SistemaVidaSocial
from logros import SistemaLogros

class Temporada:
  DIAS = [
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "viernes",
    "sabado",
    "domingo"
  ]

  def __init__(self, anio):
    self.anio = anio
    self.competiciones = []

    self.semana = 1
    self.dia = 1
    self.estado = "pendiente"

    self.calendario = {}
    self.duracion = 0

    self.partidos_programados = set()

    self.mercado_pases = MercadoPases()
    self.jugador_usuario = None
    self.ventanas_mercado_ejecutadas = set()

    self.bolsa_sponsors = BolsaSponsors()
    self.bolsa_equipamiento = BolsaEquipamiento()
    self.sistema_vida_social = SistemaVidaSocial()
    self.sistema_logros = SistemaLogros()
    self.eventos_sociales_pendientes = []

  def establecer_jugador_usuario(
    self,
    jugador
  ):
    self.jugador_usuario = jugador
    jugador.controlado = True

  def obtener_equipos(self):
    equipos = []
    vistos = set()

    for competicion in self.competiciones:
      for equipo in competicion.equipos:
        identificador = id(equipo)

        if identificador in vistos:
          continue

        vistos.add(identificador)
        equipos.append(equipo)

    return equipos

  def procesar_mercado_npc(self):
    if self.semana not in MercadoPases.VENTANAS_MERCADO:
      return []

    if self.semana in self.ventanas_mercado_ejecutadas:
      return []

    equipos = self.obtener_equipos()

    operaciones = self.mercado_pases.ejecutar_ventana_npc(
      equipos,
      self.jugador_usuario
    )

    if (
      self.jugador_usuario is not None
      and self.jugador_usuario.en_lista_transferibles
      and self.jugador_usuario.equipo is not None
    ):
      ofertas_usuario = self.mercado_pases.generar_ofertas_para_jugador(
        self.jugador_usuario,
        equipos
      )
      operaciones.extend(ofertas_usuario)

    self.ventanas_mercado_ejecutadas.add(
      self.semana
    )

    self.mercado_pases.historial_ventanas.append({
      "semana": self.semana,
      "operaciones": operaciones
    })

    self.mercado_pases.limpiar_ofertas_finalizadas()

    return operaciones

  def agregar_competicion(
    self,
    competicion
  ):
    if competicion not in self.competiciones:
      self.competiciones.append(
        competicion
      )

  def iniciar(self):
    if self.estado != "pendiente":
      return

    self.preparar_competiciones()
    self.programar_partidos_nuevos()

    self.estado = "en juego"

    for competicion in self.competiciones:
      competicion.iniciar()

  def preparar_competiciones(self):
    for competicion in self.competiciones:

      if isinstance(
        competicion,
        Liga
      ):
        competicion.generar_jornadas()

      elif isinstance(
        competicion,
        CopaNacional
      ):
        if (
          not competicion.rondas
          and competicion.divisiones
        ):
          competicion.generar_copa(
            competicion.divisiones
          )

      elif isinstance(
        competicion,
        CopaClubes
      ):
        if not competicion.partidos:
          competicion.generar_copa()

      elif isinstance(
        competicion,
        Internacional
      ):
        if not competicion.partidos:
          competicion.generar_competencia()

  def cantidad_partidos_equipo_semana(
    self,
    equipo,
    semana
  ):
    cantidad = 0

    for partido in (
      self.obtener_partidos_semana(
        semana
      )
    ):
      if (
        partido.local == equipo
        or partido.visitante == equipo
      ):
        cantidad += 1

    return cantidad

  def equipo_juega_dia(
    self,
    equipo,
    semana,
    dia
  ):
    partidos = (
      self.obtener_partidos_dia(
        semana,
        dia
      )
    )

    for partido in partidos:
      if (
        partido.local == equipo
        or partido.visitante == equipo
      ):
        return True

    return False

  def puede_asignar_partido(
    self,
    partido,
    semana,
    dia
  ):
    if self.equipo_juega_dia(
      partido.local,
      semana,
      dia
    ):
      return False

    if self.equipo_juega_dia(
      partido.visitante,
      semana,
      dia
    ):
      return False

    if (
      self.cantidad_partidos_equipo_semana(
        partido.local,
        semana
      ) >= 2
    ):
      return False

    if (
      self.cantidad_partidos_equipo_semana(
        partido.visitante,
        semana
      ) >= 2
    ):
      return False

    return True

  def asignar_partido(
    self,
    partido,
    semana,
    dia
  ):
    if not self.puede_asignar_partido(
      partido,
      semana,
      dia
    ):
      return False

    if semana not in self.calendario:
      self.calendario[semana] = {}

    if dia not in self.calendario[semana]:
      self.calendario[semana][dia] = []

    self.calendario[semana][dia].append(
      partido
    )

    self.partidos_programados.add(
      partido
    )

    return True

  def programar_partido(
    self,
    partido,
    semana_inicial=None
  ):
    if semana_inicial is None:
      semana_inicial = self.semana

    semana = semana_inicial

    while True:
      for dia in self.DIAS:
        if self.asignar_partido(
          partido,
          semana,
          dia
        ):
          return semana

      semana += 1

  def programar_partidos_nuevos(
    self,
    semana_inicial=None
  ):
    if semana_inicial is None:
      semana_inicial = self.semana

    for competicion in self.competiciones:
      if isinstance(competicion, Liga):
        for indice, jornada in enumerate(competicion.jornadas):
          semana = indice + 1

          for partido in jornada:
            if partido in self.partidos_programados:
              continue

            asignado = False
            for dia in self.DIAS:
              if self.equipo_juega_dia(
                partido.local,
                semana,
                dia
              ):
                continue

              if self.equipo_juega_dia(
                partido.visitante,
                semana,
                dia
              ):
                continue

              if self.asignar_partido(partido, semana, dia):
                asignado = True
                break

            if not asignado:
              self.programar_partido(partido, semana + 1)

        continue

      for partido in competicion.partidos:
        if partido in self.partidos_programados:
          continue

        self.programar_partido(
          partido,
          semana_inicial
        )

    if self.calendario:
      self.duracion = max(self.calendario.keys())

  def obtener_partidos_dia(
    self,
    semana,
    dia
  ):
    if semana not in self.calendario:
      return []

    return self.calendario[semana].get(
      dia,
      []
    )

  def obtener_partidos_semana(
    self,
    semana=None
  ):
    if semana is None:
      semana = self.semana

    partidos = []

    for dia in self.DIAS:
      partidos.extend(
        self.obtener_partidos_dia(
          semana,
          dia
        )
      )

    return partidos

  def obtener_jugadores(self):
    jugadores = []
    vistos = set()

    for competicion in self.competiciones:
      for equipo in competicion.equipos:
        for jugador in equipo.jugadores:
          identificador = id(jugador)

          if identificador in vistos:
            continue

          vistos.add(identificador)
          jugadores.append(jugador)

    return jugadores

  def procesar_economia_semana(self):
    jugadores = self.obtener_jugadores()

    for jugador in jugadores:
      if jugador.contrato is not None:
        jugador.contrato.avanzar_semana()

      for sponsor in list(jugador.sponsors.values()):
        sponsor.avanzar_semana(jugador)
        if not sponsor.activo:
          jugador.eliminar_sponsor(sponsor.nombre)

      for inversion in list(jugador.inversiones):
        inversion.generar_ingreso(jugador)

      jugador.procesar_semana()
      self.sistema_logros.actualizar(jugador)

    if self.jugador_usuario is not None:
      if self.semana % 4 == 1:
        self.bolsa_sponsors.actualizar(self.semana)
        self.bolsa_equipamiento.actualizar(self.semana)

      pendientes = [
        item for item in self.eventos_sociales_pendientes
        if not item["evento"].resuelto
      ]
      self.eventos_sociales_pendientes = pendientes

      # Solo se genera un evento si no quedó ninguno sin atender.
      # Así la bandeja social no acumula invitaciones de semanas anteriores.
      if not pendientes:
        evento = self.sistema_vida_social.procesar_semana(
          self.jugador_usuario,
          self.semana
        )

        if evento is not None:
          self.eventos_sociales_pendientes = [{
            "semana": self.semana,
            "evento": evento
          }]

  def simular_semana(self):
    if self.estado != "en juego":
      return

    self.procesar_mercado_npc()

    partidos = (
      self.obtener_partidos_semana()
    )

    for partido in partidos:
      if partido.estado == "pendiente":
        if (
          self.jugador_usuario is not None
          and self.jugador_usuario.equipo in [partido.local, partido.visitante]
        ):
          partido.jugador_controlado = self.jugador_usuario
        partido.simular()

    self.actualizar_competiciones()
    self.procesar_economia_semana()
    self.programar_partidos_nuevos(
      self.semana + 1
    )

  def actualizar_competiciones(self):
    for competicion in self.competiciones:

      if isinstance(
        competicion,
        Liga
      ):
        if (
          competicion.partidos
          and all(
            partido.estado == "terminado"
            for partido in competicion.partidos
          )
        ):
          if competicion.estado == "en juego":
            competicion.cerrar_temporada()
            campeon = competicion.campeon
            if campeon is not None:
              campeon.trofeos += 1
              for jugador in campeon.jugadores:
                jugador.titulos += 1
                self.sistema_logros.actualizar(jugador)

      elif isinstance(
        competicion,
        CopaNacional
      ):
        competicion.avanzar_ronda()

      elif isinstance(
        competicion,
        CopaClubes
      ):
        competicion.avanzar_fase()

      elif isinstance(
        competicion,
        Internacional
      ):
        competicion.avanzar_fase()

  def avanzar_semana(self):
    if self.estado != "en juego":
      return

    if self.semana < self.duracion:
      self.semana += 1
    else:
      self.finalizar()

  def simular(self):
    if self.estado == "pendiente":
      self.iniciar()

    while self.estado == "en juego":
      self.simular_semana()

      pendientes = (
        self.obtener_partidos_pendientes()
      )

      if not pendientes:
        self.finalizar()
        break

      self.avanzar_semana()

  def obtener_partidos_pendientes(self):
    pendientes = []

    for competicion in self.competiciones:
      for partido in competicion.partidos:
        if partido.estado != "terminado":
          pendientes.append(partido)

    return pendientes

  def finalizar(self):
    if self.estado == "en juego":
      self.estado = "terminada"


