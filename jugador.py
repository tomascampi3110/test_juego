import random

class Jugador:
  PESOS_VALORACION = {
    "arquero": {
      "reaccion": 0.30,
      "anticipacion": 0.20,
      "precision": 0.15,
      "marca": 0.15,
      "salto": 0.10,
      "fuerza": 0.05,
      "resistencia": 0.05
    },

    "defensor": {
      "marca": 0.25,
      "anticipacion": 0.20,
      "fuerza": 0.15,
      "reaccion": 0.15,
      "velocidad": 0.10,
      "salto": 0.10,
      "resistencia": 0.05
    },

    "mediocampista": {
      "pase": 0.20,
      "vision": 0.20,
      "control": 0.15,
      "precision": 0.10,
      "resistencia": 0.10,
      "velocidad": 0.10,
      "reaccion": 0.10,
      "anticipacion": 0.05
    },

    "delantero": {
      "definicion": 0.25,
      "precision": 0.20,
      "regate": 0.15,
      "control": 0.15,
      "velocidad": 0.10,
      "fuerza": 0.05,
      "reaccion": 0.05,
      "salto": 0.05
    }
  }

  def __init__(
    self,
    nombre: str,
    edad: int,
    posicion: str
  ):
    self.nombre = nombre
    self.edad = edad
    self.posicion = posicion
    self.equipo = None
    self.controlado = False

    self.dinero = 0

    self.lujo = []
    self.sponsors = {}
    self.inversiones = []
    self.inventario = []

    self.contrato = None
    self.representante = None

    self.estadisticas = {
      "velocidad": 50,
      "fuerza": 50,
      "salto": 50,
      "precision": 50,
      "definicion": 50,
      "regate": 50,
      "control": 50,
      "pase": 50,
      "vision": 50,
      "marca": 50,
      "anticipacion": 50,
      "reaccion": 50,
      "resistencia": 50,
      "equilibrio": 50
    }

    self.valoracion = 50
    self.puntos_mejora = 0
    self.habilitado = True

    self.lesion = False
    self.semanas_lesion = 0
    self.amonestado = 0

    self.goles = 0
    self.asistencias = 0

    # Progresión deportiva
    self.potencial = 75
    self.desarrollo = 50
    self.forma = 50
    self.bienestar = 50
    self.partidos_jugados = 0
    self.estadisticas_reales = {
      categoria: {
        "partidos": 0, "titularidades": 0, "suplencias": 0,
        "minutos": 0, "goles": 0, "asistencias": 0,
        "amarillas": 0, "rojas": 0, "atajadas": 0,
        "vallas_invictas": 0, "penales_atajados": 0
      }
      for categoria in ("general", "temporada", "liga", "copas")
    }
    self.historial_notas = []
    self.goles_temporada = 0
    self.asistencias_temporada = 0
    self.titulos = 0
    self.semanas_carrera = 0
    self.semanas_desde_ultimo_contrato = 0
    self.intentos_negociacion = 0
    self.negociaciones_fallidas = 0
    self.en_lista_transferibles = False
    self.retiro_forzado = False
    self.edad_retiro = 38

    # Sistemas de carrera
    self.equipamiento = {}
    self.apariencia = {
      "peinado": "clasico",
      "color_pelo": "castanio",
      "ojos": "marrones",
      "rostro": "ovalado",
      "piel": "media",
      "tatuajes": []
    }
    self.mejoras_carrera = set()
    self.niveles_mejoras = {}
    self.logros = set()
    self.puntos_xp = 0
    self.historial_mejoras_atributos = []
    self.vinculos = {
      "hinchada": 50,
      "club": 50,
      "entrenador": 50,
      "gerente": 50,
      "companeros": 50,
      "pareja": 0
    }
    self.pareja = None
    self.pareja_genero = None
    self.estado_relacion = "soltero"
    self.semanas_relacion = 0
    self.semanas_matrimonio = 0
    self.hijos = []
    self.historial_eventos_sociales = []
    self.ultima_semana_evento_social = 0
    self.espacios_sponsor = 2
    self.nivel_lujo = 0
    self.bonificadores = {
      "inversiones": 1.0,
      "sponsors": 1.0,
      "experiencia": 1.0
    }

  def __str__(self):
    return (
      f"Nombre: {self.nombre}\n"
      f"Edad: {self.edad}\n"
      f"Posición: {self.posicion}\n"
      f"Valoración: {self.valoracion}"
    )

  def agregar_inversion(
    self,
    inversion
  ):
    if inversion in self.inversiones:
      return False

    self.inversiones.append(inversion)
    return True

  def agregar_objeto(
    self,
    objeto
  ):
    if objeto in self.inventario:
      return False

    self.inventario.append(objeto)
    if getattr(objeto, "tipo", None) == "lujo":
      self.lujo.append(objeto)
      self.nivel_lujo += 1
    return True

  def agregar_sponsor(
    self,
    sponsor
  ):
    if not sponsor.puede_contratar(self):
      return False

    categoria = getattr(
      sponsor,
      "categoria_comercial",
      None
    )

    if categoria is not None:
      for existente in self.sponsors.values():
        if getattr(
          existente,
          "categoria_comercial",
          None
        ) == categoria:
          return False

    if len(self.sponsors) >= self.espacios_sponsor:
      return False

    self.sponsors[sponsor.nombre] = sponsor
    return True

  def eliminar_sponsor(
    self,
    nombre
  ):
    if nombre not in self.sponsors:
      return False

    del self.sponsors[nombre]
    return True

  def obtener_posicion_normalizada(self):
    posicion = self.posicion.lower()

    if posicion in ["arquero", "portero", "arq", "por"]:
      return "arquero"

    if posicion in [
      "defensor",
      "defensa",
      "central",
      "lateral",
      "def",
      "df"
    ]:
      return "defensor"

    if posicion in [
      "mediocampista",
      "mediocampo",
      "volante",
      "medio",
      "mc",
      "mcd",
      "mco"
    ]:
      return "mediocampista"

    if posicion in [
      "delantero",
      "atacante",
      "extremo",
      "punta",
      "del",
      "dc"
    ]:
      return "delantero"

    return "mediocampista"

  def agregar_estadistica(
    self,
    estadistica_nombre,
    estadistica_nivel
  ):
    if estadistica_nombre not in self.estadisticas:
      print("La estadística no existe")
      return

    estadistica_nivel = max(
      0,
      min(estadistica_nivel, 100)
    )

    self.estadisticas[estadistica_nombre] = estadistica_nivel
    self.calcular_valoracion()

  def _costo_base_atributo(self, valor):
    if valor < 30:
      return 10 + valor // 3
    if valor < 50:
      return 25 + (valor - 30)
    if valor < 70:
      return 45 + (valor - 50) * 2
    if valor < 80:
      return 85 + (valor - 70) * 3
    if valor < 90:
      return 115 + (valor - 80) * 1
    return 125 + (valor - 90) * 4

  def costo_mejora_estadistica(self, estadistica_nombre):
    """Costo por tramos: el precio cambia cada diez mejoras de ese atributo."""
    valor = self.estadisticas.get(estadistica_nombre, 100)
    if valor >= 100:
      return None
    mejoras_previas = sum(
      1 for mejora in self.historial_mejoras_atributos
      if mejora.get("atributo") == estadistica_nombre
    )
    return int(self._costo_base_atributo(valor) + (mejoras_previas // 10) * 12)

  def mejorar_estadistica(
    self,
    estadistica_nombre,
    cantidad
  ):
    if estadistica_nombre not in self.estadisticas:
      return

    if cantidad <= 0:
      return

    valor_actual = self.estadisticas[estadistica_nombre]
    if valor_actual >= 100:
      return
    mejoras_previas = sum(
      1 for mejora in self.historial_mejoras_atributos
      if mejora.get("atributo") == estadistica_nombre
    )
    costo_total = 0
    valor_temporal = valor_actual
    for paso in range(cantidad):
      if valor_temporal >= 100:
        break
      tramo = (mejoras_previas + paso) // 10
      costo_base = self._costo_base_atributo(valor_temporal)
      costo_total += costo_base + tramo * 12
      valor_temporal += 1
    if costo_total > self.puntos_mejora or valor_temporal == valor_actual:
      return

    nuevo_valor = (
      self.estadisticas[estadistica_nombre]
      + cantidad
    )

    self.estadisticas[estadistica_nombre] = min(
      nuevo_valor,
      100
    )

    valor_anterior = self.valoracion
    self.puntos_mejora -= costo_total
    self.historial_mejoras_atributos.append({
      "atributo": estadistica_nombre,
      "antes": self.estadisticas[estadistica_nombre] - min(cantidad, 100 - (self.estadisticas[estadistica_nombre] - cantidad)),
      "despues": self.estadisticas[estadistica_nombre],
      "costo": costo_total
    })
    self.calcular_valoracion()

  def calcular_valoracion(self):
    posicion = self.obtener_posicion_normalizada()
    pesos = self.PESOS_VALORACION[posicion]

    valoracion = 0

    for estadistica, peso in pesos.items():
      valoracion += (
        self.estadisticas.get(estadistica, 0)
        * peso
      )

    self.valoracion = round(valoracion)

  def obtener_estadistica_base(self, nombre):
    return self.estadisticas.get(nombre, 0)

  def obtener_bonificacion_equipo(self, estadistica):
    bonificacion = 0

    for objeto in self.equipamiento.values():
      if not getattr(objeto, "activo", False):
        continue

      bonificacion += getattr(
        objeto,
        "atributos",
        {}
      ).get(estadistica, 0)

    return bonificacion

  def obtener_estadistica(self, nombre):
    base = self.obtener_estadistica_base(nombre)
    equipo = self.obtener_bonificacion_equipo(nombre)
    ajuste_forma = round((self.forma - 50) * 0.04)

    return max(
      0,
      min(100, base + equipo + ajuste_forma)
    )


  def atributos_relevantes(self):
    """Devuelve atributos prioritarios para la posición del jugador."""
    por_posicion = {
      "arquero": ("reaccion", "anticipacion", "salto", "fuerza", "resistencia", "precision"),
      "portero": ("reaccion", "anticipacion", "salto", "fuerza", "resistencia", "precision"),
      "defensor": ("marca", "anticipacion", "fuerza", "velocidad", "salto", "resistencia"),
      "mediocampista": ("pase", "vision", "control", "resistencia", "precision", "anticipacion"),
      "delantero": ("definicion", "precision", "regate", "control", "velocidad", "fuerza")
    }
    clave = self.posicion.lower()
    relevantes = por_posicion.get(clave, tuple(self.estadisticas))
    secundarios = tuple(nombre for nombre in self.estadisticas if nombre not in relevantes)
    return relevantes, secundarios

  def registrar_actuacion(self, nota, datos=None):
    nota = max(1.0, min(10.0, float(nota)))
    self.partidos_jugados += 1
    self.historial_notas.append(round(nota, 2))
    self.historial_notas = self.historial_notas[-10:]

    datos = datos or {}
    self.goles_temporada += datos.get("goles", 0)
    self.asistencias_temporada += datos.get("asistencias", 0)
    # Estadísticas deportivas reales, separadas de los atributos entrenables.
    categorias = ["general", "temporada"]
    competicion = str(datos.get("competicion", "liga")).lower()
    categorias.append("copas" if "copa" in competicion or "internacional" in competicion else "liga")
    for categoria in categorias:
      registro = self.estadisticas_reales.setdefault(categoria, {})
      registro["partidos"] = registro.get("partidos", 0) + 1
      titular = bool(datos.get("titular", True))
      clave_participacion = "titularidades" if titular else "suplencias"
      registro[clave_participacion] = registro.get(clave_participacion, 0) + 1
      for clave in ("minutos", "goles", "asistencias", "amarillas", "rojas", "atajadas", "vallas_invictas", "penales_atajados"):
        registro[clave] = registro.get(clave, 0) + int(datos.get(clave, 0))

    # La forma responde al rendimiento reciente, sin reemplazar la edad.
    self.forma = max(
      0,
      min(100, round(self.forma * 0.75 + nota * 10 * 0.25))
    )

    if nota >= 8:
      self.vinculos["hinchada"] = min(
        100,
        self.vinculos.get("hinchada", 50) + 2
      )
      self.vinculos["entrenador"] = min(
        100,
        self.vinculos.get("entrenador", 50) + 1
      )
    elif nota < 5:
      self.vinculos["entrenador"] = max(
        0,
        self.vinculos.get("entrenador", 50) - 2
      )
      self.vinculos["hinchada"] = max(
        0,
        self.vinculos.get("hinchada", 50) - 1
      )

  def desarrollar(self):
    # El desarrollo automático es exclusivo de los NPC. El usuario mejora
    # sus atributos gastando puntos de mejora.
    if self.controlado or self.potencial is None:
      return False

    if self.valoracion >= self.potencial:
      return False

    if self.edad >= 34:
      factor_edad = 0.02
    elif self.edad >= 30:
      factor_edad = 0.10
    elif self.edad >= 27:
      factor_edad = 0.30
    elif self.edad >= 24:
      factor_edad = 0.50
    elif self.edad >= 21:
      factor_edad = 0.70
    elif self.edad >= 18:
      factor_edad = 0.90
    else:
      factor_edad = 1.0

    brecha = self.potencial - self.valoracion
    factor_potencial = min(1.0, brecha / 30)
    probabilidad = min(
      0.95,
      self.desarrollo / 100
      * factor_edad
      * 0.50
      * factor_potencial
      * self.bonificadores.get("experiencia", 1.0)
    )

    if random.random() >= probabilidad:
      return False

    posicion = self.obtener_posicion_normalizada()
    pesos = self.PESOS_VALORACION[posicion]
    estadisticas = list(pesos.keys())
    probabilidades = list(pesos.values())
    elegida = random.choices(
      estadisticas,
      weights=probabilidades,
      k=1
    )[0]

    self.estadisticas[elegida] = min(
      100,
      self.estadisticas[elegida] + random.randint(1, 2)
    )
    valoracion_anterior = self.valoracion
    self.calcular_valoracion()

    if self.valoracion > self.potencial:
      self.estadisticas[elegida] -= self.valoracion - self.potencial
      self.calcular_valoracion()

    return self.valoracion > valoracion_anterior

  def procesar_semana(self):
    self.semanas_carrera += 1
    self.semanas_desde_ultimo_contrato += 1

    if self.semanas_carrera % 52 == 0:
      self.edad += 1
      self.aplicar_degradacion_edad()

    self.desarrollar()

    if self.lesion:
      self.semanas_lesion = max(0, self.semanas_lesion - 1)
      if self.semanas_lesion == 0:
        self.lesion = False

    # La forma cae lentamente si no hay actuaciones que la sostengan.
    if self.forma > 50:
      self.forma -= 1
    elif self.forma < 50:
      self.forma += 1

    self.bienestar = max(
      0,
      min(100, self.bienestar)
    )

    for objeto in list(self.equipamiento.values()):
      if getattr(objeto, "activo", False):
        objeto.avanzar_semana()
        if not objeto.activo:
          del self.equipamiento[objeto.espacio]

  def aplicar_degradacion_edad(self):
    """El declive se concentra en lo físico; la técnica envejece mucho menos."""
    if self.edad < 30:
      return

    fisicos = ["velocidad", "resistencia", "reaccion", "salto", "equilibrio"]
    tecnicos = ["precision", "pase", "vision", "control", "anticipacion"]
    if self.edad < 33:
      cantidad = 1
      pool = fisicos
    elif self.edad < 36:
      cantidad = random.choice([1, 2])
      pool = fisicos
    elif self.edad < 39:
      cantidad = random.choice([2, 3])
      pool = fisicos
      if random.random() < 0.25:
        pool = tecnicos
    else:
      cantidad = random.choice([2, 3, 4])
      pool = fisicos if random.random() < 0.8 else tecnicos

    for _ in range(cantidad):
      atributo = random.choice(pool)
      self.estadisticas[atributo] = max(20, self.estadisticas[atributo] - 1)

    # Los NPC pueden mantener o perder algo de técnica por experiencia, nunca gratis mejorar al usuario.
    if not self.controlado and 30 <= self.edad <= 35 and random.random() < 0.25:
      atributo = random.choice(tecnicos)
      self.estadisticas[atributo] = min(100, self.estadisticas[atributo] + 1)
    self.calcular_valoracion()

  def solicitar_lista_transferibles(self):
    self.en_lista_transferibles = True
    return True

  def cambiar_apariencia(self, atributo, valor):
    if atributo not in self.apariencia:
      return False

    if atributo == "tatuajes":
      if valor not in self.apariencia[atributo]:
        self.apariencia[atributo].append(valor)
    else:
      self.apariencia[atributo] = valor

    return True

  def esta_disponible(self):
    return (
      self.habilitado
      and not self.lesion
    )


