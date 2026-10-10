from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Line


class AvatarWidget(Widget):
  PIEL = {
    "clara": (0.94, 0.76, 0.62),
    "media": (0.68, 0.43, 0.28),
    "oscura": (0.34, 0.20, 0.13)
  }
  PELO = {
    "negro": (0.08, 0.06, 0.05),
    "castanio": (0.25, 0.13, 0.07),
    "rubio": (0.78, 0.60, 0.25),
    "pelirrojo": (0.55, 0.20, 0.08),
    "gris": (0.55, 0.55, 0.55)
  }
  OJOS = {
    "marrones": (0.25, 0.13, 0.05),
    "azules": (0.15, 0.42, 0.75),
    "verdes": (0.12, 0.45, 0.22),
    "grises": (0.48, 0.52, 0.55)
  }

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.apariencia = {
      "peinado": "clasico",
      "color_pelo": "castanio",
      "ojos": "marrones",
      "rostro": "ovalado",
      "piel": "media",
      "tatuajes": []
    }
    self.bind(pos=self.redibujar, size=self.redibujar)

  def actualizar_apariencia(self, apariencia):
    self.apariencia = dict(apariencia)
    self.redibujar()

  def redibujar(self, *_):
    self.canvas.clear()
    x, y = self.pos
    w, h = self.size
    if w <= 0 or h <= 0:
      return

    centro_x = x + w / 2
    cabeza_w = w * 0.38
    if self.apariencia.get("rostro") == "redondo":
      cabeza_h = h * 0.68
      cabeza_w = w * 0.42
    elif self.apariencia.get("rostro") == "alargado":
      cabeza_h = h * 0.76
      cabeza_w = w * 0.34
    elif self.apariencia.get("rostro") == "cuadrado":
      cabeza_h = h * 0.68
      cabeza_w = w * 0.40
    else:
      cabeza_h = h * 0.72

    cabeza_x = centro_x - cabeza_w / 2
    cabeza_y = y + h * 0.18
    piel = self.PIEL.get(self.apariencia.get("piel"), self.PIEL["media"])
    pelo = self.PELO.get(self.apariencia.get("color_pelo"), self.PELO["castanio"])
    ojos = self.OJOS.get(self.apariencia.get("ojos"), self.OJOS["marrones"])

    with self.canvas:
      # Cuello y torso
      Color(*piel)
      Rectangle(pos=(centro_x - cabeza_w * 0.13, y + h * 0.08), size=(cabeza_w * 0.26, h * 0.20))
      Color(0.10, 0.25, 0.65)
      Ellipse(pos=(centro_x - w * 0.32, y - h * 0.18), size=(w * 0.64, h * 0.42))

      # Rostro
      Color(*piel)
      Ellipse(pos=(cabeza_x, cabeza_y), size=(cabeza_w, cabeza_h))

      # Cabello: los estilos se diferencian con capas geométricas.
      Color(*pelo)
      estilo = self.apariencia.get("peinado", "clasico")
      if estilo == "rapado":
        Ellipse(pos=(cabeza_x + cabeza_w * 0.02, cabeza_y + cabeza_h * 0.78), size=(cabeza_w * 0.96, cabeza_h * 0.22))
      elif estilo == "corto":
        Ellipse(pos=(cabeza_x - cabeza_w * 0.01, cabeza_y + cabeza_h * 0.77), size=(cabeza_w * 1.02, cabeza_h * 0.27))
      elif estilo == "rulos":
        for indice in range(7):
          cx = cabeza_x + cabeza_w * indice / 7
          Ellipse(pos=(cx, cabeza_y + cabeza_h * 0.82), size=(cabeza_w * 0.22, cabeza_h * 0.20))
      elif estilo == "largo":
        Ellipse(pos=(cabeza_x - cabeza_w * 0.05, cabeza_y + cabeza_h * 0.76), size=(cabeza_w * 1.1, cabeza_h * 0.28))
        Rectangle(pos=(cabeza_x - cabeza_w * 0.04, cabeza_y + cabeza_h * 0.30), size=(cabeza_w * 0.16, cabeza_h * 0.48))
        Rectangle(pos=(cabeza_x + cabeza_w * 0.88, cabeza_y + cabeza_h * 0.30), size=(cabeza_w * 0.16, cabeza_h * 0.48))
      elif estilo == "trenzas":
        Ellipse(pos=(cabeza_x, cabeza_y + cabeza_h * 0.78), size=(cabeza_w, cabeza_h * 0.25))
        for indice in range(3):
          Line(points=[cabeza_x + cabeza_w * (0.2 + indice * 0.3), cabeza_y + cabeza_h * 0.90, cabeza_x + cabeza_w * (0.2 + indice * 0.3), cabeza_y + cabeza_h * 0.15], width=2)
      else:
        Ellipse(pos=(cabeza_x - cabeza_w * 0.02, cabeza_y + cabeza_h * 0.76), size=(cabeza_w * 1.04, cabeza_h * 0.29))

      # Ojos y cejas
      Color(0.96, 0.92, 0.82)
      Ellipse(pos=(centro_x - cabeza_w * 0.28, cabeza_y + cabeza_h * 0.52), size=(cabeza_w * 0.20, cabeza_h * 0.07))
      Ellipse(pos=(centro_x + cabeza_w * 0.08, cabeza_y + cabeza_h * 0.52), size=(cabeza_w * 0.20, cabeza_h * 0.07))
      Color(*ojos)
      Ellipse(pos=(centro_x - cabeza_w * 0.22, cabeza_y + cabeza_h * 0.53), size=(cabeza_w * 0.08, cabeza_h * 0.05))
      Ellipse(pos=(centro_x + cabeza_w * 0.14, cabeza_y + cabeza_h * 0.53), size=(cabeza_w * 0.08, cabeza_h * 0.05))
      Color(0.15, 0.08, 0.04)
      Line(points=[centro_x - cabeza_w * 0.30, cabeza_y + cabeza_h * 0.62, centro_x - cabeza_w * 0.08, cabeza_y + cabeza_h * 0.62], width=1.4)
      Line(points=[centro_x + cabeza_w * 0.08, cabeza_y + cabeza_h * 0.62, centro_x + cabeza_w * 0.30, cabeza_y + cabeza_h * 0.62], width=1.4)

      # Boca
      Color(0.35, 0.10, 0.10)
      Line(points=[centro_x - cabeza_w * 0.10, cabeza_y + cabeza_h * 0.29, centro_x, cabeza_y + cabeza_h * 0.27, centro_x + cabeza_w * 0.10, cabeza_y + cabeza_h * 0.29], width=1.4)

      # Tatuajes: marcas visibles sobre cuello/mejilla.
      if self.apariencia.get("tatuajes"):
        Color(0.08, 0.08, 0.08)
        Line(points=[centro_x + cabeza_w * 0.18, cabeza_y + cabeza_h * 0.25, centro_x + cabeza_w * 0.22, cabeza_y + cabeza_h * 0.18, centro_x + cabeza_w * 0.18, cabeza_y + cabeza_h * 0.12], width=1.8)
