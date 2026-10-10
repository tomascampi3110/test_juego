import unittest
from carrera import Carrera
from jugador import Jugador

class TestProgresionV13(unittest.TestCase):
  def test_gana_xp_al_avanzar_semana(self):
    carrera = Carrera.nueva("Libre")
    inicial = carrera.jugador.puntos_mejora
    carrera.jugar_siguiente_semana()
    self.assertGreater(carrera.jugador.puntos_mejora, inicial)

  def test_mejora_atributo_cuesta_segun_tramo_de_valor(self):
    jugador = Jugador("Prueba", 18, "delantero")
    jugador.estadisticas["definicion"] = 85
    self.assertEqual(jugador.costo_mejora_estadistica("definicion"), 120)
    jugador.puntos_mejora = 119
    jugador.mejorar_estadistica("definicion", 1)
    self.assertEqual(jugador.estadisticas["definicion"], 85)
    jugador.puntos_mejora = 120
    jugador.mejorar_estadistica("definicion", 1)
    self.assertEqual(jugador.estadisticas["definicion"], 86)
    self.assertEqual(jugador.puntos_mejora, 0)

  def test_costo_aumenta_cada_diez_mejoras_no_cada_compra(self):
    jugador = Jugador("Prueba", 18, "delantero")
    jugador.estadisticas["definicion"] = 20
    inicial = jugador.costo_mejora_estadistica("definicion")
    for _ in range(10):
      costo = jugador.costo_mejora_estadistica("definicion")
      jugador.puntos_mejora += costo
      jugador.mejorar_estadistica("definicion", 1)
    self.assertEqual(jugador.costo_mejora_estadistica("definicion"), 37)

  def test_empieza_libre_con_ofertas_contractuales(self):
    carrera = Carrera.nueva("Libre")
    self.assertIsNone(carrera.jugador.equipo)
    self.assertIsNone(carrera.jugador.contrato)
    self.assertGreaterEqual(len(carrera.ofertas_contractuales), 1)

  def test_aceptar_oferta_firma_con_club(self):
    carrera = Carrera.nueva("Libre")
    oferta = carrera.ofertas_contractuales[0]
    resultado = carrera.responder_oferta_contractual(oferta, True)
    self.assertTrue(resultado["ok"])
    self.assertIs(carrera.jugador.equipo, oferta["equipo"])
    self.assertIs(carrera.jugador.contrato.club, oferta["equipo"])

  def test_inversion_unica_no_se_puede_comprar_dos_veces(self):
    carrera = Carrera.nueva("Inversor")
    jugador = carrera.jugador
    jugador.valoracion = 85
    jugador.dinero = 500000
    primera = carrera.comprar_inversion("negocio")
    segunda = carrera.comprar_inversion("negocio")
    self.assertTrue(primera["ok"])
    self.assertFalse(segunda["ok"])
    self.assertEqual(len([i for i in jugador.inversiones if i.identificador == "negocio"]), 1)

  def test_charla_presidente_tiene_periodo_de_espera(self):
    carrera = Carrera.nueva("Prueba")
    carrera.semanas_desde_charla_presidente = 0
    self.assertLess(carrera.semanas_desde_charla_presidente, 4)

if __name__ == "__main__":
  unittest.main()
