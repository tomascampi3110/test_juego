import random
from contratos import Contrato

class OfertaTransferencia:
  def __init__(
    self,
    mercado,
    jugador,
    vendedor,
    comprador,
    monto,
    salario_semanal=0,
    duracion_semanas=52
  ):
    self.mercado = mercado
    self.jugador = jugador
    self.vendedor = vendedor
    self.comprador = comprador
    self.monto = monto
    self.salario_semanal = salario_semanal
    self.duracion_semanas = duracion_semanas
    self.estado = "pendiente"

  def aceptar(self):
    return self.mercado.aceptar_oferta(self)

  def rechazar(self):
    if self.estado != "pendiente":
      return False

    self.estado = "rechazada"
    return True

  def __str__(self):
    return (
      f"Jugador: {self.jugador.nombre}\n"
      f"Vendedor: {self.vendedor.nombre}\n"
      f"Comprador: {self.comprador.nombre}\n"
      f"Monto: ${self.monto}\n"
      f"Salario semanal: ${self.salario_semanal}\n"
      f"Duración: {self.duracion_semanas} semanas\n"
      f"Estado: {self.estado}"
    )


class MercadoPases:
  VENTANAS_MERCADO = (1, 20)

  NECESIDADES_POSICION = {
    "arquero": 2,
    "defensor": 5,
    "mediocampista": 5,
    "delantero": 3
  }

  def __init__(self):
    self.ofertas = []
    self.transferencias = []
    self.historial_ventanas = []

  def encontrar_equipo(self, jugador):
    if getattr(jugador, "equipo", None) is not None:
      return jugador.equipo

    contrato = jugador.contrato

    if contrato is not None and contrato.esta_vigente():
      return contrato.club

    return None

  def calcular_valor_jugador(self, jugador):
    valoracion = max(jugador.valoracion, 1)

    valor = (
      valoracion ** 2
      * 100
    )

    potencial = getattr(jugador, "potencial", None)
    if not isinstance(potencial, (int, float)):
      potencial = valoracion
    brecha_potencial = max(0, potencial - valoracion)
    valor += brecha_potencial * max(1, valoracion) * 20

    if jugador.edad <= 23:
      valor *= 1.20
    elif jugador.edad <= 28:
      valor *= 1.10
    elif jugador.edad >= 33:
      valor *= 0.80

    contrato = jugador.contrato

    if (
      contrato is not None
      and contrato.esta_vigente()
    ):
      valor *= 1.10

    return round(valor)

  def calcular_salario(self, jugador):
    return max(
      1000,
      jugador.valoracion * 100
    )

  def hacer_oferta(
    self,
    jugador,
    comprador,
    monto=None,
    salario_semanal=0,
    duracion_semanas=52
  ):
    vendedor = self.encontrar_equipo(jugador)

    if vendedor is None:
      return None

    if vendedor == comprador:
      return None

    if jugador not in vendedor.jugadores:
      return None

    if monto is None:
      monto = self.calcular_valor_jugador(jugador)

    if monto <= 0:
      return None

    if not comprador.puede_comprar(monto):
      return None

    if salario_semanal <= 0:
      salario_semanal = self.calcular_salario(jugador)

    oferta = OfertaTransferencia(
      self,
      jugador,
      vendedor,
      comprador,
      monto,
      salario_semanal,
      duracion_semanas
    )

    self.ofertas.append(oferta)
    return oferta

  def aceptar_oferta(self, oferta):
    if oferta not in self.ofertas:
      return False

    if oferta.estado != "pendiente":
      return False

    jugador = oferta.jugador
    vendedor = oferta.vendedor
    comprador = oferta.comprador

    if jugador not in vendedor.jugadores:
      oferta.estado = "cancelada"
      return False

    if getattr(jugador, "controlado", False) and not jugador.en_lista_transferibles:
      oferta.estado = "cancelada"
      return False

    if not comprador.puede_comprar(oferta.monto):
      oferta.estado = "cancelada"
      return False

    if not comprador.pagar_transferencia(
      oferta.monto
    ):
      oferta.estado = "cancelada"
      return False

    vendedor.cobrar_transferencia(
      oferta.monto
    )

    vendedor.eliminar_jugador(jugador)
    comprador.agregar_jugador(jugador)

    if jugador.contrato is not None:
      jugador.contrato.activo = False

    jugador.semanas_desde_ultimo_contrato = 0
    jugador.en_lista_transferibles = False

    nuevo_contrato = Contrato(
      jugador,
      comprador,
      oferta.salario_semanal,
      oferta.duracion_semanas
    )

    jugador.contrato = nuevo_contrato

    if jugador.representante is not None:
      jugador.representante.cobrar_comision(
        nuevo_contrato
      )

    oferta.estado = "aceptada"
    self.transferencias.append(oferta)

    vendedor.actualizar_valoracion()
    comprador.actualizar_valoracion()

    return True

  def rechazar_oferta(self, oferta):
    if oferta not in self.ofertas:
      return False

    return oferta.rechazar()

  def obtener_ofertas_pendientes(self):
    pendientes = []

    for oferta in self.ofertas:
      if oferta.estado == "pendiente":
        pendientes.append(oferta)

    return pendientes

  def obtener_transferencias(self):
    return list(self.transferencias)

  def contar_jugadores_por_posicion(self, equipo):
    cantidades = {
      "arquero": 0,
      "defensor": 0,
      "mediocampista": 0,
      "delantero": 0
    }

    for jugador in equipo.jugadores:
      posicion = jugador.obtener_posicion_normalizada()
      cantidades[posicion] += 1

    return cantidades

  def obtener_necesidades(self, equipo):
    cantidades = self.contar_jugadores_por_posicion(
      equipo
    )

    necesidades = []

    for posicion, minimo in self.NECESIDADES_POSICION.items():
      faltantes = minimo - cantidades[posicion]

      if faltantes > 0:
        necesidades.extend(
          [posicion] * faltantes
        )

    return necesidades

  def jugador_puede_ser_vendido(
    self,
    jugador,
    vendedor,
    jugador_usuario=None
  ):
    if jugador is jugador_usuario:
      return False

    if getattr(jugador, "controlado", False):
      return False

    if jugador not in vendedor.jugadores:
      return False

    if len(vendedor.jugadores) <= 16:
      return False

    posicion = jugador.obtener_posicion_normalizada()
    cantidades = self.contar_jugadores_por_posicion(
      vendedor
    )

    if cantidades[posicion] <= 1:
      return False

    return True

  def seleccionar_candidato(
    self,
    comprador,
    equipos,
    jugador_usuario=None,
    jugadores_excluidos=None
  ):
    if jugadores_excluidos is None:
      jugadores_excluidos = set()
    necesidades = self.obtener_necesidades(comprador)

    if not necesidades:
      # Un club completo solo busca reforzarse si
      # encuentra una mejora clara.
      posiciones = list(
        self.NECESIDADES_POSICION.keys()
      )
    else:
      posiciones = list(dict.fromkeys(necesidades))

    candidatos = []

    for equipo in equipos:
      if equipo == comprador:
        continue

      for jugador in equipo.jugadores:
        if jugador in jugadores_excluidos:
          continue

        if not self.jugador_puede_ser_vendido(
          jugador,
          equipo,
          jugador_usuario
        ):
          continue

        posicion = jugador.obtener_posicion_normalizada()

        if posicion not in posiciones:
          continue

        if jugador.valoracion < max(
          comprador.valoracion - 5,
          1
        ):
          continue

        candidatos.append(jugador)

    if not candidatos:
      return None

    candidatos.sort(
      key=lambda jugador: jugador.valoracion,
      reverse=True
    )

    mejores = candidatos[:5]
    return random.choice(mejores)

  def generar_oferta_npc(
    self,
    comprador,
    equipos,
    jugador_usuario=None,
    jugadores_excluidos=None
  ):
    jugador = self.seleccionar_candidato(
      comprador,
      equipos,
      jugador_usuario,
      jugadores_excluidos
    )

    if jugador is None:
      return None

    valor = self.calcular_valor_jugador(jugador)

    variacion = random.uniform(0.90, 1.10)
    monto = round(valor * variacion)

    if not comprador.puede_comprar(monto):
      return None

    return self.hacer_oferta(
      jugador,
      comprador,
      monto,
      self.calcular_salario(jugador),
      52
    )

  def decidir_oferta_npc(self, oferta):
    if oferta is None:
      return False

    jugador = oferta.jugador
    valor = self.calcular_valor_jugador(jugador)

    if valor <= 0:
      return False

    relacion = oferta.monto / valor

    # Cuanto mejor sea la oferta respecto al valor de mercado,
    # mayor es la posibilidad de aceptarla.
    if relacion >= 1.05:
      probabilidad = 0.90
    elif relacion >= 0.95:
      probabilidad = 0.70
    elif relacion >= 0.85:
      probabilidad = 0.45
    else:
      probabilidad = 0.20

    return random.random() < probabilidad

  def ejecutar_ventana_npc(
    self,
    equipos,
    jugador_usuario=None,
    max_transferencias_por_equipo=1
  ):
    if not equipos:
      return []

    operaciones = []
    operaciones_por_equipo = {}
    jugadores_transferidos = set()

    orden = list(equipos)
    random.shuffle(orden)

    for comprador in orden:
      operaciones_por_equipo.setdefault(
        comprador,
        0
      )

      if (
        operaciones_por_equipo[comprador]
        >= max_transferencias_por_equipo
      ):
        continue

      oferta = self.generar_oferta_npc(
        comprador,
        equipos,
        jugador_usuario,
        jugadores_transferidos
      )

      if oferta is None:
        continue

      if not self.decidir_oferta_npc(oferta):
        oferta.rechazar()
        continue

      if oferta.aceptar():
        operaciones.append(oferta)
        jugadores_transferidos.add(
          oferta.jugador
        )
        operaciones_por_equipo[comprador] += 1
        operaciones_por_equipo[oferta.vendedor] = (
          operaciones_por_equipo.get(
            oferta.vendedor,
            0
          ) + 1
        )

    return operaciones

  def generar_ofertas_para_jugador(self, jugador, equipos, max_ofertas=3):
    if jugador.equipo is None or not jugador.en_lista_transferibles:
      return []

    ofertas = []
    vendedores = jugador.equipo
    for comprador in equipos:
      if comprador is vendedores:
        continue
      if len(ofertas) >= max_ofertas:
        break
      if comprador.presupuesto <= 0:
        continue

      necesidades = self.obtener_necesidades(comprador)
      posicion = jugador.obtener_posicion_normalizada()
      if necesidades and posicion not in necesidades:
        continue

      valor = self.calcular_valor_jugador(jugador)
      monto = round(valor * random.uniform(0.85, 1.10))
      if not comprador.puede_comprar(monto):
        continue

      oferta = self.hacer_oferta(
        jugador,
        comprador,
        monto,
        self.calcular_salario(jugador),
        52
      )
      if oferta is not None:
        ofertas.append(oferta)

    return ofertas

  def limpiar_ofertas_finalizadas(self):
    self.ofertas = [
      oferta
      for oferta in self.ofertas
      if oferta.estado == "pendiente"
    ]


