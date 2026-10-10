import unittest

from vida_social import SistemaVidaSocial
from jugador import Jugador
from equipo import Equipo


class TestPlantelYGeneroV15(unittest.TestCase):
  def test_evento_presenta_genero_y_nombre_antes_de_invitar(self):
    sistema = SistemaVidaSocial()
    jugador = Jugador("Jugador", 18, "delantero")
    evento = None
    for _ in range(200):
      candidato = sistema.generar_evento(jugador)
      if candidato.identificador == "conocer_persona":
        evento = candidato
        break
    self.assertIsNotNone(evento, "No se generó el evento de conocer a alguien en 200 intentos")
    self.assertTrue(any(palabra in evento.descripcion.lower() for palabra in ("chico", "chica")))
    self.assertTrue(any(nombre in evento.descripcion for nombre in (
      "Sofía", "Valentina", "Camila", "Martina", "Lucía", "Julieta", "Micaela", "Florencia", "Agustina", "Milagros", "Renata", "Abril",
      "Mateo", "Julián", "Thiago", "Benjamín", "Nicolás", "Franco", "Bruno", "Agustín", "Santiago", "Tomás", "Lautaro", "Facundo"
    )))

  def test_plantel_equipo_guarda_jugadores(self):
    equipo = Equipo("Club Prueba", "Estadio", "DT", None)
    jugador = Jugador("Jugador Prueba", 20, "mediocampista")
    equipo.agregar_jugador(jugador)
    self.assertIn(jugador, equipo.jugadores)
    self.assertEqual(jugador.equipo, equipo)


if __name__ == "__main__":
  unittest.main()
