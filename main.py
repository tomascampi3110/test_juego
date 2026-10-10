__version__ = "0.1.0"

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle

from carrera import Carrera
from temporada import Temporada
from guardado import GestorGuardado
from tienda import TiendaEquipamiento
from mejoras import MejoraCarrera
from economia import Inversion
from personalizacion import OPCIONES_APARIENCIA
from avatar import AvatarWidget
from zonas_tabla import zona_tabla

RUTA_GUARDADO = "partida.career"


class FondoLabel(Label):
  """Label con fondo coloreado para distinguir filas de la tabla."""
  def __init__(self, fondo=(0.12, 0.14, 0.18, 1), color_texto=(0.92, 0.94, 0.97, 1), **kwargs):
    super().__init__(color=color_texto, **kwargs)
    with self.canvas.before:
      self._color_fondo = Color(*fondo)
      self._rect_fondo = Rectangle(pos=self.pos, size=self.size)
    self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

  def _actualizar_fondo(self, *_):
    self._rect_fondo.pos = self.pos
    self._rect_fondo.size = self.size


class MenuPrincipal(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(
      orientation="vertical",
      padding=40,
      spacing=18
    )

    layout.add_widget(Label(
      text="FOOTBALL GAME",
      font_size=32
    ))

    for texto, accion in [
      ("NUEVA CARRERA", self.nueva_carrera),
      ("CARGAR PARTIDA", self.cargar_partida),
      ("SALIR", self.salir)
    ]:
      boton = Button(text=texto, font_size=20)
      boton.bind(on_press=accion)
      layout.add_widget(boton)

    self.add_widget(layout)

  def nueva_carrera(self, *_):
    App.get_running_app().mostrar_pantalla("crear")

  def cargar_partida(self, *_):
    app = App.get_running_app()
    try:
      estado = GestorGuardado.cargar(RUTA_GUARDADO)
      app.carrera = estado["carrera"]
      app.mostrar_carrera()
    except FileNotFoundError:
      app.mostrar_mensaje("No hay una partida guardada en la ruta predeterminada.")
    except Exception as error:
      app.mostrar_mensaje(f"No se pudo cargar la partida: {error}")

  def salir(self, *_):
    App.get_running_app().stop()


class CrearJugador(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(orientation="vertical", padding=30, spacing=12)
    layout.add_widget(Label(text="Crear futbolista", font_size=26))

    self.nombre = TextInput(hint_text="Nombre del jugador", multiline=False)
    self.posicion = Spinner(
      text="Delantero",
      values=("Defensor", "Mediocampista", "Delantero")
    )

    layout.add_widget(self.nombre)
    layout.add_widget(Label(
      text="Edad inicial: 18 años. Mejorá tus atributos usando puntos de mejora.",
      size_hint_y=None,
      height=48
    ))
    layout.add_widget(self.posicion)

    boton_crear = Button(text="EMPEZAR CARRERA")
    boton_crear.bind(on_press=self.crear)
    layout.add_widget(boton_crear)

    boton_volver = Button(text="VOLVER")
    boton_volver.bind(on_press=lambda *_: App.get_running_app().mostrar_pantalla("menu"))
    layout.add_widget(boton_volver)
    self.add_widget(layout)

  def crear(self, *_):
    app = App.get_running_app()
    nombre = self.nombre.text.strip()

    if not nombre:
      app.mostrar_mensaje("Ingresá un nombre para el jugador.")
      return

    app.carrera = Carrera.nueva(nombre, 18, self.posicion.text.lower())
    app.mostrar_carrera()


class GloboTexto(BoxLayout):
  """Globo visual para mensajes breves entre partidos."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(0.09, 0.16, 0.25, 1)
      self._fondo_globo = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
    self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

  def _actualizar_fondo(self, *_):
    self._fondo_globo.pos = self.pos
    self._fondo_globo.size = self.size


class PantallaCarrera(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    raiz = BoxLayout(orientation="vertical", padding=8, spacing=5)

    # Cabecera compacta: guardado y salida siempre accesibles.
    cabecera = BoxLayout(size_hint_y=None, height=40, spacing=6)
    cabecera.add_widget(Label(text="MI CARRERA", bold=True, font_size=18))
    guardar = Button(text="GUARDAR", size_hint_x=None, width=105)
    guardar.bind(on_press=self.guardar)
    cabecera.add_widget(guardar)
    menu = Button(text="MENÚ", size_hint_x=None, width=80)
    menu.bind(on_press=self.volver)
    cabecera.add_widget(menu)
    raiz.add_widget(cabecera)

    self.contenido_principal = BoxLayout(orientation="vertical", spacing=6)
    raiz.add_widget(self.contenido_principal)

    # Resumen de novedades sin cadena de ventanas.
    self.cola_globos = []
    self.popup_globo = None
    self.mensaje = Label(text="Tu carrera está pausada.", size_hint_y=None, height=34, font_size=13)
    raiz.add_widget(self.mensaje)

    self.barra_inferior = GridLayout(cols=5, size_hint_y=None, height=62, spacing=3)
    self.botones_nav = {}
    for clave, etiqueta in [
      ("inicio", "⌂\nInicio"),
      ("futbol", "⚽\nFútbol"),
      ("club", "♜\nClub"),
      ("relaciones", "♡\nRelaciones"),
      ("economia", "$\nEconomía"),
    ]:
      boton = Button(text=etiqueta, font_size=12)
      boton.bind(on_press=lambda _, k=clave: self.mostrar_seccion(k))
      self.botones_nav[clave] = boton
      self.barra_inferior.add_widget(boton)
    raiz.add_widget(self.barra_inferior)
    self.add_widget(raiz)
    self.seccion_actual = "inicio"

  def mostrar_seccion(self, seccion):
    self.seccion_actual = seccion
    self.contenido_principal.clear_widgets()
    for clave, boton in self.botones_nav.items():
      boton.background_color = (0.16, 0.19, 0.25, 1) if clave != seccion else (0.16, 0.42, 0.31, 1)

    if seccion == "inicio":
      self._mostrar_inicio()
      return

    acciones = {
      "futbol": [
        ("PRÓXIMO PARTIDO · CONTINUAR CARRERA", self.continuar_carrera),
        ("Tabla de posiciones", self.ver_tabla_posiciones),
        ("Calendario y resultados", self.ver_calendario),
      ],
      "club": [
        ("Situación contractual", self.ver_contrato),
        ("Mercado de pases", self.ver_mercado),
        ("Tienda de equipamiento", self.ver_tienda),
        ("Mejoras de atributos y carrera", self.ver_mejoras),
      ],
      "relaciones": [
        ("Charlar con el presidente", self.charlar_presidente),
        ("Mis vínculos", self.ver_vinculos),
        ("Logros", self.ver_logros),
        ("Eventos y notificaciones", self.ver_evento_social),
      ],
      "economia": [
        ("Ver patrocinadores y ofertas", self.abrir_sponsors),
        ("Administrar inversiones", self.ver_inversiones),
        ("Mejoras permanentes", self.ver_mejoras),
        ("Casino", self.ver_casino),
      ],
    }
    titulo = {"futbol":"FÚTBOL", "club":"MI CLUB", "relaciones":"RELACIONES", "economia":"ECONOMÍA"}[seccion]
    contenido = GridLayout(cols=1, spacing=8, padding=8, size_hint_y=None)
    contenido.bind(minimum_height=contenido.setter("height"))
    contenido.add_widget(Label(text=titulo, size_hint_y=None, height=38, bold=True, font_size=20))
    if seccion == "economia":
      contenido.add_widget(Label(text="Ingresos, contratos comerciales e inversiones", size_hint_y=None, height=30))
    for texto, accion in acciones[seccion]:
      boton = Button(text=texto, size_hint_y=None, height=52)
      boton.bind(on_press=accion)
      contenido.add_widget(boton)
    scroll = ScrollView()
    scroll.add_widget(contenido)
    self.contenido_principal.add_widget(scroll)

  def _mostrar_inicio(self):
    # Reconstruir la pantalla desde cero evita apilar una copia del inicio
    # cada vez que se actualiza la carrera tras simular una semana.
    self.contenido_principal.clear_widgets()
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      self.contenido_principal.add_widget(Label(text="No hay una carrera cargada."))
      return
    datos = carrera.estado_resumido()
    panel = BoxLayout(orientation="vertical", spacing=4)
    # Retrato de presentación de mayor detalle para esta build de prueba móvil.
    # El avatar geométrico sigue disponible en la pantalla de personalización.
    ruta_retrato = "assets/jugador_portada.jpg"
    try:
      retrato = Image(source=ruta_retrato, size_hint_y=None, height=205, fit_mode="contain")
      panel.add_widget(retrato)
    except Exception:
      self.avatar = AvatarWidget(size_hint_y=None, height=155)
      self.avatar.actualizar_apariencia(carrera.jugador.apariencia)
      panel.add_widget(self.avatar)
    panel.add_widget(Label(
      text=f"{datos['nombre']} · {datos['edad']} años · {datos['posicion']}\n"
      f"{datos['equipo']}  |  VAL {datos['valoracion']}  |  Forma {datos['forma']}\n"
      f"${datos['dinero']:,.0f}  ·  Salario ${datos['salario']:,.0f}/sem.  ·  Puntos {carrera.jugador.puntos_mejora}\n"
      f"Contrato: {datos['semanas_contrato']} semanas  ·  Temporada {datos['temporada']} · Jornada {datos['semana']}",
      size_hint_y=None, height=88, halign="center", valign="middle", font_size=14
    ))
    proximo = self._obtener_proximo_partido()
    if proximo:
      rival, condicion, jornada = proximo
      panel.add_widget(FondoLabel(
        text=f"PRÓXIMO PARTIDO · JORNADA {jornada}\n\n{carrera.jugador.equipo.nombre}  vs  {rival}\n{condicion}",
        fondo=(0.08, 0.23, 0.18, 1), size_hint_y=None, height=92, font_size=17, halign="center"
      ))
    else:
      panel.add_widget(Label(text="No hay partidos pendientes en la temporada.", size_hint_y=None, height=60))
    jugar = Button(text="CONTINUAR CARRERA", size_hint_y=None, height=54, font_size=17)
    jugar.bind(on_press=self.continuar_carrera)
    panel.add_widget(jugar)
    atajos = GridLayout(cols=2, size_hint_y=None, height=94, spacing=6)
    for texto, accion in [
      ("Mejorar atributos · XP", self.ver_mejoras_atributos),
      ("Mejoras permanentes", self.ver_mejoras),
      ("Personalizar jugador", self.ver_personalizacion),
      ("Patrocinadores", self.abrir_sponsors),
      ("Situación contractual", self.ver_contrato),
    ]:
      boton = Button(text=texto)
      boton.bind(on_press=accion)
      atajos.add_widget(boton)
    panel.add_widget(atajos)
    self.contenido_principal.add_widget(panel)

  def _obtener_proximo_partido(self):
    carrera = App.get_running_app().carrera
    if carrera is None:
      return None
    equipo = carrera.jugador.equipo
    temporada = carrera.temporada
    for jornada in range(temporada.semana, len(carrera.liga.jornadas) + 1):
      for partido in temporada.obtener_partidos_semana(jornada):
        if equipo in (partido.local, partido.visitante) and partido.estado == "pendiente":
          rival = partido.visitante if partido.local == equipo else partido.local
          condicion = "LOCAL" if partido.local == equipo else "VISITANTE"
          return rival.nombre, condicion, jornada
    return None

  def abrir_sponsors(self, *_):
    carrera = App.get_running_app().carrera
    if carrera is None:
      return
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    desplazamiento = ScrollView()
    self.contenido_sponsors = GridLayout(cols=1, spacing=8, padding=8, size_hint_y=None)
    self.contenido_sponsors.bind(minimum_height=self.contenido_sponsors.setter("height"))
    desplazamiento.add_widget(self.contenido_sponsors)
    contenido.add_widget(desplazamiento)
    cerrar = Button(text="CERRAR", size_hint_y=None, height=44)
    contenido.add_widget(cerrar)
    popup = Popup(title="Patrocinadores", content=contenido, size_hint=(0.88, 0.84))
    cerrar.bind(on_press=popup.dismiss)
    self.refrescar_sponsors()
    popup.open()

  def actualizar(self):
    carrera = App.get_running_app().carrera
    if carrera is None:
      self.estado.text = "No hay carrera cargada."
      return

    if self.seccion_actual == "inicio":
      self.mostrar_seccion("inicio")
    self.refrescar_sponsors()

  def continuar_carrera(self, *_):
    """Simula la próxima semana cuando ya no quedan globos por leer."""
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      self.mensaje.text = "No hay una carrera cargada."
      return

    if self.popup_globo is not None:
      return

    if carrera.temporada.estado != "en juego":
      self.mensaje.text = "La temporada terminó. Podés revisar la tabla y los resultados."
      self.actualizar()
      return

    pendientes_sociales = [
      item for item in carrera.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if pendientes_sociales:
      self.mostrar_evento(pendientes_sociales[0]["evento"])
      return

    temporada = carrera.temporada
    semana_jugada = temporada.semana
    partidos_semana = temporada.obtener_partidos_semana(semana_jugada)
    equipo_jugador = carrera.jugador.equipo
    partido_jugador = next((
      partido for partido in partidos_semana
      if equipo_jugador in (partido.local, partido.visitante)
      and partido.estado == "pendiente"
    ), None)

    resultado = carrera.jugar_siguiente_semana()
    if resultado.get("requiere_evento"):
      self.mostrar_evento(resultado["evento"])
      return
    if not resultado.get("ok"):
      self.mensaje.text = resultado.get("mensaje", "No se pudo continuar la carrera.")
      self.actualizar()
      return

    mensajes = []
    if partido_jugador is not None and partido_jugador.estado == "terminado":
      goles_local, goles_visitante = partido_jugador.resultado
      mensajes.append(
        f"FINAL DEL PARTIDO\n\n{partido_jugador.local.nombre}  {goles_local} - "
        f"{goles_visitante}  {partido_jugador.visitante.nombre}"
      )
      if resultado.get("nota"):
        mensajes.append(f"TU RENDIMIENTO\n\n{resultado['nota']}")

    if temporada.estado == "en juego":
      siguiente_semana = temporada.semana
      partidos_siguientes = temporada.obtener_partidos_semana(siguiente_semana)
      equipo_actual = carrera.jugador.equipo
      proximo = next((
        partido for partido in partidos_siguientes
        if equipo_actual in (partido.local, partido.visitante)
        and partido.estado == "pendiente"
      ), None)
      if proximo is not None:
        rival = proximo.visitante if proximo.local == equipo_actual else proximo.local
        condicion = "jugás de local" if proximo.local == equipo_actual else "jugás de visitante"
        mensajes.append(
          f"PRÓXIMO PARTIDO\n\nTu siguiente partido es contra {rival.nombre}.\n"
          f"{condicion.capitalize()}."
        )
      mensajes.append(
        f"SEMANA {resultado.get('semana', semana_jugada)} COMPLETADA\n\n"
        f"Dinero disponible: ${carrera.jugador.dinero:,.0f}."
      )
    else:
      mensajes.append("FIN DE TEMPORADA\n\nTerminó la temporada. Revisá la tabla final y tus estadísticas.")

    pendientes_sociales = [
      item for item in temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if pendientes_sociales:
      mensajes.append(
        f"NUEVA NOTIFICACIÓN\n\nTenés un evento pendiente: {pendientes_sociales[0]['evento'].titulo}."
      )

    self.actualizar()
    if mensajes:
      # Toda la información semanal en una sola ventana, sin una cadena de popups.
      self.cola_globos = []
      self.mostrar_resumen_unico("\n\n────────────────────\n\n".join(mensajes))
    else:
      self.mensaje.text = "No hay novedades nuevas. Podés revisar las pestañas o continuar cuando quieras."

  def mostrar_resumen_unico(self, texto):
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    desplazamiento = ScrollView(do_scroll_x=False)
    etiqueta = Label(
      text=texto,
      size_hint_y=None,
      halign="left",
      valign="top",
      font_size=17,
      color=(0.96, 0.97, 1, 1)
    )
    etiqueta.bind(width=lambda widget, ancho: setattr(widget, "text_size", (ancho, None)))
    etiqueta.bind(texture_size=lambda widget, tam: setattr(widget, "height", tam[1] + 24))
    desplazamiento.add_widget(etiqueta)
    contenido.add_widget(desplazamiento)
    boton = Button(text="CERRAR NOVEDADES", size_hint_y=None, height=46)
    contenido.add_widget(boton)
    popup = Popup(
      title="Resumen de la semana",
      content=contenido,
      size_hint=(0.88, 0.78),
      auto_dismiss=False
    )
    boton.bind(on_press=lambda *_: self.cerrar_resumen(popup))
    self.popup_globo = popup
    popup.open()

  def cerrar_resumen(self, popup):
    popup.dismiss()
    self.popup_globo = None
    carrera = App.get_running_app().carrera
    pendientes = [
      item for item in carrera.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if carrera.temporada.estado != "en juego":
      self.mensaje.text = "Temporada finalizada. Podés revisar la tabla y las estadísticas."
    elif pendientes:
      self.mensaje.text = "Resumen visto. Tenés un evento pendiente en Relaciones; podés resolverlo cuando quieras."
    else:
      self.mensaje.text = "Resumen visto. La carrera quedó pausada: revisá lo que quieras y tocá CONTINUAR CARRERA cuando estés listo."

  def ver_tabla_posiciones(self, *_):
    carrera = App.get_running_app().carrera
    liga = carrera.liga
    if carrera.jugador.equipo is None:
      app = App.get_running_app()
      app.mostrar_mensaje("Todavía no tenés club. Podés revisar las ofertas en Club → Situación contractual; cuando firmes, la tabla de tu liga aparecerá acá.")
      return
    equipos_ordenados = liga.tabla()

    raiz = BoxLayout(orientation="vertical", padding=8, spacing=6)
    raiz.add_widget(Label(
      text=f"{liga.nombre} · Temporada {carrera.temporada.anio}",
      size_hint_y=None,
      height=32,
      font_size=18
    ))

    leyenda = GridLayout(cols=2, size_hint_y=None, height=52, spacing=4)
    leyenda.add_widget(FondoLabel(
      text="  1–4 · Copa principal", fondo=(0.10, 0.38, 0.22, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  5–9 · Copa secundaria", fondo=(0.10, 0.27, 0.48, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  Últimos 2 · Descenso", fondo=(0.48, 0.13, 0.16, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  Tu equipo", fondo=(0.65, 0.45, 0.08, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    raiz.add_widget(leyenda)

    desplazamiento = ScrollView(do_scroll_x=True)
    tabla = GridLayout(
      cols=10,
      spacing=1,
      size_hint=(None, None),
      row_default_height=32,
      row_force_default=True,
      width=900
    )
    tabla.bind(minimum_height=tabla.setter("height"))
    anchos = [42, 250, 48, 42, 42, 42, 48, 48, 48, 58]
    tabla.width = sum(anchos)

    encabezados = ["POS", "EQUIPO", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]
    for indice, encabezado in enumerate(encabezados):
      tabla.add_widget(FondoLabel(
        text=f"[b]{encabezado}[/b]",
        markup=True,
        fondo=(0.08, 0.09, 0.12, 1),
        size_hint_x=None,
        width=anchos[indice],
        size_hint_y=None,
        height=32,
        font_size=12
      ))

    colores_zona = {
      "copa_principal": (0.10, 0.25, 0.17, 1),
      "copa_secundaria": (0.10, 0.19, 0.30, 1),
      "descenso": (0.30, 0.12, 0.14, 1),
      "normal": (0.12, 0.14, 0.18, 1)
    }
    color_usuario = (0.42, 0.29, 0.06, 1)
    for posicion, equipo in enumerate(equipos_ordenados, start=1):
      diferencia = equipo.gf - equipo.gc
      valores = [
        str(posicion), equipo.nombre, str(equipo.pj), str(equipo.g),
        str(equipo.e), str(equipo.p), str(equipo.gf), str(equipo.gc),
        f"{diferencia:+d}", str(equipo.pts)
      ]
      zona = zona_tabla(posicion, len(equipos_ordenados))
      es_equipo_usuario = equipo is carrera.jugador.equipo
      for indice, valor in enumerate(valores):
        fondo = color_usuario if es_equipo_usuario else colores_zona[zona]
        # La celda de posición conserva el color de clasificación incluso en la fila del usuario.
        if indice == 0:
          fondo = colores_zona[zona]
        texto = f"[b]{valor}[/b]" if es_equipo_usuario or indice in (0, 9) else valor
        if indice == 1:
          boton_equipo = Button(
            text=texto,
            markup=True,
            background_normal="",
            background_color=fondo,
            color=(0.96, 0.96, 0.98, 1),
            size_hint_x=None,
            width=anchos[indice],
            size_hint_y=None,
            height=32,
            font_size=12,
            halign="left",
            valign="middle"
          )
          boton_equipo.bind(on_press=lambda _boton, equipo_seleccionado=equipo: self.ver_plantel_equipo(equipo_seleccionado))
          tabla.add_widget(boton_equipo)
        else:
          tabla.add_widget(FondoLabel(
            text=texto,
            markup=True,
            fondo=fondo,
            size_hint_x=None,
            width=anchos[indice],
            size_hint_y=None,
            height=32,
            font_size=12,
            halign="center",
            valign="middle",
            text_size=(anchos[indice], 32)
          ))

    desplazamiento.add_widget(tabla)
    raiz.add_widget(desplazamiento)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    popup = Popup(title="Tabla de posiciones", content=raiz, size_hint=(0.96, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_plantel_equipo(self, equipo):
    """Muestra el plantel, minutos/participaciones y estadísticas reales por competición."""
    raiz = BoxLayout(orientation="vertical", padding=10, spacing=8)
    cabecera_plantel = BoxLayout(orientation="horizontal", size_hint_y=None, height=82, spacing=10)
    ruta_escudo = getattr(equipo, "ruta_escudo", "")
    if ruta_escudo:
      cabecera_plantel.add_widget(Image(source=ruta_escudo, size_hint_x=None, width=72, fit_mode="contain"))
    cabecera_plantel.add_widget(Label(
      text=f"[b]{equipo.nombre}[/b]\nDT: {equipo.dt} · Estadio: {equipo.estadio}",
      markup=True, halign="left", valign="middle"
    ))
    raiz.add_widget(cabecera_plantel)
    selector = Spinner(
      text="Estadísticas generales",
      values=("Estadísticas generales", "Temporada actual", "Liga", "Copas"),
      size_hint_y=None, height=42
    )
    raiz.add_widget(selector)
    desplazamiento_plantel = ScrollView()
    lista = GridLayout(cols=1, spacing=4, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    desplazamiento_plantel.add_widget(lista)
    raiz.add_widget(desplazamiento_plantel)

    def cargar_lista(*_):
      lista.clear_widgets()
      jugadores = sorted(equipo.jugadores, key=lambda j: getattr(j, "valoracion", 0), reverse=True)
      if not jugadores:
        lista.add_widget(Label(text="Este equipo todavía no tiene jugadores cargados.", size_hint_y=None, height=42))
        return
      for jugador in jugadores:
        valoracion = getattr(jugador, "valoracion", 0)
        edad = getattr(jugador, "edad", "—")
        posicion = getattr(jugador, "posicion", "Sin posición")
        reales = getattr(jugador, "estadisticas_reales", {})
        if selector.text == "Temporada actual":
          datos = reales.get("temporada", {})
        elif selector.text == "Liga":
          datos = reales.get("liga", {})
        elif selector.text == "Copas":
          datos = reales.get("copas", {})
        else:
          datos = reales.get("general", {})
        partidos = datos.get("partidos", getattr(jugador, "partidos_jugados", 0))
        goles = datos.get("goles", getattr(jugador, "goles", 0))
        asistencias = datos.get("asistencias", getattr(jugador, "asistencias", 0))
        titularidades = datos.get("titularidades", 0)
        suplencias = datos.get("suplencias", max(0, partidos - titularidades))
        vallas = datos.get("vallas_invictas", 0)
        atajadas = datos.get("atajadas", 0)
        tarjetas_amarillas = datos.get("amarillas", 0)
        tarjetas_rojas = datos.get("rojas", 0)
        texto = (
          f"[b]{jugador.nombre}[/b] · {posicion} · {edad} años · VAL {valoracion}\n"
          f"PJ {partidos} · Titular {titularidades} · Suplente {suplencias} · "
          f"Goles {goles} · Asistencias {asistencias}\n"
          f"Vallas invictas {vallas} · Atajadas {atajadas} · "
          f"Amarillas {tarjetas_amarillas} · Rojas {tarjetas_rojas}"
        )
        lista.add_widget(FondoLabel(
          text=texto, markup=True, fondo=(0.12, 0.15, 0.20, 1),
          size_hint_y=None, height=76, font_size=12, halign="left", valign="middle",
          text_size=(680, 76)
        ))
    selector.bind(text=cargar_lista)
    cargar_lista()
    cerrar = Button(text="Volver", size_hint_y=None, height=42)
    popup = Popup(title=f"Plantel · {equipo.nombre}", content=raiz, size_hint=(0.92, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_calendario(self, *_):
    carrera = App.get_running_app().carrera
    temporada = carrera.temporada
    semanas = sorted({semana for semana in temporada.calendario})
    if not semanas:
      App.get_running_app().mostrar_mensaje("Todavía no hay partidos programados.")
      return

    raiz = BoxLayout(orientation="vertical", padding=10, spacing=8)
    controles = BoxLayout(size_hint_y=None, height=42, spacing=8)
    controles.add_widget(Label(text="Jornada:", size_hint_x=None, width=85))
    selector = Spinner(
      text=str(min(temporada.semana, max(semanas))),
      values=tuple(str(semana) for semana in semanas),
      size_hint_x=None,
      width=100
    )
    controles.add_widget(selector)
    controles.add_widget(Label(
      text="Elegí una jornada para consultar sus partidos.",
      halign="left"
    ))
    raiz.add_widget(controles)

    lista_scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=5, padding=4, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    lista_scroll.add_widget(lista)
    raiz.add_widget(lista_scroll)

    def actualizar_jornada(texto):
      lista.clear_widgets()
      semana = int(texto)
      partidos = temporada.obtener_partidos_semana(semana)
      partidos.sort(key=lambda partido: (
        partido.local.nombre.lower(), partido.visitante.nombre.lower()
      ))
      lista.add_widget(Label(
        text=f"JORNADA {semana} · {len(partidos)} PARTIDOS",
        size_hint_y=None,
        height=32,
        font_size=16
      ))
      if not partidos:
        lista.add_widget(Label(
          text="No hay partidos programados para esta jornada.",
          size_hint_y=None,
          height=40
        ))
        return

      for partido in partidos:
        if partido.estado == "terminado":
          marcador = f"{partido.resultado[0]} - {partido.resultado[1]}"
          estado = "FINAL"
        elif partido.estado == "en juego":
          marcador = f"{partido.resultado[0]} - {partido.resultado[1]}"
          estado = f"EN JUEGO · {partido.minuto}'"
        else:
          marcador = "vs"
          estado = "PENDIENTE"
        fila = BoxLayout(size_hint_y=None, height=46, spacing=6)
        fila.add_widget(Label(
          text=partido.local.nombre,
          halign="right",
          text_size=(None, None)
        ))
        fila.add_widget(Label(
          text=marcador,
          size_hint_x=None,
          width=100,
          bold=True
        ))
        fila.add_widget(Label(text=partido.visitante.nombre))
        fila.add_widget(Label(
          text=estado,
          size_hint_x=None,
          width=115,
          font_size=11
        ))
        lista.add_widget(fila)

    selector.bind(text=lambda _, texto: actualizar_jornada(texto))
    actualizar_jornada(selector.text)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    popup = Popup(title="Calendario y resultados", content=raiz, size_hint=(0.94, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def guardar(self, *_):
    app = App.get_running_app()
    try:
      ruta = GestorGuardado.guardar({"carrera": app.carrera}, RUTA_GUARDADO)
      app.mostrar_mensaje(f"Partida guardada en {ruta}.")
    except Exception as error:
      app.mostrar_mensaje(f"No se pudo guardar: {error}")

  def ver_sponsors(self, *_):
    self.refrescar_sponsors()

  def refrescar_sponsors(self):
    if not hasattr(self, "contenido_sponsors"):
      return
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      return

    lista = self.contenido_sponsors
    lista.clear_widgets()
    jugador = carrera.jugador
    lista.add_widget(Label(
      text=f"PATROCINADORES · {len(jugador.sponsors)}/{jugador.espacios_sponsor} espacios ocupados\nDinero: ${jugador.dinero:,.0f}",
      size_hint_y=None, height=56, font_size=17
    ))

    lista.add_widget(Label(text="CONTRATOS ACTIVOS", size_hint_y=None, height=32, bold=True))
    if jugador.sponsors:
      for sponsor in jugador.sponsors.values():
        lista.add_widget(Label(
          text=f"{sponsor.nombre} · ${sponsor.pago_semanal:,.0f}/semana · {sponsor.semanas_restantes} semanas",
          size_hint_y=None, height=48
        ))
    else:
      lista.add_widget(Label(text="Todavía no tenés patrocinadores contratados.", size_hint_y=None, height=42))

    bolsa = carrera.temporada.bolsa_sponsors
    if not bolsa.ofertas:
      bolsa.actualizar(carrera.temporada.semana)
    lista.add_widget(Label(text="OFERTAS DISPONIBLES · Tocá una para contratar", size_hint_y=None, height=42, bold=True))
    ofertas_disponibles = [
      (indice, oferta) for indice, oferta in enumerate(bolsa.ofertas)
      if oferta.estado == "disponible"
    ]
    if not ofertas_disponibles:
      lista.add_widget(Label(text="No hay ofertas disponibles en este momento.", size_hint_y=None, height=42))
    for indice, oferta in ofertas_disponibles:
      sponsor = oferta.sponsor
      texto = (
        f"{sponsor.nombre} · {sponsor.categoria_comercial}\n"
        f"${sponsor.pago_semanal:,.0f}/semana · {sponsor.duracion_semanas} semanas"
      )
      if oferta.bono_firma:
        texto += f" · Bono de firma ${oferta.bono_firma:,.0f}"
      if oferta.requisito_reputacion:
        texto += f" · Reputación requerida: {oferta.requisito_reputacion}"
      boton = Button(text=texto, size_hint_y=None, height=68)
      boton.bind(on_press=lambda _, i=indice: self.aceptar_sponsor(i))
      lista.add_widget(boton)

  def aceptar_sponsor(self, indice, popup=None):
    app = App.get_running_app()
    ok = app.carrera.aceptar_sponsor(indice)
    if ok:
      app.carrera.temporada.sistema_logros.actualizar(app.carrera.jugador)
      if popup is not None:
        popup.dismiss()
    app.mostrar_mensaje("Sponsor contratado." if ok else "No cumplís los requisitos, no hay espacio o ya tenés un sponsor de esa categoría.")
    self.actualizar()
    self.refrescar_sponsors()

  def ver_tienda(self, *_):
    app = App.get_running_app()
    carrera = app.carrera
    bolsa = carrera.temporada.bolsa_equipamiento
    if not bolsa.ofertas:
      bolsa.actualizar(carrera.temporada.semana)

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    popup = Popup(title="Oportunidades de equipamiento", content=contenido, size_hint=(0.85, 0.8))
    for indice, item in enumerate(bolsa.ofertas):
      texto = (
        f"{item['nombre']} · ${item['precio']}"
        f" (antes ${item['precio_original']})\n"
        f"-{item['descuento']}% · dura aprox. una temporada ({item['durabilidad']} partidos) · stock {item['stock']}"
      )
      boton = Button(text=texto, size_hint_y=None, height=65)
      boton.bind(on_press=lambda _, i=indice: self.comprar_oferta_equipo(i, popup))
      contenido.add_widget(boton)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_oferta_equipo(self, indice, popup):
    app = App.get_running_app()
    resultado = app.carrera.comprar_oferta_equipamiento(indice)
    if resultado["ok"]:
      popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def comprar_equipo(self, identificador):
    app = App.get_running_app()
    resultado = app.carrera.comprar_equipamiento(identificador)
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def ver_inversiones(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=6, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    contenido.add_widget(Label(
      text=f"Dinero disponible: ${jugador.dinero}\nIngresos semanales actuales: ${sum(inv.ingreso_semanal for inv in jugador.inversiones):.0f}",
      size_hint_y=None,
      height=55
    ))

    for identificador, oferta in Inversion.CATALOGO.items():
      req_val = oferta.get("valoracion_minima", 0)
      req_pat = oferta.get("patrimonio_minimo", 0)
      desbloqueada = jugador.valoracion >= req_val and jugador.dinero + sum(getattr(inv, "dinero_invertido", 0) for inv in jugador.inversiones) >= req_pat
      texto = (
        f"{oferta['nombre']} · ${oferta['costo']}\n"
        f"Ingreso semanal: ${oferta['ingreso_semanal']}\n{oferta['descripcion']}\n"
        f"Requisitos: valoración {req_val} · patrimonio ${req_pat:,} · {'DISPONIBLE' if desbloqueada else 'BLOQUEADA'}"
      )
      boton = Button(text=texto, size_hint_y=None, height=105, disabled=not desbloqueada)
      boton.bind(on_press=lambda _, ident=identificador: self.comprar_inversion(ident, popup))
      lista.add_widget(boton)

    if jugador.inversiones:
      lista.add_widget(Label(text="Tus inversiones", size_hint_y=None, height=35))
      for inversion in jugador.inversiones:
        lista.add_widget(Label(
          text=f"{inversion.nombre} · Nivel {inversion.nivel} · ${inversion.ingreso_semanal:.0f}/semana",
          size_hint_y=None,
          height=35
        ))
        mejorar = Button(
          text=f"Mejorar inversión · ${max(1000, inversion.costo // 2)}",
          size_hint_y=None,
          height=45
        )
        mejorar.bind(on_press=lambda _, inv=inversion: self.mejorar_inversion(inv, popup))
        lista.add_widget(mejorar)

    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    popup = Popup(title="Inversiones", content=contenido, size_hint=(0.88, 0.85))
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_inversion(self, identificador, popup=None):
    app = App.get_running_app()
    resultado = app.carrera.comprar_inversion(identificador)
    app.mostrar_mensaje(resultado["mensaje"])
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_inversiones()

  def mejorar_inversion(self, inversion, popup=None):
    app = App.get_running_app()
    costo = max(1000, inversion.costo // 2)
    if inversion.mejorar(app.carrera.jugador, costo):
      app.mostrar_mensaje(f"Mejoraste {inversion.nombre}; ahora genera ${inversion.ingreso_semanal:.0f} por semana.")
    else:
      app.mostrar_mensaje("No tenés dinero suficiente para mejorar esta inversión.")
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_inversiones()

  def ver_mejoras_atributos(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    contenido.add_widget(Label(text=f"XP / PUNTOS DISPONIBLES: {jugador.puntos_mejora}\nCada mejora cuesta XP según el nivel actual del atributo (valor actual + 5). Las barras muestran el costo de la próxima mejora.", size_hint_y=None, height=65))
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=5, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    for atributo, valor in jugador.estadisticas.items():
      fila = BoxLayout(size_hint_y=None, height=43, spacing=5)
      costo = jugador.costo_mejora_estadistica(atributo)
      if costo is None:
        costo_texto = "Máximo"
        boton_texto = "Máximo"
      else:
        costo_texto = f"{costo} XP"
        boton_texto = f"Mejorar ({costo})"
      fila.add_widget(Label(text=f"{atributo.title()}: {valor}/100\nPróxima mejora: {costo_texto}", halign="left"))
      mas = Button(text=boton_texto, size_hint_x=None, width=125, disabled=costo is None or jugador.puntos_mejora < costo)
      mas.bind(on_press=lambda _, a=atributo: self.aplicar_mejora_atributo(a, 1))
      fila.add_widget(mas)
      lista.add_widget(fila)
    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    popup = Popup(title="Atributos y puntos de mejora", content=contenido, size_hint=(0.9, 0.9))
    self.popup_atributos = popup
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def aplicar_mejora_atributo(self, atributo, cantidad):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    if cantidad > 0:
      anterior = jugador.valoracion
      costo = jugador.costo_mejora_estadistica(atributo)
      if costo is None or jugador.puntos_mejora < costo:
        app.mostrar_mensaje(f"Necesitás {costo if costo is not None else 'más'} XP para mejorar {atributo}. Te quedan {jugador.puntos_mejora}.")
      else:
        jugador.mejorar_estadistica(atributo, 1)
        app.mostrar_mensaje(f"{atributo.title()} mejoró. Valoración: {anterior} → {jugador.valoracion}. XP restantes: {jugador.puntos_mejora}.")
    if getattr(self, "popup_atributos", None) is not None:
      self.popup_atributos.dismiss()
    self.actualizar()
    self.ver_mejoras_atributos()

  def ver_mejoras(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=6, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    popup = Popup(title="Mejoras permanentes", content=contenido, size_hint=(0.88, 0.85))

    for identificador, mejora in MejoraCarrera.CATALOGO.items():
      nivel = MejoraCarrera.nivel(jugador, identificador)
      max_nivel = mejora["max_nivel"]
      precio = MejoraCarrera.costo_siguiente_nivel(jugador, identificador) if nivel < max_nivel else None
      if identificador == "espacio_sponsor":
        progreso = "Comprada" if nivel else "No adquirida"
      else:
        progreso = f"Nivel {nivel}/{max_nivel} · bonificación actual: +{round((jugador.bonificadores.get(mejora['bonificador'], 1.0) - 1) * 100)}%"
      texto_precio = f"${precio}" if precio is not None else "NIVEL MÁXIMO"
      boton = Button(
        text=f"{mejora['nombre']} · {texto_precio}\n{progreso}\n{mejora['descripcion']}" + (f" Cada nivel suma {int(mejora['incremento'] * 100)}%." if mejora["incremento"] else ""),
        size_hint_y=None,
        height=100,
        disabled=nivel >= max_nivel
      )
      boton.bind(on_press=lambda _, ident=identificador, pop=popup: self.comprar_mejora(ident, pop))
      lista.add_widget(boton)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_mejora(self, identificador, popup=None):
    app = App.get_running_app()
    ok = app.carrera.comprar_mejora(identificador)
    app.mostrar_mensaje("Mejora comprada: bonificación aumentada un 5%." if ok else "No tenés dinero suficiente o esa mejora llegó al nivel máximo.")
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_mejoras()

  def ver_evento_social(self, *_):
    app = App.get_running_app()
    pendientes = [
      item for item in app.carrera.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if not pendientes:
      self.mensaje.text = "No hay notificaciones sociales pendientes. Avanzá al próximo partido para recibir nuevas oportunidades."
      return
    self.mostrar_evento(pendientes[0]["evento"])

  def mostrar_evento(self, evento):
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    contenido.add_widget(Label(
      text=f"{evento.titulo}\n{evento.descripcion}\n\nElegí una opción para cerrar esta notificación y continuar la carrera."
    ))
    popup = Popup(title="Notificación de la carrera", content=contenido, size_hint=(0.85, 0.75), auto_dismiss=False)
    for indice, opcion in enumerate(evento.opciones):
      boton = Button(
        text=f"{opcion.texto} · ${opcion.coste}",
        size_hint_y=None,
        height=58
      )
      boton.bind(on_press=lambda _, i=indice: self.elegir_evento(evento, i, popup))
      contenido.add_widget(boton)

    dejar = Button(text="Dejar pendiente", size_hint_y=None, height=40)
    dejar.bind(on_press=popup.dismiss)
    contenido.add_widget(dejar)
    popup.open()

  def elegir_evento(self, evento, indice, popup=None):
    app = App.get_running_app()
    resultado = app.carrera.resolver_evento_social(evento, indice)
    if resultado["ok"] and popup is not None:
      popup.dismiss()
      self.mensaje.text = (
        f"Notificación resuelta: {evento.titulo}. La carrera quedó pausada; "
        "podés revisar otras pestañas y continuar cuando quieras."
      )
      self.actualizar()
      return
    else:
      self.mensaje.text = resultado["mensaje"]
    self.actualizar()

  def ver_contrato(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contrato = jugador.contrato

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=8)
    if contrato is None or not contrato.esta_vigente():
      contenido.add_widget(Label(text="Estás libre. Podés esperar ofertas o elegir una de las disponibles."))
      for oferta in app.carrera.ofertas_contractuales:
        if oferta["estado"] != "pendiente":
          continue
        bloque_oferta = BoxLayout(orientation="vertical", size_hint_y=None, height=94, spacing=3)
        fila_oferta = BoxLayout(size_hint_y=None, height=48, spacing=5)
        fila_oferta.add_widget(Label(text=f"{oferta['equipo'].nombre} · ${oferta['salario']}/sem."))
        ver_plantel = Button(text="Ver plantel", size_hint_x=None, width=105)
        ver_plantel.bind(on_press=lambda _, equipo=oferta["equipo"]: self.ver_plantel_equipo(equipo))
        aceptar = Button(text="Firmar", size_hint_x=None, width=82)
        aceptar.bind(on_press=lambda _, o=oferta: self.responder_oferta(o, True, popup))
        rechazar = Button(text="Rechazar", size_hint_x=None, width=90)
        rechazar.bind(on_press=lambda _, o=oferta: self.responder_oferta(o, False, popup))
        fila_oferta.add_widget(ver_plantel)
        fila_oferta.add_widget(aceptar)
        fila_oferta.add_widget(rechazar)
        bloque_oferta.add_widget(fila_oferta)
        resumen_plantel = Label(
          text=f"Plantel: {len(oferta['equipo'].jugadores)} jugadores · " +
          f"Arqueros: {sum(1 for j in oferta['equipo'].jugadores if j.posicion.lower() in ('arquero', 'portero'))}",
          size_hint_y=None, height=34, halign="left"
        )
        bloque_oferta.add_widget(resumen_plantel)
        contenido.add_widget(bloque_oferta)
    else:
      contenido.add_widget(Label(
        text=(
          f"Club: {contrato.club.nombre}\n"
          f"Salario: ${contrato.salario_semanal}/semana\n"
          f"Semanas restantes: {contrato.semanas_restantes}"
        )
      ))

    popup = Popup(title="Situación contractual", content=contenido, size_hint=(0.85, 0.8))

    boton_renovar = Button(text="Solicitar renovación", size_hint_y=None, height=48)
    boton_renovar.bind(on_press=lambda *_: self.accion_renovacion(popup))
    contenido.add_widget(boton_renovar)

    if contrato is None or not contrato.esta_vigente():
      boton_negociar = Button(text="Negociar contrato", size_hint_y=None, height=48)
      boton_negociar.bind(on_press=lambda *_: self.abrir_negociacion(popup))
      contenido.add_widget(boton_negociar)

    boton_transferible = Button(text="Pedir estar en lista de transferibles", size_hint_y=None, height=48)
    boton_transferible.bind(on_press=lambda *_: self.pedir_transferible(popup))
    contenido.add_widget(boton_transferible)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def responder_oferta(self, oferta, aceptar, popup):
    app = App.get_running_app()
    resultado = app.carrera.responder_oferta_contractual(oferta, aceptar)
    popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()
    self.ver_contrato()

  def accion_renovacion(self, popup_anterior):
    app = App.get_running_app()
    popup_anterior.dismiss()
    resultado, negociacion = app.carrera.solicitar_renovacion()
    if not resultado["ok"]:
      app.mostrar_mensaje(resultado["mensaje"])
      return
    self.mostrar_minijuego_negociacion(negociacion)

  def abrir_negociacion(self, popup_anterior):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    popup_anterior.dismiss()

    if jugador.contrato is not None and jugador.contrato.esta_vigente():
      resultado, negociacion = app.carrera.solicitar_renovacion()
      if not resultado["ok"]:
        app.mostrar_mensaje(resultado["mensaje"])
        return
      self.mostrar_minijuego_negociacion(negociacion)
      return

    self.mostrar_minijuego_negociacion(app.carrera.negociar_contrato())

  def mostrar_minijuego_negociacion(self, negociacion):
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(
      text=(
        f"El club ofrece ${negociacion.salario_ofrecido} por semana.\n"
        "Mové la mano hasta el punto que consideres adecuado y probá cerrar el acuerdo."
      ),
      size_hint_y=None,
      height=75
    ))
    slider = Slider(min=0, max=100, value=50, step=1)
    indice_objetivo = round(negociacion.objetivo / 5)
    pista = "·" * indice_objetivo + " 🤝 " + "·" * max(0, 20 - indice_objetivo)
    contenido.add_widget(Label(text=f"Posición objetivo del club\n{pista}", size_hint_y=None, height=50))
    contenido.add_widget(Label(text="Mové tu mano con el control y acercate al apretón."))
    contenido.add_widget(slider)
    popup = Popup(title="Negociación de contrato", content=contenido, size_hint=(0.85, 0.55))

    boton = Button(text="ESTRECHAR LAS MANOS", size_hint_y=None, height=48)
    boton.bind(on_press=lambda *_: self.resolver_negociacion(negociacion, slider.value, popup))
    contenido.add_widget(boton)
    cancelar = Button(text="Cancelar", size_hint_y=None, height=38)
    cancelar.bind(on_press=popup.dismiss)
    contenido.add_widget(cancelar)
    popup.open()

  def resolver_negociacion(self, negociacion, posicion, popup):
    app = App.get_running_app()
    resultado = negociacion.intentar_acuerdo(posicion)
    popup.dismiss()
    if resultado["ok"]:
      app.mostrar_mensaje(
        f"{resultado['mensaje']}\nSalario acordado: ${resultado['salario_semanal']}/semana."
      )
    else:
      app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def pedir_transferible(self, popup):
    app = App.get_running_app()
    resultado = app.carrera.solicitar_lista_transferibles()
    popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])

  def ver_casino(self, *_):
    app = App.get_running_app()
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    contenido.add_widget(Label(text=f"CASINO · Dinero disponible: ${app.carrera.jugador.dinero:,}\nApuesta mínima $100 · máxima $10.000", size_hint_y=None, height=55))
    apuesta = TextInput(text="100", hint_text="Apuesta", multiline=False, input_filter="int", size_hint_y=None, height=42)
    contenido.add_widget(apuesta)
    juego = Spinner(text="Ruleta", values=("Ruleta", "Tragamonedas", "Carrera de caballos", "Apuestas deportivas"), size_hint_y=None, height=42)
    contenido.add_widget(juego)
    eleccion = Spinner(text="rojo", values=("rojo", "negro", "par", "impar", "0", "7", "14", "21", "28", "Relámpago", "Tormenta", "Centella", "Sombra", "Equipo favorito"), size_hint_y=None, height=42)
    contenido.add_widget(eleccion)
    resultado_label = Label(text="Elegí el juego, la apuesta y la opción.", size_hint_y=None, height=65)
    contenido.add_widget(resultado_label)
    popup = Popup(title="Casino · dinero virtual", content=contenido, size_hint=(0.88, 0.78))

    def actualizar_opciones(spinner, valor):
      if valor == "Ruleta":
        eleccion.values = ("rojo", "negro", "par", "impar", "0", "7", "14", "21", "28")
        eleccion.text = "rojo"
      elif valor == "Tragamonedas":
        eleccion.values = ("Girar",)
        eleccion.text = "Girar"
      elif valor == "Carrera de caballos":
        eleccion.values = ("Relámpago", "Tormenta", "Centella", "Sombra")
        eleccion.text = "Relámpago"
      else:
        eleccion.values = ("Equipo favorito", "Equipo no favorito")
        eleccion.text = "Equipo favorito"

    juego.bind(text=actualizar_opciones)

    def apostar(_):
      try:
        monto = int(apuesta.text)
      except ValueError:
        resultado_label.text = "Ingresá un monto válido."
        return
      casino = app.carrera.casino
      if juego.text == "Ruleta":
        resultado = casino.jugar_ruleta(app.carrera.jugador, monto, eleccion.text)
      elif juego.text == "Tragamonedas":
        resultado = casino.jugar_tragamonedas(app.carrera.jugador, monto)
      elif juego.text == "Carrera de caballos":
        resultado = casino.jugar_carrera_caballos(app.carrera.jugador, monto, eleccion.text)
      else:
        resultado = casino.apostar_partido(app.carrera.jugador, monto, eleccion.text, 0.58 if eleccion.text == "Equipo favorito" else 0.42)
      resultado_label.text = resultado["mensaje"] + (f"\nResultado neto: ${resultado['neto']:+,}\nSaldo: ${resultado['dinero']:,}" if resultado["ok"] else "")
      self.actualizar()

    boton = Button(text="APOSTAR", size_hint_y=None, height=46)
    boton.bind(on_press=apostar)
    contenido.add_widget(boton)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_personalizacion(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    contenido.add_widget(Label(text="Personalización visual", size_hint_y=None, height=35))
    spinners = {}
    for atributo, opciones in OPCIONES_APARIENCIA.items():
      spinner = Spinner(
        text=jugador.apariencia.get(atributo, opciones[0]),
        values=tuple(opciones),
        size_hint_y=None,
        height=42
      )
      spinners[atributo] = spinner
      contenido.add_widget(Label(text=atributo.replace("_", " ").title(), size_hint_y=None, height=22))
      contenido.add_widget(spinner)

    popup = Popup(title="Personalizar futbolista", content=contenido, size_hint=(0.85, 0.9))
    guardar = Button(text="Guardar apariencia", size_hint_y=None, height=44)
    guardar.bind(on_press=lambda *_: self.guardar_apariencia(spinners, popup))
    contenido.add_widget(guardar)
    tatuaje = Button(text="Comprar tatuaje genérico · $25.000", size_hint_y=None, height=44)
    tatuaje.bind(on_press=lambda *_: self.comprar_tatuaje(popup))
    contenido.add_widget(tatuaje)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def guardar_apariencia(self, spinners, popup):
    app = App.get_running_app()
    for atributo, spinner in spinners.items():
      app.carrera.personalizar(atributo, spinner.text)
    popup.dismiss()
    self.actualizar()
    app.mostrar_mensaje("Apariencia guardada.")

  def comprar_tatuaje(self, popup):
    app = App.get_running_app()
    ok = app.carrera.comprar_tatuaje("Tatuaje genérico", 25000)
    popup.dismiss()
    self.actualizar()
    app.mostrar_mensaje("Tatuaje desbloqueado." if ok else "No tenés dinero suficiente o ya tenés ese tatuaje.")

  def ver_retiro(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(
      text=(
        f"Edad actual: {jugador.edad}\n"
        f"Edad prevista de retiro: {jugador.edad_retiro}\n"
        "Cuando alcances la edad de retiro, podés pagar para extender la carrera."
      )
    ))
    popup = Popup(title="Retiro profesional", content=contenido, size_hint=(0.8, 0.5))
    extender = Button(text="Extender una temporada", size_hint_y=None, height=46)
    extender.bind(on_press=lambda *_: self.confirmar_extension(popup))
    contenido.add_widget(extender)
    retirarse = Button(text="Retirarme", size_hint_y=None, height=46)
    retirarse.bind(on_press=lambda *_: self.confirmar_retiro(popup))
    contenido.add_widget(retirarse)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def confirmar_extension(self, popup):
    app = App.get_running_app()
    popup.dismiss()
    resultado = app.carrera.extender_carrera()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def confirmar_retiro(self, popup):
    app = App.get_running_app()
    popup.dismiss()
    resultado = app.carrera.retirarse()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def ver_perfil(self, *_):
    """Muestra un resumen compacto; el perfil principal ya está visible en la cabecera."""
    self.actualizar()
    self.mensaje.text = "Este es tu perfil: foto, club, valoración, forma, dinero y contrato aparecen arriba."

  def ver_logros(self, *_):
    jugador = App.get_running_app().carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    logros = sorted(jugador.logros)
    contenido.add_widget(Label(
      text=f"LOGROS DESBLOQUEADOS: {len(logros)}\n" + ("\n".join(f"• {logro}" for logro in logros) if logros else "Todavía no desbloqueaste logros."),
      halign="left", valign="top"
    ))
    popup = Popup(title="Logros", content=contenido, size_hint=(0.78, 0.65))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_vinculos(self, *_):
    jugador = App.get_running_app().carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    filas = [f"{nombre.replace('_', ' ').title()}: {nivel}/100" for nombre, nivel in jugador.vinculos.items()]
    contenido.add_widget(Label(
      text="RELACIONES DE TU CARRERA\n\n" + "\n".join(filas) + f"\n\nPareja: {jugador.pareja or 'Sin pareja'}" + (f" ({jugador.pareja_genero}) · Estado: {jugador.estado_relacion}" if jugador.pareja else "") + f"\nHijos: {len(jugador.hijos)}",
      halign="left", valign="top"
    ))
    popup = Popup(title="Mis vínculos", content=contenido, size_hint=(0.78, 0.65))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def charlar_presidente(self, *_):
    app = App.get_running_app()
    carrera = app.carrera
    jugador = carrera.jugador
    contrato = jugador.contrato
    semanas = contrato.semanas_restantes if contrato is not None and contrato.esta_vigente() else 0
    if carrera.semanas_desde_charla_presidente < 4:
      app.mostrar_mensaje("Ya hablaste con la dirigencia hace poco. Volvé a intentarlo dentro de unas semanas.")
      return
    saludo = carrera.temporada.sistema_vida_social.hablar_con_presidente(jugador)["saludo"]
    carrera.semanas_desde_charla_presidente = 0
    texto = (
      f"{saludo}\n\n"
      f"Presidencia de {jugador.equipo.nombre}.\n\n"
      f"Relación con el club: {jugador.vinculos.get('club', 50)}/100\n"
      f"Relación con el gerente: {jugador.vinculos.get('gerente', 50)}/100\n"
      f"Contrato vigente: {'Sí' if semanas else 'No'}\n"
      f"Semanas restantes: {semanas}\n\n"
      "Desde esta sección podés revisar tu situación contractual o consultar el mercado de pases."
    )
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    contenido.add_widget(Label(text=texto, halign="left", valign="middle"))
    popup = Popup(title="Charla con el presidente", content=contenido, size_hint=(0.82, 0.62))
    contrato_btn = Button(text="Ver situación contractual", size_hint_y=None, height=42)
    contrato_btn.bind(on_press=lambda *_: (popup.dismiss(), self.ver_contrato()))
    mercado_btn = Button(text="Consultar mercado de pases", size_hint_y=None, height=42)
    mercado_btn.bind(on_press=lambda *_: (popup.dismiss(), self.ver_mercado()))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(contrato_btn)
    contenido.add_widget(mercado_btn)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_mercado(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    mercado = app.carrera.temporada.mercado_pases
    ofertas = [
      oferta for oferta in mercado.obtener_ofertas_pendientes()
      if oferta.jugador is jugador
    ]

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    if not jugador.en_lista_transferibles:
      contenido.add_widget(Label(
        text="No estás en la lista de transferibles. Podés solicitarlo desde Situación contractual.",
        size_hint_y=None,
        height=70
      ))
    if not ofertas:
      contenido.add_widget(Label(
        text="No hay ofertas pendientes. Las ofertas de clubes pueden aparecer durante las ventanas de mercado.",
        size_hint_y=None,
        height=70
      ))

    popup = Popup(title="Mercado de pases", content=contenido, size_hint=(0.85, 0.8))
    for oferta in ofertas:
      boton = Button(
        text=(
          f"{oferta.comprador.nombre} ofrece ${oferta.monto}\n"
          f"Salario: ${oferta.salario_semanal}/semana"
        ),
        size_hint_y=None,
        height=65
      )
      boton.bind(on_press=lambda _, o=oferta: self.aceptar_oferta_usuario(o, popup))
      contenido.add_widget(boton)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def aceptar_oferta_usuario(self, oferta, popup):
    app = App.get_running_app()
    ok = oferta.aceptar()
    popup.dismiss()
    app.mostrar_mensaje(
      f"Transferencia concretada a {oferta.comprador.nombre}." if ok
      else "No se pudo concretar la transferencia."
    )
    self.actualizar()

  def volver(self, *_):
    App.get_running_app().mostrar_pantalla("menu")


class FootballGameApp(App):
  def build(self):
    self.carrera = None
    self.pantallas = ScreenManager()
    self.pantallas.add_widget(MenuPrincipal(name="menu"))
    self.pantallas.add_widget(CrearJugador(name="crear"))
    self.pantallas.add_widget(PantallaCarrera(name="carrera"))
    return self.pantallas

  def mostrar_pantalla(self, nombre):
    self.pantallas.current = nombre
    if nombre == "carrera":
      self.pantallas.get_screen("carrera").actualizar()

  def mostrar_carrera(self):
    self.mostrar_pantalla("carrera")

  def mostrar_mensaje(self, mensaje):
    if hasattr(self, "pantallas") and self.pantallas.current == "carrera":
      pantalla = self.pantallas.get_screen("carrera")
      pantalla.mensaje.text = str(mensaje)
      return

    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(text=str(mensaje)))
    boton = Button(text="Aceptar", size_hint_y=None, height=42)
    contenido.add_widget(boton)
    popup = Popup(title="Football Game", content=contenido, size_hint=(0.75, 0.5))
    boton.bind(on_press=popup.dismiss)
    popup.open()


if __name__ == "__main__":
  FootballGameApp().run()
