class SistemaRetiro:
  EDAD_RETIRO_NORMAL = 38

  def __init__(self):
    self.historial = []

  def debe_retirarse(self, jugador):
    return jugador.edad >= getattr(
      jugador,
      "edad_retiro",
      self.EDAD_RETIRO_NORMAL
    ) and not getattr(jugador, "retiro_forzado", False)

  def costo_extension(self, jugador):
    exceso = max(0, jugador.edad - 35)
    base = max(25000, jugador.valoracion * 1500)
    return round(base * (1 + exceso * 0.75))

  def extender_carrera(self, jugador):
    if jugador.edad < jugador.edad_retiro:
      return {
        "ok": False,
        "mensaje": f"Podés extender tu carrera cuando alcances los {jugador.edad_retiro} años."
      }

    if jugador.retiro_forzado:
      return {"ok": False, "mensaje": "La carrera ya terminó."}

    costo = self.costo_extension(jugador)
    if jugador.dinero < costo:
      return {
        "ok": False,
        "mensaje": f"Necesitás ${costo} para extender tu carrera.",
        "costo": costo
      }

    jugador.dinero -= costo
    jugador.edad_retiro = getattr(
      jugador,
      "edad_retiro",
      self.EDAD_RETIRO_NORMAL
    ) + 1
    self.historial.append({
      "jugador": jugador.nombre,
      "edad": jugador.edad,
      "costo": costo
    })

    return {
      "ok": True,
      "mensaje": "Extendiste tu carrera una temporada más.",
      "costo": costo
    }

  def finalizar_carrera(self, jugador):
    jugador.retiro_forzado = True
    return True
