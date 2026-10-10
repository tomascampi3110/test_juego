import os
import unittest
from clubes_reales import CLUBES_ARGENTINA, COMPETICIONES_REALES
from carrera import Carrera

class TestPackMovil(unittest.TestCase):
  def test_catalogo_tiene_20_clubes_reales_y_sin_repetidos(self):
    nombres = [club["nombre"] for club in CLUBES_ARGENTINA]
    self.assertEqual(len(nombres), 20)
    self.assertEqual(len(set(nombres)), 20)

  def test_carrera_usa_clubes_reales_y_escudos(self):
    carrera = Carrera.nueva("Prueba")
    self.assertEqual(len(carrera.liga.equipos), 20)
    for equipo in carrera.liga.equipos:
      self.assertTrue(equipo.estadio)
      self.assertTrue(os.path.exists(equipo.ruta_escudo))

  def test_catalogo_incluye_copas_reales(self):
    nombres = {item["nombre"] for item in COMPETICIONES_REALES}
    self.assertIn("Copa Libertadores", nombres)
    self.assertIn("Copa Sudamericana", nombres)
    self.assertIn("UEFA Champions League", nombres)

  def test_retrato_y_icono_movil(self):
    self.assertTrue(os.path.exists("assets/jugador_portada.jpg"))
    self.assertTrue(os.path.exists("assets/icon.png"))
