# knot-qa-framework

Framework de automatización de práctica del **Bootcamp de QA & Automatización · Knot Academy × Accenture**. Desde la S3 lo construimos por capas, con clases, principios SOLID y patrones de diseño, usando Playwright y TypeScript sobre el **Banco Demo** y, desde la S5, sobre **ParaBank**, un banco de práctica real en internet. El Banco Demo es un banco de práctica que corre en tu equipo, sin internet, con login, código OTP, saldos, transferencias, 4x1000 y recargas a celular. El Banco Demo tiene bugs sembrados a propósito: no los corrijas.

## Cómo empezar

| Ruta | Necesitas | Pasos |
|---|---|---|
| **1 · En tu equipo** | Poder ejecutar programas | Descarga el repo (**Code → Download ZIP**), clic derecho en el ZIP → **Propiedades → Desbloquear**, extráelo fuera de OneDrive y haz **doble clic en `preparar.cmd`**. Cuando diga **LISTO**, en esa misma ventana: `npm.cmd run retos:s03` |
| **2 · En la nube** | Una cuenta personal de GitHub | **Use this template → Create a new repository**. En tu copia, abre el archivo del reto y edítalo con el lápiz ✏️ → **Commit changes**. En la pestaña **Actions** verás la verificación; abajo, en **Artifacts**, descarga `evidencias.html` |
| **3 · Solo navegador** | Un navegador | Lee el código y los retos aquí en GitHub y explora el [Banco Demo en línea](https://coach1-knotacademy.github.io/knot-qa-framework/banco/index.html) (`ana` / `Clave123`) |

Si la Ruta 1 no funciona en 5 minutos, pasa a la 2. Si GitHub tampoco abre, ve a la 3.

**Laboratorio de la S4, sin instalar nada:** [`laboratorio/laboratorio_S4.html`](laboratorio/laboratorio_S4.html) trae los 5 retos de la S4 con sus pruebas y corre en el navegador (descárgalo y ábrelo con Edge). También está en línea: [laboratorio de la S4](https://coach1-knotacademy.github.io/knot-qa-framework/laboratorio-s4.html). Para quien termine: [práctica extra](https://coach1-knotacademy.github.io/knot-qa-framework/practica-extra-s4.html) (archivo `laboratorio/practica_extra_S4.html`).

**S5 · Patrones y un sitio real:** [`retos/S05.md`](retos/S05.md). Laboratorio sin instalar nada: [laboratorio de la S5](https://coach1-knotacademy.github.io/knot-qa-framework/laboratorio-s5.html) y [actividades de la clase](https://coach1-knotacademy.github.io/knot-qa-framework/actividades-s5.html). Lo que escribió la IA con y sin el repo, y qué pasó al correrlo: [`docs/ia-s5/`](docs/ia-s5/README.md). La suite de ParaBank corre en GitHub Actions cada vez que se publica y deja su reporte con videos y traces: [reporte de ParaBank](https://coach1-knotacademy.github.io/knot-qa-framework/reportes/parabank/index.html).

**Validación automática:** en tu copia (Ruta 2), cada push y cada pull request corre el flujo **Retos** (`npm run tipos` y `npm run retos:s04`, en menos de un minuto). En la pestaña **Actions** ves si quedó en verde.

## Comandos

| Comando | Qué hace |
|---|---|
| `npm test` | Corre todas las pruebas (el Banco Demo se inicia solo) |
| `npm run retos:s03` · `npm run retos:s04` · `npm run retos:s05` | Corre solo los retos de esa sesión |
| `npm run recargas` | S5 · Recargas a celular en el Banco Demo (Page Object, Factory y bloqueos reales) |
| `npm run parabank` · `npm run parabank:ver` | S5 · La suite de ParaBank, en internet (`:ver` abre el navegador). Va de a una prueba: el sitio bloquea 5 minutos a quien hace demasiadas peticiones (HTTP 429) |
| `npm run verificar-clase` | Revisa todo y muestra una tabla: pruebas base, retos y hallazgos. Con `-- s03-inicio` (o `s03-solucion`, `s04-inicio`, `s04-solucion`) exige exactamente el estado de esa etiqueta |
| `npm run evidencias` | Crea `evidencias.html` con los resultados y pantallazos |
| `npm run demo` | Abre el Banco Demo para explorarlo a mano en http://127.0.0.1:4000 |
| `npm run grabar` | Graba pasos con codegen (antes, deja `npm run demo` abierto en otra ventana) |

En Windows PowerShell escribe `npm.cmd` en lugar de `npm`.

## Capas

| Carpeta | Responde a | Ejemplo |
|---|---|---|
| `tests/` | ¿Qué se prueba? | `tests/ui/inicio.spec.ts` |
| `src/soporte/` | ¿Cómo recibe cada prueba sus piezas? | fixtures: `paginaLogin`, `cliente` |
| `src/flujos/` | ¿Qué pasos de negocio se repiten? | `iniciarSesionPorUi`, `abrirConSesion` |
| `src/paginas/` | ¿Cómo se usa cada pantalla? | `PaginaLogin.ingresar()` |
| `src/api/` | ¿Cómo se llama a cada servicio? | `ClienteBanco.cuentas()` |
| `src/config/` · `src/datos/` | ¿Dónde está el sistema y con qué datos? | `entorno.urlBase`, `usuarios.ana`, `fabricaDeRecargas.grande()` |
| `src/screenplay/` | S5 · ¿Cómo se cuenta la prueba como un caso manual? | `Actor`, `Recargar`, `SaldoDisponible` |
| `src/sitios/parabank/` | S5 · Las mismas capas, para otro sitio | páginas, API, fábrica, fixtures y tareas de ParaBank |

Explicación y diagrama: [`docs/arquitectura.md`](docs/arquitectura.md). Para ver el "antes", abre [`tests/antes/espagueti.spec.ts`](tests/antes/espagueti.spec.ts).

## Sesiones

| Sesión | Tema | Qué crece |
|---|---|---|
| S3 | Arquitectura por capas y clases | `src/paginas`, `src/api`, `src/flujos` · [retos/S03.md](retos/S03.md) |
| S4 | Principios SOLID | `src/legado` y `tests/retos-s04` · [retos/S04.md](retos/S04.md) |
| S5 | Patrones de diseño | Page Object, Factory (`src/datos/fabrica*.ts`), Screenplay (`src/screenplay`) y un sitio real (`src/sitios/parabank`) · [retos/S05.md](retos/S05.md) |
| S6 | Configuración y localizadores | `src/config` (ambientes) y `src/paginas` (localizadores robustos) |
| S7 | BDD | `features/` con escenarios Gherkin que llaman a `src/flujos` |
| S8 | Datos de prueba y Allure | `src/datos` (CSV y generadores) y reporte Allure |
| S9 | Logging | `src/soporte` (bitácora de cada paso) |
| S10 | CI/CD | `.github/workflows` (pipeline completo) |

## Puntos de partida

Cada sesión tiene una etiqueta: `s03-inicio`, `s03-solucion`, `s04-inicio`, `s04-solucion`, `s05-inicio`, `s05-solucion`. Si te atrasaste, empieza desde la etiqueta de la sesión:

```
git stash -u
git fetch --tags
git switch -c mi-s04 s04-inicio
```
