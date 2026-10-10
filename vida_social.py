import random


class Vinculo:
  def __init__(self, nombre, nivel=50):
    self.nombre = nombre
    self.nivel = max(0, min(100, int(nivel)))

  def modificar(self, cantidad):
    self.nivel = max(0, min(100, self.nivel + int(cantidad)))
    return self.nivel


class OpcionSocial:
  def __init__(self, texto, coste=0, efectos=None):
    self.texto = texto
    self.coste = max(0, int(coste))
    self.efectos = dict(efectos or {})

  def ejecutar(self, jugador):
    if jugador.dinero < self.coste:
      return {"ok": False, "mensaje": "No tenés dinero suficiente."}

    jugador.dinero -= self.coste
    cambios = {}

    for clave, cantidad in self.efectos.items():
      if clave.startswith("vinculo:"):
        nombre = clave.split(":", 1)[1]
        actual = jugador.vinculos.get(nombre, 50 if nombre != "pareja" else 0)
        nuevo = max(0, min(100, actual + cantidad))
        jugador.vinculos[nombre] = nuevo
        cambios[clave] = nuevo
      elif clave == "bienestar":
        jugador.bienestar = max(0, min(100, jugador.bienestar + cantidad))
        cambios[clave] = jugador.bienestar
      elif clave == "forma":
        jugador.forma = max(0, min(100, jugador.forma + cantidad))
        cambios[clave] = jugador.forma
      elif clave == "pareja_nueva" and jugador.pareja is None:
        genero = self.efectos.get("pareja_genero") or random.choice(["mujer", "hombre"])
        nombres = {"mujer": ["Sofía", "Valentina", "Camila", "Martina", "Lucía", "Julieta", "Micaela", "Florencia", "Agustina", "Milagros", "Renata", "Abril"], "hombre": ["Mateo", "Julián", "Thiago", "Benjamín", "Nicolás", "Franco", "Bruno", "Agustín", "Santiago", "Tomás", "Lautaro", "Facundo"]}
        jugador.pareja_genero = genero
        jugador.pareja = self.efectos.get("pareja_nombre") or random.choice(nombres[genero])
        jugador.estado_relacion = "en pareja"
        jugador.semanas_relacion = 0
        jugador.vinculos["pareja"] = 50
        articulo = "un chico" if genero == "hombre" else "una chica"
        cambios[clave] = f"Conociste {articulo} llamado/a {jugador.pareja}."

    mensaje = "Actividad completada."
    if "pareja_nueva" in cambios:
      mensaje = cambios["pareja_nueva"]
    return {"ok": True, "mensaje": mensaje, "cambios": cambios}


class EventoSocial:
  def __init__(self, identificador, titulo, descripcion, opciones, tipo="companeros"):
    self.identificador = identificador
    self.titulo = titulo
    self.descripcion = descripcion
    self.opciones = opciones
    self.tipo = tipo
    self.resuelto = False

  def elegir(self, jugador, indice):
    if self.resuelto or not 0 <= indice < len(self.opciones):
      return {"ok": False, "mensaje": "Esta opción no está disponible."}

    resultado = self.opciones[indice].ejecutar(jugador)
    if resultado["ok"]:
      self.resuelto = True
      jugador.historial_eventos_sociales.append({
        "evento": self.identificador,
        "opcion": self.opciones[indice].texto
      })

    return resultado


