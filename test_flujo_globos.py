import ast
import unittest
from pathlib import Path


class TestFlujoGlobos(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    ruta = Path(__file__).resolve().parents[1] / "main.py"
    cls.arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    cls.metodos = {}
    for nodo in ast.walk(cls.arbol):
      if isinstance(nodo, ast.ClassDef) and nodo.name == "PantallaCarrera":
        cls.metodos = {
          metodo.name: metodo
          for metodo in nodo.body
          if isinstance(metodo, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        break

  def nombres_llamados(self, nombre_metodo):
    metodo = self.metodos[nombre_metodo]
    return {
      nodo.func.attr if isinstance(nodo.func, ast.Attribute)
      else nodo.func.id if isinstance(nodo.func, ast.Name)
      else ""
      for nodo in ast.walk(metodo)
      if isinstance(nodo, ast.Call)
    }

  def test_cerrar_resumen_no_avanza_otra_semana(self):
    llamadas = self.nombres_llamados("cerrar_resumen")
    self.assertNotIn("continuar_carrera", llamadas)

  def test_resumen_semanal_es_un_solo_popup(self):
    llamadas = self.nombres_llamados("mostrar_resumen_unico")
    self.assertEqual(sum(1 for nodo in ast.walk(self.metodos["mostrar_resumen_unico"])
                         if isinstance(nodo, ast.Call)
                         and isinstance(nodo.func, ast.Name)
                         and nodo.func.id == "Popup"), 1)
    self.assertNotIn("mostrar_siguiente_globo", llamadas)

  def test_resolver_evento_social_no_simula_otra_semana(self):
    llamadas = self.nombres_llamados("elegir_evento")
    self.assertNotIn("continuar_carrera", llamadas)

  def test_patrocinadores_se_abren_en_vista_directa(self):
    self.assertIn("abrir_sponsors", self.metodos)
    llamadas = self.nombres_llamados("abrir_sponsors")
    self.assertIn("ScrollView", llamadas)
    self.assertIn("GridLayout", llamadas)
    self.assertIn("refrescar_sponsors", llamadas)


if __name__ == "__main__":
  unittest.main()
