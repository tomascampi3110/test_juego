import pickle
from pathlib import Path


class GestorGuardado:
  EXTENSION = ".career"

  @classmethod
  def guardar(cls, estado, ruta):
    ruta = Path(ruta)
    if ruta.suffix != cls.EXTENSION:
      ruta = ruta.with_suffix(cls.EXTENSION)

    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")

    with temporal.open("wb") as archivo:
      pickle.dump(estado, archivo, protocol=pickle.HIGHEST_PROTOCOL)

    temporal.replace(ruta)
    return ruta

  @classmethod
  def cargar(cls, ruta):
    """Cargar solo archivos de carrera creados por este juego y de confianza."""
    ruta = Path(ruta)
    with ruta.open("rb") as archivo:
      return pickle.load(archivo)
