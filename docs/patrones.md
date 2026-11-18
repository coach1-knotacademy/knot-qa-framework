# Patrones de diseño del framework (S5)

Los cuatro patrones no son piezas nuevas: le ponen nombre y reglas a las capas que armamos en la S3 (ver [arquitectura.md](arquitectura.md)). Este archivo lo genera `laboratorio/generar/generar_actividades_s5.py` desde `fichas_s5.py`, la misma fuente de las actividades y del deck: si cambias una ficha, cámbiala allí.

| Patrón | Capa de la S3 | Dónde verlo |
|---|---|---|
| Page Object | `src/paginas/` | `PaginaRecargas`, `src/sitios/parabank/paginas/` |
| Factory | `src/datos/` | `fabricaDeRecargas`, `fabricaDeTransferencias`, `src/sitios/parabank/fabricaDeClientes.ts` |
| Screenplay | `src/flujos/` → `src/screenplay/` | `Actor.ts`, `billetera/`, `src/sitios/parabank/screenplay/tareas.ts` |
| Singleton | `src/config/` | `entorno.ts`, `src/sitios/parabank/entorno.ts` |
| (Inyección de dependencias, S4) | `src/soporte/` | los fixtures: la prueba pide sus piezas |

## Page Object

*Lo construyeron en la S3: `PaginaLogin`, `PaginaOtp` y `PaginaTransferir` (retos 1 a 3). Hoy le ponemos nombre y reglas.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | Cambian el botón «Ingresar» por «Entrar» y hay que corregir 40 casos en el ALM. |
| **La idea, en una frase** | El **manual de una pantalla**: lo que la pantalla **tiene** (campos, botones) y lo que **sabe hacer** (transferir, recargar). La prueba dice **qué**; la página sabe **cómo**. |
| **Sus partes, en el repo** | Localizadores `private` (lo que tiene) · métodos con nombre de negocio, como `recargar()` (lo que sabe hacer) · su `ruta` · hereda de `PaginaBase`. |
| **Sí, cuando** | Toda pantalla que usa más de una prueba. |
| **No, cuando** | Con `expect` adentro: la página no decide si algo está bien, eso lo dice la prueba. Tampoco una sola clase gigante para todo el sitio. |
| **La frase para tu líder** | «Si rediseñan el portal de transferencias, se arregla un archivo, no 200 casos.» |
| **Cómo pedírselo a la IA** | «Usa `PaginaRecargas`; no escribas localizadores dentro de la prueba.» |

## Factory

*En la S3 era `usuarios.ana`: datos con nombre en un solo lugar. La fábrica es el paso siguiente.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | «El usuario de pruebas de siempre» ya lo usó otro y la prueba falla. O la hoja de datos tiene 30 copias del mismo monto y nadie sabe por qué es 60.000. |
| **La idea, en una frase** | Pides los datos por su **nombre de negocio** («una recarga grande») y la fábrica te entrega un objeto **nuevo y válido** cada vez. |
| **Sus partes, en el repo** | `valida()`, el molde con valores por defecto · variantes con nombre: `grande()`, `aOperadorCaido()` · `cambios`: solo escribes lo que le importa a esa prueba. |
| **Sí, cuando** | Datos que se repiten o que tienen reglas: el monto que pide código, el límite diario, un cliente único por corrida en ParaBank. |
| **No, cuando** | Un dato que usa una sola prueba. **Nunca** datos copiados de producción: datos personales reales (habeas data). |
| **La frase para tu líder** | «Si el banco sube el umbral del código a $80.000, se cambia un número, no 30 pruebas. Y ningún dato sale de producción.» |
| **Cómo pedírselo a la IA** | «Los datos salen de `fabricaDeRecargas`; no escribas montos ni números a mano.» |

## Screenplay

*En la S3, `iniciarSesionPorUi()` ya era una tarea, aunque no se llamara así. Screenplay ordena todas las tareas alrededor de quien las hace.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | El caso dice «Ana transfiere $50 a ahorros», pero la prueba son 12 clics que no cuentan la historia. Y con dos roles (quien crea y quien aprueba) se vuelve un enredo. |
| **La idea, en una frase** | La prueba contada por un **actor**: **quién** (Actor), **con qué** (Habilidad), **qué hace** (Tarea) y **qué revisa** (Pregunta). |
| **Sus partes, en el repo** | `Actor.llamado('Ana')` · `.puede(...)` le da una Habilidad (el navegador, la API) · `.intenta(...)` hace Tareas · `.pregunta(...)` responde Preguntas. |
| **Sí, cuando** | Hay varios roles con habilidades distintas. Ejemplo: **doble autorización** (maker-checker), donde un cliente crea una transferencia sobre el tope y un aprobador la autoriza. También prepara BDD (S7). |
| **No, cuando** | Una suite pequeña con un solo rol: Page Object y flujos bastan. No es mejor ni peor: se usan juntos, porque una tarea usa un Page Object por dentro. |
| **La frase para tu líder** | «La prueba se lee como el caso del ALM: el negocio la puede revisar sin saber programar.» |
| **Cómo pedírselo a la IA** | «Escribe la prueba con un Actor y las tareas de `src/screenplay/`.» |

