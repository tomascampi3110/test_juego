# Football Game — base integrada de carrera

Esta carpeta contiene una versión de trabajo que integra los sistemas acordados para la carrera de un futbolista. Está separada en módulos para poder probar y ampliar cada parte sin concentrar toda la lógica en `main.py`.

## Ejecutar

Requisitos para la interfaz:

```bash
python -m pip install -r requirements.txt
python main.py
```

Para ejecutar únicamente las pruebas del backend (no necesitan Kivy):

```bash
python -m unittest discover -s tests -v
```

## Cambios de esta revisión

- La edad inicial del jugador controlado está fijada en 18 años. El jugador controlado no tiene potencial oculto ni desarrollo automático: mejora sus atributos gastando puntos de mejora. El potencial se usa únicamente para la progresión de los NPC.
- El botón **CONTINUAR CARRERA** simula exactamente una semana por clic. No hay avance automático ni simulación en cadena.
- El jugador empieza con $50.000 de dinero virtual.
- El perfil del jugador queda visible en la pantalla principal con avatar, club, valoración, forma, dinero, salario y puntos de mejora. Los botones Guardar y Menú principal están juntos en la cabecera.
- Las pestañas separan Perfil, Fútbol, Club, Relaciones, Economía, Inversiones y Patrocinadores. Situación contractual, mercado de pases, vínculos, logros y charla con el presidente están agrupados en Relaciones.
- Los patrocinadores activos y las ofertas disponibles se muestran directamente en su pestaña; se puede contratar una oferta con un solo clic, sin abrir ventanas intermedias.
- Al terminar una semana, todas las novedades se reúnen en un único resumen desplazable. Cerrarlo pausa la carrera: no avanza otra semana ni encadena popups.

## Sistemas incluidos

- **Carrera y temporada:** liga de 20 equipos, 38 jornadas y 380 partidos; cada equipo juega una vez por semana en la liga.
- **Puntaje de partido:** nota de 1 a 10 basada en goles, asistencias, duelos y amonestaciones. El futbolista controlado recibe una actuación registrada en el partido de su club.
- **Forma y edad:** la forma afecta ligeramente las estadísticas efectivas y existe degradación física progresiva a partir de los 30 años. El potencial y el desarrollo automático se reservan para los NPC.
- **Equipamiento temporal:** botines y canilleras con 50 partidos de durabilidad (para cubrir una temporada de liga y parte de las copas); las canilleras reducen el riesgo de lesión.
- **Personalización visual:** peinado, pelo, ojos, forma de rostro, piel y tatuajes. `avatar.py` dibuja una representación sencilla en Kivy que se actualiza al cambiar la apariencia.
- **Mejoras permanentes:** bonificadores para ingresos de inversiones, sponsors, entrenamiento y espacios adicionales de patrocinio; la tienda muestra el efecto de cada compra.
- **Sponsors:** ofertas periódicas, contratos con duración, límites de espacios y exclusión de sponsors de la misma categoría comercial.
- **Negociación contractual:** un minijuego de posición de mano, flexibilidad influida por rendimiento, relaciones, antigüedad e intentos fallidos.
- **Mercado:** solicitud de lista de transferibles y ofertas durante las ventanas de mercado.
- **Casino:** juegos con dinero virtual y límites de apuesta.
- **Logros:** recompensas únicas en dinero y XP.
- **Vida social:** vínculos con hinchada, club, entrenador, gerente, compañeros y pareja; eventos con varias decisiones. La bandeja mantiene como máximo una notificación social pendiente y bloquea el avance hasta resolverla o dejarla abierta.
- **Retiro:** edad de retiro configurable y extensión de carrera mediante pago.
- **Guardado/carga:** guarda el estado completo de la carrera en `partida.career`.

## Importante sobre guardados

El prototipo usa `pickle` para preservar las referencias entre jugadores, clubes, partidos y temporada. Cargá únicamente partidas que haya generado este juego y que sean de confianza; no abras archivos de guardado descargados de terceros.

## Estado del proyecto

La lógica de backend y la sintaxis de los módulos se probaron en este entorno. La interfaz Kivy está incluida, pero no se pudo ejecutar gráficamente aquí porque este entorno no tiene Kivy instalado. La interfaz debe probarse en la computadora donde está instalado Kivy.

La personalización usa un avatar geométrico provisional; no es todavía un modelo 3D ni un conjunto de sprites detallados. Las marcas comerciales de las ofertas son nombres genéricos para evitar depender de licencias.

## Economía e inversiones

