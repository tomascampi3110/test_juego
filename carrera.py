import random
from jugador import Jugador
from equipo import Equipo
from competiciones import Liga
from temporada import Temporada
from contratos import Contrato
from tienda import TiendaEquipamiento
from mejoras import MejoraCarrera
from economia import Inversion
from negociacion import NegociacionContrato
from casino import Casino
from personalizacion import personalizar_jugador, agregar_tatuaje
from retiro import SistemaRetiro
from clubes_reales import CLUBES_ARGENTINA


class Carrera:
  def __init__(self, jugador, temporada, liga):
    self.jugador = jugador
    self.temporada = temporada
    self.liga = liga
    self.casino = Casino()
    self.retiro = SistemaRetiro()
    self.historial = []
    self.ofertas_contractuales = []
    self.semanas_desde_charla_presidente = 99

  @staticmethod
  def potencial_inicial_segun_edad(edad, valoracion):
    """El potencial máximo tiende a ser mayor cuanto más joven es el jugador."""
    if edad <= 18:
      minimo, maximo = 84, 94
    elif edad <= 20:
      minimo, maximo = 80, 91
    elif edad <= 23:
      minimo, maximo = 75, 87
    elif edad <= 26:
      minimo, maximo = 70, 82
    elif edad <= 29:
      minimo, maximo = 65, 77
    else:
      minimo, maximo = 60, 72

    minimo = max(int(valoracion), minimo)
    maximo = max(minimo, maximo)
    return random.randint(minimo, maximo)

  @classmethod
  def nueva(cls, nombre, edad=None, posicion="delantero", anio=2026):
    equipos = []
    clubes = CLUBES_ARGENTINA
    nombres = [club["nombre"] for club in clubes]

    # La carrera del usuario siempre empieza a los 18 años.
    # Se conserva el parámetro edad por compatibilidad con las pruebas/versiones previas.
    edad_inicial = 18
    jugador_usuario = Jugador(nombre, edad_inicial, posicion)
    # El jugador controlado progresa gastando puntos de mejora; no tiene potencial.
    jugador_usuario.potencial = None
    jugador_usuario.desarrollo = 0
    jugador_usuario.dinero = 50000

    for indice, nombre_equipo in enumerate(nombres):
      ficha_club = clubes[indice]
      equipo = Equipo(
        nombre_equipo,
        ficha_club["estadio"],
        f"Entrenador {indice + 1}",
        None
      )
      equipo.sigla = ficha_club["sigla"]
      equipo.ciudad = ficha_club["ciudad"]
      equipo.ruta_escudo = f"assets/escudos/{ficha_club['sigla'].lower()}.png"
      equipo.presupuesto = random.randint(250000, 1500000)

      cantidad_npc = 17 if indice == len(nombres) - 1 else 18
      posiciones = ["arquero", "defensor", "mediocampista", "delantero"]

      for numero in range(cantidad_npc):
        posicion_npc = posiciones[numero % len(posiciones)]
        npc = Jugador(
          f"Jugador {indice + 1}-{numero + 1}",
          random.randint(18, 34),
          posicion_npc
        )
        for estadistica in npc.estadisticas:
          npc.estadisticas[estadistica] = random.randint(35, 75)
        npc.desarrollo = random.randint(20, 80)
        npc.calcular_valoracion()
        npc.potencial = cls.potencial_inicial_segun_edad(
          npc.edad,
          npc.valoracion
        )
        equipo.agregar_jugador(npc)

      equipo.actualizar_valoracion()
      equipos.append(equipo)

    liga = Liga("Liga Nacional", equipos, 1)
    for equipo in equipos:
      equipo.liga = liga

    equipo_inicial = equipos[-1]
    equipo_inicial.presupuesto = min(equipo_inicial.presupuesto, 350000)
    equipo_inicial.actualizar_valoracion()

    temporada = Temporada(anio)
    temporada.agregar_competicion(liga)
    temporada.establecer_jugador_usuario(jugador_usuario)
    temporada.iniciar()
    temporada.bolsa_sponsors.actualizar(1)
    temporada.bolsa_equipamiento.actualizar(1)

    carrera = cls(jugador_usuario, temporada, liga)
    carrera.generar_ofertas_contractuales(inicial=True)
    return carrera

  def jugar_siguiente_semana(self):
    if self.temporada.estado != "en juego":
      return {"ok": False, "mensaje": "La temporada ya terminó."}

    pendientes = [
      item for item in self.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    self.temporada.eventos_sociales_pendientes = pendientes
    if pendientes:
      return {
        "ok": False,
        "requiere_evento": True,
        "evento": pendientes[0]["evento"],
        "mensaje": "Tenés una notificación pendiente. Resolvela antes de avanzar."
      }

    semana_jugada = self.temporada.semana
    partidos = self.temporada.obtener_partidos_semana(semana_jugada)
    pendientes = [partido for partido in partidos if partido.estado == "pendiente"]

    self.temporada.simular_semana()
    if self.jugador.equipo is None:
      self.jugador.procesar_semana()
    self.temporada.avanzar_semana()
    self.semanas_desde_charla_presidente += 1
    self.otorgar_puntos_mejora(semana_jugada)
    if self.jugador.contrato is None or not self.jugador.contrato.esta_vigente():
      if semana_jugada % 2 == 0:
        self.generar_ofertas_contractuales()

    resumen = {
      "ok": True,
      "semana": semana_jugada,
      "partidos": len(pendientes),
      "nota": self.jugador.historial_notas[-1] if self.jugador.historial_notas else None,
      "dinero": self.jugador.dinero,
      "semana_siguiente": self.temporada.semana,
      "estado": self.temporada.estado
    }
    self.historial.append(resumen)
    return resumen


  def otorgar_puntos_mejora(self, semana):
    """Entrega puntos acumulables según el rendimiento y el nivel de la carrera."""
    nota = self.jugador.historial_notas[-1] if self.jugador.historial_notas else 5.0
    # La progresión debe permitir varias mejoras significativas por temporada.
    # Base semanal + bonificaciones por rendimiento y pertenecer a un club.
    base = 8
    if nota >= 8:
      base += 5
    elif nota >= 7:
      base += 3
    elif nota < 5:
      base -= 2
    equipo = self.jugador.equipo
    if equipo is not None:
      base += 2 if equipo.valoracion >= 65 else 1
    # Estar libre no bloquea el desarrollo: se mantiene la base completa.
    base = max(5, base)
    self.jugador.puntos_mejora += base
    return base

  def generar_ofertas_contractuales(self, inicial=False):
    """Crea ofertas de clubes que el jugador puede aceptar o rechazar."""
    if self.jugador.contrato is not None and self.jugador.contrato.esta_vigente():
      return []
    equipos = [e for e in self.liga.equipos if self.jugador not in e.jugadores]
    equipos.sort(key=lambda e: abs(e.valoracion - self.jugador.valoracion))
    cantidad = 3 if inicial else 1
    nuevas = []
    for equipo in equipos[:cantidad]:
      if any(o["equipo"] is equipo and o["estado"] == "pendiente" for o in self.ofertas_contractuales):
        continue
      salario = max(1000, int(self.jugador.valoracion * random.randint(45, 85)))
      oferta = {"equipo": equipo, "salario": salario, "duracion": 52, "estado": "pendiente"}
      self.ofertas_contractuales.append(oferta)
      nuevas.append(oferta)
    return nuevas

  def responder_oferta_contractual(self, oferta, aceptar):
    if oferta not in self.ofertas_contractuales or oferta["estado"] != "pendiente":
      return {"ok": False, "mensaje": "Esta oferta ya no está disponible."}
    if not aceptar:
      oferta["estado"] = "rechazada"
      return {"ok": True, "mensaje": "Oferta rechazada."}
    if self.jugador.equipo is not None:
      self.jugador.equipo.eliminar_jugador(self.jugador)
    equipo = oferta["equipo"]
    equipo.agregar_jugador(self.jugador)
    self.jugador.contrato = Contrato(self.jugador, equipo, oferta["salario"], oferta["duracion"])
    oferta["estado"] = "aceptada"
    self.liga.recalcular_tabla() if hasattr(self.liga, "recalcular_tabla") else None
    return {"ok": True, "mensaje": f"Firmaste con {equipo.nombre} por ${oferta['salario']:,} semanales."}

  def negociar_contrato(self):
    equipo = self.jugador.equipo
    salario = max(1000, self.jugador.valoracion * 100)
    return NegociacionContrato(self.jugador, equipo, salario, 52)

  def solicitar_renovacion(self):
    negociacion = self.negociar_contrato()
    return negociacion.pedir_renovacion(), negociacion

  def solicitar_lista_transferibles(self):
    import random

    jugador = self.jugador
    contrato = jugador.contrato
    probabilidad = 0.50

    if jugador.historial_notas:
      promedio = sum(jugador.historial_notas[-5:]) / len(jugador.historial_notas[-5:])
      if promedio < 5:
        probabilidad += 0.20
      elif promedio >= 8:
        probabilidad -= 0.15

    if contrato is not None and contrato.esta_vigente():
      if contrato.semanas_restantes > 39:
        probabilidad -= 0.15
      elif contrato.semanas_restantes <= 12:
        probabilidad += 0.15

    probabilidad -= max(0, jugador.vinculos.get("club", 50) - 50) / 300
    probabilidad = max(0.10, min(0.90, probabilidad))

    if random.random() <= probabilidad:
      jugador.solicitar_lista_transferibles()
      return {
        "ok": True,
        "mensaje": "El club aceptó tu solicitud. Podés recibir ofertas en la próxima ventana de mercado."
      }

    jugador.vinculos["club"] = max(0, jugador.vinculos.get("club", 50) - 3)
    return {
      "ok": False,
      "mensaje": "El club rechazó tu solicitud por ahora. La relación con la dirigencia se resintió un poco."
    }

  def comprar_equipamiento(self, identificador):
    return TiendaEquipamiento.comprar_y_equipar(
      self.jugador,
      identificador
    )

  def comprar_oferta_equipamiento(self, indice):
    return self.temporada.bolsa_equipamiento.comprar(
      self.jugador,
      indice
    )

  def comprar_mejora(self, identificador):
    return MejoraCarrera.comprar(self.jugador, identificador)

  def comprar_inversion(self, identificador):
    if identificador not in Inversion.CATALOGO:
      return {"ok": False, "mensaje": "La inversión seleccionada no existe."}

    oferta = Inversion.CATALOGO[identificador]
    if any(getattr(inv, "identificador", None) == identificador for inv in self.jugador.inversiones):
      return {"ok": False, "mensaje": "Ya tenés esta inversión. Mejorala hasta el nivel máximo en lugar de comprar otra."}
    if self.jugador.valoracion < oferta.get("valoracion_minima", 0):
      return {"ok": False, "mensaje": f"Necesitás valoración {oferta['valoracion_minima']} para acceder a esta inversión."}
    patrimonio = self.jugador.dinero + sum(getattr(inv, "dinero_invertido", 0) for inv in self.jugador.inversiones)
    if patrimonio < oferta.get("patrimonio_minimo", 0):
      return {"ok": False, "mensaje": f"Necesitás un patrimonio de ${oferta['patrimonio_minimo']:,} para acceder a esta inversión."}
    if self.jugador.dinero < oferta["costo"]:
      return {"ok": False, "mensaje": "No tenés dinero suficiente para esa inversión."}

    inversion = Inversion(
      oferta["nombre"],
      oferta["tipo"],
      oferta["costo"],
      oferta["ingreso_semanal"]
    )
    if not self.jugador.agregar_inversion(inversion):
      return {"ok": False, "mensaje": "No se pudo registrar la inversión."}

    self.jugador.dinero -= oferta["costo"]
    return {"ok": True, "mensaje": f"Inversión adquirida: {oferta['nombre']}."}

  def personalizar(self, atributo, valor):
    return personalizar_jugador(self.jugador, atributo, valor)

  def comprar_tatuaje(self, nombre, precio):
    return agregar_tatuaje(self.jugador, nombre, precio)

  def aceptar_sponsor(self, indice):
    if not 0 <= indice < len(self.temporada.bolsa_sponsors.ofertas):
      return False

    oferta = self.temporada.bolsa_sponsors.ofertas[indice]
    return oferta.aceptar(self.jugador)

  def resolver_evento_social(self, evento, indice_opcion):
    resultado = evento.elegir(self.jugador, indice_opcion)
    if resultado["ok"]:
      self.temporada.eventos_sociales_pendientes = [
        item for item in self.temporada.eventos_sociales_pendientes
        if item["evento"] is not evento
      ]
    return resultado

  def extender_carrera(self):
    return self.retiro.extender_carrera(self.jugador)

  def retirarse(self):
    if not self.retiro.debe_retirarse(self.jugador):
      return {
        "ok": False,
        "mensaje": f"Tu edad de retiro es {self.jugador.edad_retiro}. Todavía podés seguir jugando."
      }

    self.retiro.finalizar_carrera(self.jugador)
    self.temporada.estado = "terminada"
    return {
      "ok": True,
      "mensaje": "Te retiraste del fútbol profesional. La carrera quedó finalizada."
    }

  def estado_resumido(self):
    equipo = self.jugador.equipo.nombre if self.jugador.equipo else "Sin club"
    contrato = self.jugador.contrato
    salario = contrato.salario_semanal if contrato and contrato.esta_vigente() else 0
    restante = contrato.semanas_restantes if contrato and contrato.esta_vigente() else 0

    return {
      "nombre": self.jugador.nombre,
      "edad": self.jugador.edad,
      "posicion": self.jugador.posicion,
      "valoracion": self.jugador.valoracion,
      "forma": self.jugador.forma,
      "dinero": self.jugador.dinero,
      "equipo": equipo,
      "salario": salario,
      "semanas_contrato": restante,
      "semana": self.temporada.semana,
      "temporada": self.temporada.anio,
      "estado_temporada": self.temporada.estado
    }
