FOOTBALL CAREER - BUILD ANDROID

IMPORTANTE
Este ZIP contiene el proyecto configurado para generar un APK Android, pero el APK binario no se ha compilado en este entorno. La compilación de Kivy necesita descargar Android SDK/NDK y toolchains; Buildozer está pensado para Linux/macOS o Windows mediante WSL.

OPCIÓN RECOMENDADA: GENERAR APK CON GITHUB ACTIONS
1. Descomprimí el ZIP.
2. Creá un repositorio en GitHub y subí el contenido de esta carpeta.
3. Abrí la pestaña Actions y ejecutá "Build Android APK" (Run workflow).
4. Cuando termine correctamente, entrá en el run y descargá el artefacto "football-career-debug-apk".
5. Descomprimí el artefacto en el teléfono y abrí el APK. Android puede pedir habilitar la instalación desde esa fuente.

OPCIÓN LOCAL EN WINDOWS
1. Instalá WSL2 y Ubuntu.
2. Copiá la carpeta del proyecto al filesystem de Ubuntu, no la compiles desde /mnt/c.
3. Instalá dependencias según la documentación oficial de Buildozer: https://buildozer.readthedocs.io/
4. Dentro de la carpeta del proyecto, ejecutá: buildozer -v android debug
5. El APK aparecerá en bin/.

CONTENIDO DE PRUEBA
- Liga argentina de 20 clubes reales para conservar el calendario de 38 jornadas del prototipo.
- Catálogo de copas y ligas reales para ampliar el universo más adelante.
- Retrato de futbolista generado para la pantalla inicial.
- Escudos estilizados originales con siglas y colores inspirados en los clubes; no son logos oficiales.
- Trofeo ilustrado original.

Las competiciones que aparecen en el catálogo son referencias; no todas están implementadas como torneos jugables en esta build. Los planteles y resultados siguen siendo generados por el simulador.
