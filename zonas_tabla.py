def zona_tabla(posicion, cantidad_equipos):
  """Devuelve la zona visual de una posición en una liga.

  Convención provisional: puestos 1-4 copa principal, 5-9 copa secundaria,
  últimos dos puestos descenso. Se puede ajustar cuando se definan las copas.
  """
  if posicion <= 4:
    return "copa_principal"
  if posicion <= 9:
    return "copa_secundaria"
  if posicion > cantidad_equipos - 2:
    return "descenso"
  return "normal"
