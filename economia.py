class Sponsor:
  CATEGORIAS = {
    "local": {
      "valoracion": 5,
      "lujo": 0
    },
    "deportivo": {
      "valoracion": 30,
      "lujo": 2
    },
    "deluxe": {
      "valoracion": 70,
      "lujo": 5
    }
  }

  def __init__(
    self,
    nombre,
    categoria,
    pago_semanal,
    duracion_semanas,
    categoria_comercial=None,
    bono_rendimiento=0
  ):
    if categoria not in self.CATEGORIAS:
      categoria = "local"

    self.nombre = nombre
    self.categoria = categoria
    self.categoria_comercial = categoria_comercial
    self.bono_rendimiento = max(0, int(bono_rendimiento))

    self.pago_semanal = pago_semanal

    self.duracion_semanas = (
      duracion_semanas
    )

    self.semanas_restantes = (
      duracion_semanas
    )

    requisitos = self.CATEGORIAS[
      categoria
    ]

    self.requisito_valoracion = (
      requisitos["valoracion"]
    )

    self.requisito_lujo = (
      requisitos["lujo"]
    )

    self.activo = True

  def puede_contratar(
    self,
    jugador
  ):
    if jugador.valoracion < (
      self.requisito_valoracion
    ):
      return False

    nivel_lujo = getattr(
      jugador,
      "nivel_lujo",
      len(jugador.lujo)
    )
    if nivel_lujo < self.requisito_lujo:
      return False

    return True

  def pagar(
    self,
    jugador
  ):
    if not self.activo:
      return 0

    pago = round(
      self.pago_semanal
      * getattr(jugador, "bonificadores", {}).get("sponsors", 1.0)
    )
    jugador.dinero += pago

    return pago

  def avanzar_semana(
    self,
    jugador
  ):
    if not self.activo:
      return

    self.pagar(jugador)

    if (
      self.bono_rendimiento > 0
      and jugador.historial_notas
      and sum(jugador.historial_notas[-3:]) / len(jugador.historial_notas[-3:]) >= 8
    ):
      bono = round(
        self.bono_rendimiento
        * getattr(jugador, "bonificadores", {}).get("sponsors", 1.0)
      )
      jugador.dinero += bono

    self.semanas_restantes -= 1

    if self.semanas_restantes <= 0:
      self.semanas_restantes = 0
      self.activo = False

  def __str__(
    self
  ):
    return (
      f"Sponsor: {self.nombre}\n"
      f"Categoría: {self.categoria}\n"
      f"Pago semanal: "
      f"${self.pago_semanal}\n"
      f"Semanas restantes: "
      f"{self.semanas_restantes}\n"
      f"Valoración mínima: "
      f"{self.requisito_valoracion}\n"
      f"Lujo mínimo: "
      f"{self.requisito_lujo}"
    )


class Inversion:
  CATALOGO = {
    "negocio": {
      "nombre": "Negocio local",
      "tipo": "negocio",
      "costo": 10000,
      "ingreso_semanal": 450,
      "descripcion": "Un negocio pequeño con ingresos semanales estables.",
      "valoracion_minima": 40,
      "patrimonio_minimo": 0
    },
    "inmobiliaria": {
      "nombre": "Propiedad en alquiler",
      "tipo": "inmobiliaria",
      "costo": 25000,
      "ingreso_semanal": 950,
      "descripcion": "Comprá una propiedad y cobrá alquiler cada semana.",
      "valoracion_minima": 55,
      "patrimonio_minimo": 15000
    },
    "financiera": {
      "nombre": "Fondo de inversión",
      "tipo": "financiera",
      "costo": 50000,
      "ingreso_semanal": 2100,
      "descripcion": "Mayor inversión inicial y mayores ingresos semanales.",
      "valoracion_minima": 65,
      "patrimonio_minimo": 40000
    },
    "fabrica": {
      "nombre": "Fábrica propia",
      "tipo": "negocio",
      "costo": 250000,
      "ingreso_semanal": 9500,
      "descripcion": "Un emprendimiento industrial de gran escala.",
      "valoracion_minima": 80,
      "patrimonio_minimo": 200000
    }
  }

  TIPOS = {
    "negocio": {
      "riesgo": 10,
      "ingreso_base": 50
    },
    "inmobiliaria": {
      "riesgo": 5,
      "ingreso_base": 40
    },
    "financiera": {
      "riesgo": 30,
      "ingreso_base": 75
    }
  }

  def __init__(
    self,
    nombre,
    tipo,
    costo,
    ingreso_semanal
  ):
    if tipo not in self.TIPOS:
      tipo = "negocio"

    self.nombre = nombre
    self.tipo = tipo
    self.identificador = next((clave for clave, datos in self.CATALOGO.items() if datos["nombre"] == nombre), nombre.lower().replace(" ", "_"))

    self.costo = costo
    self.ingreso_semanal = ingreso_semanal

    self.nivel = 1
    self.dinero_invertido = costo

    self.activa = True

  def generar_ingreso(
    self,
    jugador
  ):
    if not self.activa:
      return 0

    ingreso = round(
      self.ingreso_semanal
      * getattr(jugador, "bonificadores", {}).get("inversiones", 1.0)
    )
    jugador.dinero += ingreso

    return ingreso

  def mejorar(
    self,
    jugador,
    costo
  ):
    if self.nivel >= 5:
      return False

    if costo <= 0:
      return False

    if jugador.dinero < costo:
      return False

    jugador.dinero -= costo

    self.dinero_invertido += costo

    self.nivel += 1

    self.ingreso_semanal += (
      costo * 0.05
    )

    return True

  def __str__(
    self
  ):
    return (
      f"Inversión: {self.nombre}\n"
      f"Tipo: {self.tipo}\n"
      f"Nivel: {self.nivel}\n"
      f"Dinero invertido: "
      f"${self.dinero_invertido}\n"
      f"Ingreso semanal: "
      f"${self.ingreso_semanal}"
    )

