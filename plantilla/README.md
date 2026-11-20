# Mi framework de QA · plantilla (S6)

Un framework mínimo y **propio**, con las mismas capas del `knot-qa-framework`, para empezar el de tu proyecto. Corre contra el **Banco Demo publicado en GitHub Pages**: no hace falta levantar ningún servidor.

```
src/config/ambientes.ts      catálogo de ambientes (demo, qa, uat), producción bloqueada, configuración congelada
src/config/entorno.ts        la configuración de la corrida (entorno.urlBase, entorno.usuario, entorno.clave)
src/paginas/PaginaBase.ts    lo que tienen en común todas las pantallas
src/paginas/PaginaRecargas.ts  un Page Object de ejemplo, con localizadores por rol y etiqueta
src/datos/fabricaDeRecargas.ts los datos de prueba, con nombres de negocio
src/flujos/sesion.ts         abrir la sesión sin pasar por las pantallas de ingreso
src/soporte/fixtures.ts      las piezas que recibe cada prueba
tests/CP-101-recarga.spec.ts una prueba que sale de un caso manual (el ID va en el nombre)
PROMPT.md                    el prompt para pedirle a tu Copilot una prueba nueva con esta forma
```

## Cómo usarla (Windows PowerShell)

1. Copia la carpeta `plantilla` a un lugar **fuera de OneDrive** y ábrela en VS Code.
2. En la terminal de VS Code, dentro de esa carpeta:

   ```powershell
   npm.cmd install
   npx.cmd playwright install chromium
   npm.cmd test
   ```

   Si tu equipo no deja descargar Chromium, usa el Edge instalado en lugar del segundo comando:

   ```powershell
   $env:PW_CHANNEL = 'msedge'
   npm.cmd test
   ```

3. El reporte: `npm.cmd run reporte`. Arriba dice contra qué ambiente se corrió.

Si `npm.cmd install` no funciona en tu equipo (sin acceso al registro de paquetes), no insistas: usa la [página de la plantilla](https://coach1-knotacademy.github.io/knot-qa-framework/plantilla.html) para leer y copiar los archivos, y practica en el laboratorio de la S6.

## Ambientes

Sin variables se usa `demo`. Para otro ambiente, solo en esa ventana:

```powershell
$env:AMBIENTE = 'qa'
$env:CLAVE_BANCO = '...'
npm.cmd test
```

- `qa` y `uat` tienen direcciones de ejemplo (`.ejemplo`): cámbialas en `src/config/ambientes.ts` por las de tu proyecto. **Nunca agregues producción.**
- Fuera de `demo`, si falta `CLAVE_BANCO` la corrida se detiene de inmediato y dice qué hacer.
- Cualquier ambiente que no esté en el catálogo (`produccion`, `prod`…) se bloquea.
- Si prefieres un archivo, copia `.env.ejemplo` como `.env` y llénalo. El `.env` nunca se sube (está en `.gitignore`).

## Para agregar tu caso

1. Pide la prueba con [`PROMPT.md`](PROMPT.md) (o escríbela tú con la misma forma que `CP-101`).
2. Antes de correrla, revísala con la lista de cotejo: localizadores por rol o etiqueta, URL desde `entorno`, sin claves, sin `waitForTimeout`, datos desde la fábrica, esperado desde la regla y el ID del caso en el nombre.
3. Córrela sola: `npx.cmd playwright test -g "CP-102"`.

Solo sitios de práctica (Banco Demo y ParaBank). Nunca datos, pantallas ni casos del banco donde trabajas.