## Singleton

*En la S3, `entorno.ts` ya era único: la dirección del ambiente en un solo lugar.*

| | |
|---|---|
| **El problema que ya sufrías a mano** | Cada tester anota su propia URL del ambiente: uno prueba en QA y otro, sin saberlo, en UAT. |
| **La idea, en una frase** | De algunas cosas debe existir **una sola**: la configuración. De otras, **una por prueba**: el navegador, la sesión y el cliente. |
| **Sus partes, en el repo** | Un solo objeto `entorno` (dirección, usuario, tiempos) que se lee de variables de entorno. En TypeScript un módulo ya es único: no hace falta la clase con `getInstance()`. |
| **Sí, cuando** | La configuración de cada ambiente (QA, UAT) y las reglas de convivencia con un sitio real, como la pausa entre pruebas para que ParaBank no responda 429. |
| **No, cuando** | Un navegador o una sesión compartidos (`DriverManager.getInstance()`): en paralelo, una prueba puede ver la cuenta de otro cliente. Es un **incidente de confidencialidad**, no una prueba inestable. |
| **La frase para tu líder** | «Nadie corre contra producción por error: el ambiente vive en un solo lugar.» |
| **Cómo pedírselo a la IA** | «La dirección sale de la configuración; nunca la escribas dentro de la prueba.» |

## Cómo leer una prueba

| Lo que ves | Cómo se lee |
|---|---|
| `async` / `await` | «espera a que este paso termine antes de seguir», como en el caso manual: un paso a la vez. |
| `{ paginaRecargas, cliente }` | las piezas que la prueba **pide**; alguien más se las entrega (los fixtures, la D de la S4). |
| `paginaRecargas.recargar(...)` | «a esta pantalla, pídele que haga esto». El punto separa **quién** de **qué hace**. |
| `class` · `new` | la clase es el molde; `new` saca un objeto del molde. |
| `private` | solo la clase lo toca. Las pruebas no ven los localizadores. |
| `this.` | «lo mío»: el campo o el método de esta misma clase. |
| `.desde(...).hacia(...).por(...)` | una frase de negocio dicha en pedazos: «transferir desde la principal hacia ahorros por 50». |

## Los cuatro juntos: la prueba CP-021

En `tests/recargas/recargas.spec.ts`. Se corre sola con `npx playwright test -g "CP-021"`.

```ts
test('CP-021 · una recarga de más de $50.000 pide código…',
  async ({ paginaRecargas, cliente }) => {
  await paginaRecargas.recargar(fabricaDeRecargas.grande());
  await expect(paginaRecargas.campoCodigo).toBeVisible();
  const codigo = await cliente.leerCodigo(usuarios.ana.usuario);
  await paginaRecargas.confirmar(codigo);
  expect(await paginaRecargas.esperarResultado())
    .toContain('Valor: $60.000');
});
```

| Línea | Qué patrón usa |
|---|---|
| `test('CP-021 · una recarga de más de $50.000 pide código…',` | Trazabilidad: el ID del caso del ALM va en el nombre. |
| `async ({ paginaRecargas, cliente }) => {` | Fixtures: la prueba pide sus piezas. |
| `await paginaRecargas.recargar(fabricaDeRecargas.grande());` | Page Object + Factory. |
| `await expect(paginaRecargas.campoCodigo).toBeVisible();` | La prueba decide qué está bien, no la página. |
| `const codigo = await cliente.leerCodigo(usuarios.ana.usuario);` | API + datos con nombre. |
| `await paginaRecargas.confirmar(codigo);` | Page Object. |
| `.toContain('Valor: $60.000');` | El esperado sale de la regla, no de la pantalla. |

## Fuentes

- Page Object: Martin Fowler, «PageObject» (martinfowler.com/bliki/PageObject.html).
- Screenplay: Serenity/JS, «Screenplay Pattern» (serenity-js.org).
- Factory y Singleton: Gamma, Helm, Johnson y Vlissides, *Design Patterns* (1994). En pruebas, la «fábrica de datos» es lo que también se llama *Object Mother* o *Test Data Builder*.
