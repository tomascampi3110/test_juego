import unittest
from zonas_tabla import zona_tabla


class TestZonasTabla(unittest.TestCase):
  def test_cuatro_primeros_clasifican_a_copa_principal(self):
    for posicion in range(1, 5):
      self.assertEqual(zona_tabla(posicion, 20), "copa_principal")

  def test_puestos_cinco_a_nueve_clasifican_a_copa_secundaria(self):
    for posicion in range(5, 10):
      self.assertEqual(zona_tabla(posicion, 20), "copa_secundaria")

  def test_zona_media_es_neutra(self):
    for posicion in range(10, 19):
      self.assertEqual(zona_tabla(posicion, 20), "normal")

  def test_ultimos_dos_puestos_son_descenso(self):
    self.assertEqual(zona_tabla(19, 20), "descenso")
    self.assertEqual(zona_tabla(20, 20), "descenso")


if __name__ == "__main__":
  unittest.main()
