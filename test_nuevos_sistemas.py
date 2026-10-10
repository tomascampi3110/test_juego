import unittest
from carrera import Carrera
from jugador import Jugador
from vida_social import SistemaVidaSocial
from economia import Inversion
from casino import Casino


class TestNuevosSistemas(unittest.TestCase):
  def test_inversiones_bloqueadas_por_valoracion_y_patrimonio(self):
    carrera = Carrera.nueva("Jugador")
    jugador = carrera.jugador
    jugador.dinero = 500000
    jugador.valoracion = 50
    resultado = carrera.comprar_inversion("fabrica")
    self.assertFalse(resultado["ok"])
    self.assertIn("valoración 80", resultado["mensaje"])

  def test_fabrica_se_compra_con_requisitos(self):
    carrera = Carrera.nueva("Jugador")
    jugador = carrera.jugador
    jugador.dinero = 300000
    jugador.valoracion = 85
    resultado = carrera.comprar_inversion("fabrica")
    self.assertTrue(resultado["ok"])
    self.assertEqual(jugador.inversiones[-1].nombre, "Fábrica propia")

  def test_ruleta_valida_y_registra_apuesta(self):
    jugador = Jugador("Jugador", 18, "delantero")
    jugador.dinero = 1000
    casino = Casino()
    resultado = casino.jugar_ruleta(jugador, 100, "rojo")
    self.assertTrue(resultado["ok"])
    self.assertEqual(len(casino.historial), 1)
    self.assertGreaterEqual(jugador.dinero, 800)
    self.assertLessEqual(jugador.dinero, 1100)

  def test_tragamonedas_y_caballos_validan_apuesta(self):
    jugador = Jugador("Jugador", 18, "delantero")
    jugador.dinero = 1000
    casino = Casino()
    self.assertTrue(casino.jugar_tragamonedas(jugador, 100)["ok"])
    self.assertTrue(casino.jugar_carrera_caballos(jugador, 100, "Relámpago")["ok"])
    self.assertFalse(casino.jugar_carrera_caballos(jugador, 100, "Pegaso")["ok"])

  def test_pareja_guarda_genero_y_estado(self):
    jugador = Jugador("Jugador", 18, "delantero")
    sistema = SistemaVidaSocial()
    self.assertTrue(sistema.crear_pareja(jugador, "Sofía", "mujer"))
    self.assertEqual(jugador.pareja_genero, "mujer")
    self.assertEqual(jugador.estado_relacion, "en pareja")
    self.assertFalse(sistema.crear_pareja(jugador, "Mateo", "hombre"))

  def test_saludo_presidente_contextual(self):
    jugador = Jugador("Jugador", 18, "delantero")
    saludo = SistemaVidaSocial().hablar_con_presidente(jugador)
    self.assertIn("¿Qué tal?", saludo["saludo"])
    self.assertIn("Hablar del contrato", saludo["opciones"])

  def test_jugador_usuario_no_mejora_atributos_solo(self):
    carrera = Carrera.nueva("Jugador")
    jugador = carrera.jugador
    antes = dict(jugador.estadisticas)
    for _ in range(52):
      jugador.procesar_semana()
    self.assertEqual(jugador.estadisticas, antes)


if __name__ == "__main__":
  unittest.main()
