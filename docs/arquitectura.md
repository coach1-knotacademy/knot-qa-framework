# Arquitectura del framework

Un framework de automatización separa **qué se prueba** de **cómo se habla con el sistema**. Cada capa tiene una sola tarea y solo conoce a la capa de abajo.

```
  tests/                  QUÉ se prueba. Se lee como el caso manual. Sin localizadores.
     │  pide piezas a
     ▼
  src/soporte/            Fixtures: entregan las piezas ya armadas a cada prueba.
     │  arma
     ▼
  src/flujos/             Pasos de negocio que combinan varias piezas: "iniciar sesión".
     │  usa
     ▼
  src/paginas/  src/api/  CÓMO se habla con el sistema:
                          páginas → la pantalla (localizadores y acciones)
                          api     → los servicios (rutas, JSON, token)
     │  leen
     ▼
  src/config/  src/datos/ DÓNDE está el sistema y CON QUÉ datos se prueba.
     │
     ▼
  banco-demo/             El sistema bajo prueba. No es parte del framework.
```

## Qué va en cada carpeta

| Carpeta | Responde a | Ejemplo | Regla |
|---|---|---|---|
| `tests/` | ¿Qué se prueba? | `tests/ui/inicio.spec.ts` | Sin `getByLabel` ni URLs: solo pasos y resultados esperados. |
| `src/soporte/` | ¿Cómo recibe cada prueba sus piezas? | `fixtures.ts` | La prueba pide `paginaLogin`; no hace `new PaginaLogin(page)`. |
| `src/flujos/` | ¿Qué pasos de negocio se repiten? | `iniciarSesionPorUi`, `abrirConSesion` | Combina páginas y API. No tiene localizadores propios. |
| `src/paginas/` | ¿Cómo se usa cada pantalla? | `PaginaLogin.ingresar()` | Un archivo por pantalla. Los localizadores viven solo aquí. Sin `expect`. Desde la S6, por rol o etiqueta (la escalera de abajo). |
| `src/api/` | ¿Cómo se llama a cada servicio? | `ClienteBanco.cuentas()` | Guarda el token. Devuelve `{ estado, datos }`; no decide si está bien. |
| `src/config/` | ¿Dónde está el sistema? | `entorno.urlBase` | Todo valor que cambia entre ambientes sale de aquí, con variables de entorno. Desde la S6, un catálogo de ambientes (`ambientes.ts`). |
| `src/datos/` | ¿Con qué datos? | `usuarios.ana` | Nada de `'Clave123'` regado por las pruebas. |
| `src/legado/` (S4) | Código heredado para refactorizar | `AyudanteTodo` | Ejemplos de lo que SOLID evita. |
| `src/screenplay/` (S5) | ¿Quién hace qué, contado como el caso manual? | `Actor`, `Recargar` | Las tareas usan páginas o API por dentro. Opcional. |
| `src/sitios/parabank/` (S5) | Otro sistema bajo prueba, con la **misma forma** | `PaginaTransferirParaBank` | Cada sitio trae sus páginas, su API, su configuración, su fábrica y sus fixtures. Las capas no cambian. |
| `src/config/ambientes.ts` (S6) | ¿Contra qué ambiente corre la suite? | `configurarAmbiente('qa', process.env)` | Catálogo `local`, `qa`, `uat`. Producción bloqueada, clave obligatoria fuera de `local`, configuración congelada. |
| `src/paginas/heredadas/` (S6) | Un Page Object que nos dejó otro equipo | `PaginaRecargasHeredada` | Localizadores frágiles para cambiar por robustos. Se prueba contra Recargas de hoy y la del rediseño (`?rediseno=1`). |
| `plantilla/` (S6) | ¿Cómo arranco el framework de mi proyecto? | `tests/CP-101-recarga.spec.ts` | Un framework mínimo aparte, con las mismas capas y el prompt para Copilot. No entra en las pruebas de este repo. |

## Por qué así

Compara `tests/antes/espagueti.spec.ts` con `tests/ui/inicio.spec.ts`:

- **Si cambia la pantalla**, se corrige una página y no veinte pruebas.
- **Si cambia el ambiente**, se cambia una variable de entorno y no el código.
- **Si cambia el servicio** (como la migración a `/api/v2/cuentas`), se ajusta `ClienteBanco` y las pruebas siguen iguales.
- **Las pruebas se leen como el caso manual**: cualquiera del equipo puede revisarlas.

## Patrones de diseño (S5): el nombre de lo que ya construimos

Las capas de la S3 ya eran patrones; en la S5 les pusimos nombre y reglas. Las fichas completas (problema, partes, sí/no, la frase para tu líder) están en [patrones.md](patrones.md).

