# Laboratorio de la S4

`laboratorio_S4.html` tiene los 5 retos de la S4 (SOLID) con el mismo código y las mismas pruebas del repo, y los corre en el navegador: no necesita Node, ni instalar nada, ni internet.

- **Usarlo:** descarga el archivo y ábrelo con doble clic en Edge, o entra a la [versión en línea](https://coach1-knotacademy.github.io/knot-qa-framework/laboratorio-s4.html).
- **Qué hace:** editor con números de línea, botón «Correr pruebas» con la salida de Playwright (✓/✘, Expected/Received), pistas y solución. En los retos 4 y 5 imita `npm run tipos`. El avance queda guardado en tu navegador.
- **Regenerarlo** (instructor), desde la raíz: `python3 laboratorio/generar/generar.py`. Toma el código de las etiquetas `s04-inicio` y `s04-solucion`.

Para quitar los tipos de TypeScript en el navegador usa [Sucrase](https://github.com/alangpierce/sucrase) (licencia MIT), incluido en `generar/sucrase.min.js`.