class SistemaVidaSocial:
  def __init__(self):
    self.eventos_generados = []
    self.pareja_nombres = ["Alex", "Sam", "Noa", "Luca", "Dani"]

  def crear_pareja(self, jugador, nombre=None, genero=None):
    if jugador.pareja is not None:
      return False
    genero = genero or random.choice(["mujer", "hombre"])
    nombres = {"mujer": ["Sofía", "Valentina", "Camila", "Martina", "Lucía", "Julieta", "Micaela", "Florencia"], "hombre": ["Mateo", "Julián", "Thiago", "Benjamín", "Nicolás", "Franco", "Bruno", "Agustín"]}
    jugador.pareja_genero = genero
    jugador.pareja = nombre or random.choice(nombres.get(genero, self.pareja_nombres))
    jugador.estado_relacion = "en pareja"
    jugador.semanas_relacion = 0
    jugador.vinculos["pareja"] = 50
    return True

  def hablar_con_presidente(self, jugador):
    relacion = jugador.vinculos.get("gerente", 50)
    if jugador.historial_notas and sum(jugador.historial_notas[-3:]) / len(jugador.historial_notas[-3:]) >= 7.5:
      saludo = "Te estuvimos siguiendo: venís rindiendo muy bien. ¿Qué tal, para qué venís a hablar hoy?"
    elif relacion < 35:
      saludo = "Tenemos algunas diferencias pendientes. ¿Qué querés hablar hoy?"
    else:
      saludo = "¿Qué tal? ¿Para qué venís a hablar hoy?"
    return {"saludo": saludo, "opciones": ["Hablar del contrato", "Consultar el mercado de pases", "Hablar de tus minutos", "Preguntar por el futuro en el club"]}

  def procesar_relacion(self, jugador):
    """Avanza hitos familiares lentamente y según la calidad de la relación."""
    if jugador.pareja is None:
      return None
    jugador.semanas_relacion += 1
    nivel = jugador.vinculos.get("pareja", 0)
    if nivel <= 12 and jugador.semanas_relacion >= 4 and random.random() < 0.18:
      nombre = jugador.pareja
      jugador.pareja = None
      jugador.pareja_genero = None
      jugador.estado_relacion = "soltero"
      jugador.vinculos["pareja"] = 0
      jugador.semanas_relacion = 0
      return {"tipo": "ruptura", "titulo": "La relación llegó a su fin", "descripcion": f"Después de un tiempo de distanciamiento, {nombre} decidió terminar la relación."}
    if jugador.estado_relacion == "en pareja" and jugador.semanas_relacion >= 26 and nivel >= 75 and random.random() < 0.025:
      jugador.estado_relacion = "casado"
      jugador.semanas_matrimonio = 0
      return {"tipo": "casamiento", "titulo": "¡Se casaron!", "descripcion": f"Vos y {jugador.pareja} decidieron dar el siguiente paso y casarse."}
    if jugador.estado_relacion == "casado":
      jugador.semanas_matrimonio += 1
      if not jugador.hijos and jugador.semanas_matrimonio >= 40 and nivel >= 70 and random.random() < 0.012:
        genero = random.choice(["niño", "niña"])
        jugador.hijos.append({"genero": genero, "edad": 0})
        return {"tipo": "hijo", "titulo": "¡Llegó un nuevo integrante a la familia!", "descripcion": f"Tu familia creció: tuvieron un bebé, {genero}."}
    return None

  def procesar_semana(self, jugador, semana):
    hito = self.procesar_relacion(jugador)
    if hito is not None:
      evento = EventoSocial(hito["tipo"], hito["titulo"], hito["descripcion"], [OpcionSocial("Aceptar lo que pasó", 0, {"bienestar": 1})], hito["tipo"])
      self.eventos_generados.append((semana, evento))
      return evento
    if semana - jugador.ultima_semana_evento_social < 3:
      return None

    if random.random() > 0.55:
      return None

    jugador.ultima_semana_evento_social = semana
    evento = self.generar_evento(jugador)
    if evento is not None:
      self.eventos_generados.append((semana, evento))

    return evento

  def generar_evento(self, jugador):
    eventos = [
      EventoSocial(
        "cena_companeros",
        "Tus compañeros te invitan a cenar",
        "El grupo quiere pasar una noche juntos.",
        [
          OpcionSocial("Aceptar la cena", 1500, {"vinculo:companeros": 8, "bienestar": 4}),
          OpcionSocial("Quedarte descansando", 0, {"bienestar": 5, "forma": 2}),
          OpcionSocial("Invitarlos a un lugar de lujo", 7000, {"vinculo:companeros": 12, "bienestar": 6})
        ]
      ),
      EventoSocial(
        "reunion_gerente",
        "El gerente quiere hablar con vos",
        "La dirigencia te invita a conversar sobre tu futuro en el club.",
        [
          OpcionSocial("Hablar de tus objetivos deportivos", 0, {"vinculo:gerente": 6, "vinculo:club": 3}),
          OpcionSocial("Pedir mejores condiciones", 0, {"vinculo:gerente": -1, "vinculo:club": -1}),
          OpcionSocial("Agradecer y seguir trabajando", 0, {"vinculo:gerente": 2, "bienestar": 2})
        ],
        "gerente"
      ),
      EventoSocial(
        "actividad_club",
        "Actividad del club",
        "El club organiza una actividad para el plantel.",
        [
          OpcionSocial("Participar", 0, {"vinculo:club": 4, "vinculo:companeros": 5}),
          OpcionSocial("No asistir", 0, {"bienestar": 1})
        ],
        "club"
      )
    ]

    if jugador.pareja is None:
      genero_candidato = random.choice(["mujer", "hombre"])
      nombres_candidatos = {
        "mujer": ["Sofía", "Valentina", "Camila", "Martina", "Lucía", "Julieta", "Micaela", "Florencia", "Agustina", "Milagros", "Renata", "Abril"],
        "hombre": ["Mateo", "Julián", "Thiago", "Benjamín", "Nicolás", "Franco", "Bruno", "Agustín", "Santiago", "Tomás", "Lautaro", "Facundo"]
      }
      nombre_candidato = random.choice(nombres_candidatos[genero_candidato])
      articulo = "un chico" if genero_candidato == "hombre" else "una chica"
      opciones_pareja = [
        OpcionSocial("Invitar a salir", 1200, {"pareja_nueva": 1, "pareja_genero": genero_candidato, "pareja_nombre": nombre_candidato, "bienestar": 5}),
        OpcionSocial("Seguir como conocidos", 0, {"bienestar": 2}),
        OpcionSocial("No avanzar por ahora", 0, {})
      ]
      eventos.append(
        EventoSocial(
          "conocer_persona",
          "Conociste a alguien",
          f"En un evento social conociste a {articulo} llamado/a {nombre_candidato}. Se quedaron hablando y parece que hay interés mutuo.",
          opciones_pareja,
          "pareja"
        )
      )

    if jugador.pareja is not None:
      eventos.append(
        EventoSocial(
          "cita_pareja",
          f"{jugador.pareja} quiere salir",
          "Tu pareja quiere pasar tiempo con vos.",
          [
            OpcionSocial("Organizar una cita", 2500, {"vinculo:pareja": 10, "bienestar": 5}),
            OpcionSocial("Proponer algo tranquilo en casa", 300, {"vinculo:pareja": 5, "bienestar": 3}),
            OpcionSocial("Decir que no podés esta semana", 0, {"vinculo:pareja": -4})
          ],
          "pareja"
        )
      )

    return random.choice(eventos)