| Capa | Patrón | Su regla en una línea |
|---|---|---|
| `src/paginas/` | **Page Object** | La página sabe **cómo**; la prueba dice **qué**. Sin `expect` adentro. |
| `src/datos/` | **Factory** | Datos con nombre de negocio; un objeto nuevo en cada llamada. Nunca datos de producción. |
| `src/flujos/` → `src/screenplay/` | **Screenplay** | Actor, Habilidad, Tarea y Pregunta. Útil con varios roles (maker-checker). |
| `src/config/` | **Singleton** | Una sola configuración. El navegador y la sesión, nunca únicos. |
| `src/soporte/` | **Inyección de dependencias** (la D de SOLID, S4) | La prueba pide sus piezas; los fixtures se las entregan. |

## Configuración y localizadores (S6): las dos capas que más rompen una suite

| Capa | Qué la rompe en un equipo real | Cómo se protege aquí |
|---|---|---|
| `src/config/` | Correr contra el ambiente equivocado, una clave en el código, alguien que cambia la configuración a mitad de la corrida | `AMBIENTE=local\|qa\|uat` con lista blanca (producción bloqueada) · `CLAVE_BANCO` obligatoria fuera de `local`, por la terminal o un `.env` que nunca se sube · `Object.freeze` |
| `src/paginas/` | Desarrollo cambia ids, clases u orden de la pantalla | La escalera de localizadores: `getByRole(rol, { name })` → `getByLabel` → `getByText` → `getByTestId` pactado → CSS o XPath nunca |

El ambiente y la dirección salen en el reporte de Playwright (`metadata`); la clave, nunca. Fichas completas: [configuracion-y-localizadores.md](configuracion-y-localizadores.md). Retos: [`retos/S06.md`](../retos/S06.md).

**Trazabilidad:** el ID del caso manual (el del ALM) va en el nombre de la prueba, como `CP-021 · …` en `tests/recargas/recargas.spec.ts`. Así el reporte se cruza con la matriz de casos y se corre solo ese caso con `-g "CP-021"`.

## Cómo crece este framework (y el de ustedes)

| Sesión | Lo que se le agrega | Dónde |
|---|---|---|
| S3 | Las capas | `tests/`, `src/` |
| S4 | SOLID: por qué las capas están así | `src/legado/` (el antes) |
| S5 | Patrones: Page Object, Factory, Screenplay, Singleton · un sitio real | `src/screenplay/`, `src/sitios/` |
| S6 | Ambientes (`local`, `qa`, `uat`; producción bloqueada; clave por la terminal; configuración congelada) y localizadores robustos · tu CP convertido en prueba · la plantilla de tu framework | `src/config/ambientes.ts`, `src/paginas/heredadas/`, `plantilla/` |
| S7 | Gherkin/BDD: tu CP de la S6 con otra sintaxis, sobre las tareas de Screenplay | sobre `src/flujos/` y `src/screenplay/` |
| S8 | Data Driven sobre las fábricas y reportería (reporte HTML con evidencias; Allure solo demo) | `src/datos/`, reportes |
| S9 | Logging, manejo de errores, reutilizables e integración continua | `src/soporte/`, `.github/workflows/` |
| S10 | Presentaciones: tu framework o tu revisión | tu repo, con estas mismas capas |

El framework que presentan en la S10 tiene esta misma forma: si alguien abre su repo, debe reconocer cada capa. Para arrancarlo: [`plantilla/`](../plantilla/README.md).

## Programación orientada a objetos en este repo

| Concepto | Dónde verlo |
|---|---|
| Clase y objeto | `PaginaInicio` es la clase (el molde); `new PaginaInicio(page)` crea un objeto. |
| Constructor | `constructor(page: Page)` en cada página: arma los localizadores una sola vez. |
| Herencia | `PaginaLogin extends PaginaBase`: recibe `abrir()` y `mensajeDeError` sin escribirlos. |
| Polimorfismo | `abrir()` está una sola vez en `PaginaBase` y abre una pantalla distinta según la `ruta` de cada hija. |
| Encapsulamiento | Los localizadores son `private`; el token de `ClienteBanco` también. Las pruebas no los tocan. |

## Cómo se marcan los bugs encontrados

Una prueba que encuentra un bug conocido llama a `hallazgoEsperado('BUG-01', '...')` (en `src/soporte/hallazgos.ts`). La prueba describe el comportamiento **correcto**; como el bug existe, falla, y Playwright la cuenta como "falla esperada". Así la suite queda en verde, el bug queda registrado en el reporte y, si algún día lo corrigen, Playwright avisa.
