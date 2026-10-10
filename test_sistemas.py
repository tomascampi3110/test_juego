import tempfile
import unittest
from pathlib import Path

from carrera import Carrera
from jugador import Jugador
from equipo import Equipo
from partido import Partido
from economia import Sponsor
from equipamiento import Equipamiento
from guardado import GestorGuardado
from negociacion import NegociacionContrato
from personalizacion import agregar_tatuaje


class TestSistemasCarrera(unittest.TestCase):
  def test_calendario_liga_20_equipos(self):
    carrera = Carrera.nueva("Tomás", 20, "delantero")
    self.assertEqual(len(carrera.liga.partidos), 380)
    self.assertEqual(carrera.temporada.duracion, 38)

    for semana in range(1, 39):
      partidos = carrera.temporada.obtener_partidos_semana(semana)
      self.assertEqual(len(partidos), 10)
      equipos = []
      for partido in partidos:
        equipos.extend([partido.local, partido.visitante])
      self.assertEqual(len(set(equipos)), 20)

  def test_tabla_se_actualiza_despues_de_simular_jornada(self):
    carrera = Carrera.nueva("Tomás", 18, "delantero")
    partidos = carrera.temporada.obtener_partidos_semana(1)
    self.assertEqual(len(partidos), 10)

    for partido in partidos:
      partido.simular()

    tabla = carrera.liga.tabla()
    self.assertEqual(len(tabla), 20)
    self.assertEqual(sum(equipo.pj for equipo in tabla), 20)
    self.assertEqual(sum(equipo.gf for equipo in tabla), sum(equipo.gc for equipo in tabla))
    self.assertEqual(sum(equipo.pts for equipo in tabla), sum(
      3 if partido.resultado[0] != partido.resultado[1] else 2
      for partido in partidos
    ))

  def test_sponsors_excluyen_categoria_repetida(self):
    jugador = Jugador("Jugador", 22, "delantero")
    jugador.valoracion = 80
    jugador.nivel_lujo = 5

    adidas = Sponsor(
      "Marca A",
      "deluxe",
      1000,
      20,
      categoria_comercial="indumentaria"
    )
    under_armour = Sponsor(
      "Marca B",
      "deportivo",
      800,
      20,
      categoria_comercial="indumentaria"
    )
    bebidas = Sponsor(
      "Bebidas",
      "local",
      500,
      20,
      categoria_comercial="bebidas"
    )

    self.assertTrue(jugador.agregar_sponsor(adidas))
    self.assertFalse(jugador.agregar_sponsor(under_armour))
    self.assertTrue(jugador.agregar_sponsor(bebidas))

  def test_puntaje_partido_y_logros(self):
    local = Equipo("Local", "Estadio", "DT", None)
    visitante = Equipo("Visitante", "Estadio", "DT", None)
    jugador = Jugador("Goleador", 21, "delantero")
    otro = Jugador("Rival", 22, "defensor")
    local.agregar_jugador(jugador)
    visitante.agregar_jugador(otro)

    botines = Equipamiento(
      "Botines test",
      "botines",
      100,
      {"precision": 3},
      durabilidad_partidos=2
    )
    jugador.equipamiento["botines"] = botines

    partido = Partido(local, visitante, "Estadio")
    partido.iniciar()
    partido.agregar_gol(jugador, local)
    partido.agregar_gol(jugador, local)
    partido.agregar_gol(jugador, local)
    partido.finalizar()

    self.assertEqual(jugador.partidos_jugados, 1)
    self.assertEqual(jugador.historial_notas[-1], 10.0)
    self.assertIn("hat_trick", jugador.logros)
    self.assertEqual(botines.durabilidad, 1)

  def test_bonificacion_temporal_equipo(self):
    jugador = Jugador("Jugador", 22, "mediocampista")
    equipo = Equipamiento(
      "Botines",
      "botines",
      100,
      {"velocidad": 4},
      durabilidad_partidos=1
    )
    jugador.equipamiento["botines"] = equipo
    self.assertEqual(jugador.obtener_estadistica("velocidad"), 54)
    equipo.desgastar()
    jugador.equipamiento.pop("botines")
    self.assertEqual(jugador.obtener_estadistica("velocidad"), 50)

  def test_tatuaje_cuesta_dinero_y_actualiza_apariencia(self):
    jugador = Jugador("Jugador", 22, "delantero")
    jugador.dinero = 50000
    self.assertTrue(agregar_tatuaje(jugador, "Tatuaje test", 25000))
    self.assertEqual(jugador.dinero, 25000)
    self.assertIn("Tatuaje test", jugador.apariencia["tatuajes"])
    self.assertEqual(jugador.nivel_lujo, 1)

  def test_negociacion_firma_contrato(self):
    carrera = Carrera.nueva("Jugador", 22, "delantero")
    jugador = carrera.jugador
    jugador.semanas_desde_ultimo_contrato = 12
    negociacion = NegociacionContrato(
      jugador,
      jugador.equipo,
      5000,
      52
    )
    resultado = negociacion.intentar_acuerdo(50)
    self.assertTrue(resultado["ok"])
    self.assertGreaterEqual(resultado["salario_semanal"], 5000)
    self.assertTrue(jugador.contrato.esta_vigente())

  def test_casino_valida_apuestas(self):
    carrera = Carrera.nueva("Jugador", 22, "delantero")
    jugador = carrera.jugador
    jugador.dinero = 1000
    resultado = carrera.casino.jugar_moneda(jugador, 100, "cara")
    self.assertTrue(resultado["ok"])
    self.assertGreaterEqual(jugador.dinero, 900)
    invalida = carrera.casino.jugar_moneda(jugador, 100000, "cara")
    self.assertFalse(invalida["ok"])

  def test_guardado_preserva_referencias(self):
    carrera = Carrera.nueva("Jugador", 22, "delantero")
    with tempfile.TemporaryDirectory() as carpeta:
      ruta = GestorGuardado.guardar(
        {"carrera": carrera},
        Path(carpeta) / "test"
      )
      cargado = GestorGuardado.cargar(ruta)["carrera"]
      self.assertEqual(cargado.jugador.nombre, "Jugador")
      self.assertIs(cargado.temporada.jugador_usuario, cargado.jugador)
      self.assertIsNone(cargado.jugador.equipo)
      self.assertGreaterEqual(len(cargado.ofertas_contractuales), 1)
      self.assertEqual(len(cargado.liga.partidos), 380)

  def test_procesamiento_semanal_envejece_cada_52_semanas(self):
    jugador = Jugador("Jugador", 20, "delantero")
    for _ in range(52):
      jugador.procesar_semana()
    self.assertEqual(jugador.edad, 21)

  def test_simular_semana_juega_liga_y_califica_al_usuario(self):
    carrera = Carrera.nueva("Titular", 21, "mediocampista")
    resultado = carrera.jugar_siguiente_semana()
    self.assertEqual(resultado["partidos"], 10)
    self.assertIsNone(carrera.jugador.equipo)
    self.assertEqual(carrera.jugador.partidos_jugados, 0)
    self.assertGreater(carrera.jugador.puntos_mejora, 0)
    self.assertEqual(carrera.temporada.semana, 2)

  def test_bolsa_equipamiento_tiene_stock_y_descuento(self):
    carrera = Carrera.nueva("Comprador", 22, "defensor")
    jugador = carrera.jugador
    jugador.dinero = 100000
    bolsa = carrera.temporada.bolsa_equipamiento
    self.assertTrue(bolsa.ofertas)
    resultado = bolsa.comprar(jugador, 0)
    self.assertTrue(resultado["ok"])
    self.assertEqual(bolsa.ofertas[0]["stock"], 0)

  def test_mejora_permanente_bonifica_inversiones(self):
    from economia import Inversion
    from mejoras import MejoraCarrera

    jugador = Jugador("Inversor", 23, "mediocampista")
    jugador.dinero = 100000
    inversion = Inversion("Negocio", "negocio", 1000, 100)
    jugador.agregar_inversion(inversion)
    self.assertTrue(MejoraCarrera.comprar(jugador, "inversiones_plus"))
    dinero_antes = jugador.dinero
    ingreso = inversion.generar_ingreso(jugador)
    self.assertEqual(ingreso, 105)
    self.assertEqual(jugador.dinero, dinero_antes + 105)
    self.assertTrue(MejoraCarrera.comprar(jugador, "inversiones_plus"))
    self.assertEqual(jugador.bonificadores["inversiones"], 1.10)


  def test_compra_inversion_cobra_costo_y_genera_ingresos(self):
    carrera = Carrera.nueva("Inversor", posicion="mediocampista")
    carrera.jugador.dinero = 30000
    dinero_antes = carrera.jugador.dinero

    resultado = carrera.comprar_inversion("negocio")

    self.assertTrue(resultado["ok"])
    self.assertEqual(len(carrera.jugador.inversiones), 1)
    self.assertEqual(carrera.jugador.dinero, dinero_antes - 10000)
    self.assertEqual(carrera.jugador.inversiones[0].ingreso_semanal, 450)

  def test_mejoras_permanentes_suben_de_cinco_en_cinco(self):
    from mejoras import MejoraCarrera

    jugador = Jugador("Mejoras", 18, "delantero")
    jugador.dinero = 200000

    self.assertTrue(MejoraCarrera.comprar(jugador, "sponsors_plus"))
    self.assertAlmostEqual(jugador.bonificadores["sponsors"], 1.05)
    self.assertTrue(MejoraCarrera.comprar(jugador, "sponsors_plus"))
    self.assertAlmostEqual(jugador.bonificadores["sponsors"], 1.10)
    self.assertEqual(MejoraCarrera.nivel(jugador, "sponsors_plus"), 2)

  def test_pareja_se_crea_con_evento_social(self):
    from vida_social import OpcionSocial

    jugador = Jugador("Social", 22, "delantero")
    opcion = OpcionSocial("Invitar a salir", 0, {"pareja_nueva": 1})
    resultado = opcion.ejecutar(jugador)
    self.assertTrue(resultado["ok"])
    self.assertIsNotNone(jugador.pareja)
    self.assertEqual(jugador.vinculos["pareja"], 50)

  def test_transferencia_del_usuario_actualiza_club_y_contrato(self):
    carrera = Carrera.nueva("Transferible", 22, "delantero")
    jugador = carrera.jugador
    jugador.en_lista_transferibles = True
    comprador = carrera.liga.equipos[0]
    comprador.presupuesto = 1000000
    jugador.equipo = carrera.liga.equipos[-1]
    jugador.equipo.agregar_jugador(jugador)
    oferta = carrera.temporada.mercado_pases.hacer_oferta(
      jugador, comprador, monto=100000, salario_semanal=6000, duracion_semanas=52
    )

    self.assertIsNotNone(oferta)
    self.assertTrue(oferta.aceptar())
    self.assertIs(jugador.equipo, comprador)
    self.assertIs(jugador.contrato.club, comprador)
    self.assertFalse(jugador.en_lista_transferibles)


  def test_carrera_usuario_empieza_a_los_18_con_dinero_inicial(self):
    carrera = Carrera.nueva("Promesa", 31, "delantero")
    self.assertEqual(carrera.jugador.edad, 18)
    self.assertEqual(carrera.jugador.dinero, 50000)
    self.assertIsNone(carrera.jugador.potencial)
    self.assertFalse(carrera.jugador.desarrollar())

  def test_potencial_disminuye_con_edad_de_inicio(self):
    joven = Carrera.potencial_inicial_segun_edad(18, 50)
    veterano = Carrera.potencial_inicial_segun_edad(32, 50)
    self.assertGreaterEqual(joven, 84)
    self.assertLessEqual(veterano, 72)

  def test_solicitar_lista_transferibles_devuelve_resultado_mostrable(self):
    carrera = Carrera.nueva("Transferible", 18, "delantero")
    resultado = carrera.solicitar_lista_transferibles()
    self.assertIsInstance(resultado, dict)
    self.assertIn("ok", resultado)
    self.assertIn("mensaje", resultado)

  def test_valor_mercado_usuario_no_depende_de_potencial(self):
    carrera = Carrera.nueva("SinPotencial", 18, "delantero")
    valor = carrera.temporada.mercado_pases.calcular_valor_jugador(carrera.jugador)
    self.assertGreater(valor, 0)

  def test_puntos_mejora_son_la_progresion_del_usuario(self):
    jugador = Carrera.nueva("Mejoras", 18, "delantero").jugador
    jugador.puntos_mejora = 200
    antes = jugador.estadisticas["definicion"]
    jugador.mejorar_estadistica("definicion", 3)
    self.assertEqual(jugador.estadisticas["definicion"], antes + 3)
    self.assertLess(jugador.puntos_mejora, 200)
    self.assertEqual(jugador.puntos_mejora, 200 - jugador.historial_mejoras_atributos[-1]["costo"])

  def test_evento_social_bloquea_avance_y_no_se_acumula(self):
    from vida_social import EventoSocial, OpcionSocial

    carrera = Carrera.nueva("Social", 25, "mediocampista")
    temporada = carrera.temporada
    evento = EventoSocial(
      "test",
      "Invitación de prueba",
      "Evento para comprobar la bandeja",
      [OpcionSocial("Aceptar", 0, {"bienestar": 1})]
    )
    temporada.eventos_sociales_pendientes.append({
      "semana": temporada.semana,
      "evento": evento
    })

    semana_original = temporada.semana
    resultado = carrera.jugar_siguiente_semana()
    self.assertTrue(resultado["requiere_evento"])
    self.assertEqual(temporada.semana, semana_original)
    self.assertEqual(len(temporada.eventos_sociales_pendientes), 1)

    resuelto = carrera.resolver_evento_social(evento, 0)
    self.assertTrue(resuelto["ok"])
    self.assertEqual(temporada.eventos_sociales_pendientes, [])

  def test_equipamiento_dura_al_menos_una_temporada(self):
    from tienda import TiendaEquipamiento
    for item in TiendaEquipamiento.CATALOGO:
      self.assertGreaterEqual(item["durabilidad"], 38)



if __name__ == "__main__":
  unittest.main()