- **Inversiones:** pestaña propia en Economía con negocios, propiedades en alquiler y fondos de inversión; cada compra genera ingresos semanales y las inversiones pueden mejorarse.
- **Mejoras permanentes por niveles:** los bonificadores de inversiones, sponsors y puntos de mejora aumentan un 5% por nivel, hasta 10 niveles. El precio sube en cada nivel; el espacio adicional de sponsor sigue siendo una compra única.

### Interfaz de carrera (v6)
- La navegación separa Inversiones y Patrocinadores en pestañas propias; Economía queda para equipamiento, mejoras permanentes y casino.
- La tabla de posiciones resalta el equipo del jugador con un tono dorado y muestra zonas visuales para copa principal (puestos 1–4), copa secundaria (5–9) y descenso (últimos dos puestos). Estas posiciones son una convención visual provisional hasta terminar de definir las competiciones y sus cupos.


## Flujo de carrera y novedades (v9)

Se eliminó el avance automático día por día. **CONTINUAR CARRERA** simula una semana por clic. Al finalizar, aparece una única ventana desplazable que agrupa el resultado del partido, el rendimiento del jugador, el próximo rival, la economía semanal y las notificaciones relevantes. Al cerrarla, la simulación queda pausada y el usuario puede navegar por todas las pestañas. Los eventos sociales no provocan avance automático.

La pestaña **Patrocinadores** muestra simultáneamente los contratos activos y las ofertas disponibles. La pestaña **Relaciones** reúne charla con el presidente, situación contractual, mercado de pases, vínculos, logros y eventos sociales. El perfil principal está visible en la parte superior de la pantalla, y el acceso al menú principal está al lado de Guardar.

## Vida personal, inversiones y casino (revisión de sistemas)

- **Relaciones:** pareja con nombre y género, estado sentimental, posibilidad de ruptura si el vínculo cae mucho, matrimonio tras una relación estable y posibilidad de tener hijos. Los hitos son eventos poco frecuentes y se muestran como notificaciones.
- **Presidente:** saludo contextual según el rendimiento y la relación con la dirigencia, con accesos a contrato, mercado y futuro en el club.
- **Inversiones escalonadas:** cada oportunidad muestra los requisitos de valoración y patrimonio. Los negocios iniciales son accesibles temprano; una fábrica requiere valoración 80, patrimonio mínimo de $200.000 y capital de compra.
- **Casino:** ruleta, tragamonedas, carreras de caballos y apuestas deportivas con dinero virtual. Los resultados se registran en un historial y las apuestas validan saldo y límites.
- **Progresión visible:** la pantalla de atributos muestra los puntos disponibles y permite gastar un punto para subir un atributo en una unidad; la valoración se recalcula automáticamente. El jugador controlado no recibe desarrollo automático gratuito.
- **Edad:** los NPC tienen progresión limitada por edad y potencial. A partir de los 30 años comienza un declive principalmente físico, que se acelera a partir de los 33 y 36; la técnica puede mantenerse mejor por experiencia. El jugador controlado no sufre cambios automáticos de atributos, aunque su forma puede variar.

## Versión 13: progresión y comienzo como agente libre

- El jugador comienza sin club ni contrato y recibe ofertas iniciales de equipos cercanos a su valoración.
- Las ofertas se pueden aceptar o rechazar desde Situación contractual; al aceptar, el jugador se incorpora al club y firma por 52 semanas.
- Se reciben puntos de mejora cada semana; la cantidad varía según nota, nivel del equipo y situación contractual.
- Mejorar un atributo cuesta XP en función de su valor actual: valor actual + 5 para el siguiente punto (por ejemplo, 10 cuesta 15 XP).
- Cada tipo de inversión se puede adquirir una sola vez y luego mejorar hasta nivel 5.
- Las conversaciones con el presidente tienen un período de espera de cuatro semanas.
- La suite incluye pruebas de XP semanal, costo progresivo de atributos, ofertas contractuales e inversiones únicas.


## Versión 16: planteles y estadísticas
- Las ofertas contractuales muestran el tamaño del plantel y la cantidad de arqueros, e incluyen acceso directo para consultar todos los jugadores antes de firmar.
- Se agregó una vista de plantel con selector de estadísticas generales, temporada, liga y copas; muestra partidos, titularidades, suplencias, goles, asistencias, tarjetas, atajadas y vallas invictas.
- Se separaron estadísticas deportivas reales de los atributos que se mejoran con XP.
- Se quitó la posición de arquero de la selección inicial del jugador hasta que exista una mecánica de atajadas/penales interactiva. Los NPC siguen pudiendo ser arqueros.
