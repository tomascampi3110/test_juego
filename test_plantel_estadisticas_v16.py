import unittest
from jugador import Jugador
from equipo import Equipo

class TestPlantelEstadisticasV16(unittest.TestCase):
  def test_registra_estadisticas_reales_generales_y_por_competicion(self):
    jugador = Jugador("Prueba", 20, "delantero")
    jugador.registrar_actuacion(7.5, {"goles": 2, "asistencias": 1, "minutos": 90, "competicion": "liga"})
    self.assertEqual(jugador.estadisticas_reales["general"]["partidos"], 1)
    self.assertEqual(jugador.estadisticas_reales["liga"]["goles"], 2)
    self.assertEqual(jugador.estadisticas_reales["temporada"]["asistencias"], 1)

  def test_copas_separadas_de_liga(self):
    jugador = Jugador("Prueba", 20, "mediocampista")
    jugador.registrar_actuacion(7, {"competicion": "Copa Nacional", "goles": 1})
    self.assertEqual(jugador.estadisticas_reales["copas"]["partidos"], 1)
    self.assertEqual(jugador.estadisticas_reales["liga"]["partidos"], 0)

  def test_atributos_relevantes_segun_posicion(self):
    arquero = Jugador("Arq", 20, "arquero")
    relevantes, secundarios = arquero.atributos_relevantes()
    self.assertIn("reaccion", relevantes)
    self.assertNotIn("definicion", relevantes)
    self.assertIn("definicion", secundarios)

if __name__ == "__main__":
  unittest.main()
