# Retos avanzados de la S3 · para quien terminó

Mismo repo, mismos fixtures, mismo `verificar-clase`. **No se toca la infraestructura:** solo creas archivos nuevos (y en el reto C mueves dos líneas de herencia).

| Reto | Concepto | Necesita | Archivo nuevo |
|---|---|---|---|
| A · Del espagueti al framework | Capas | Retos 1, 2, 3 y 5 | `tests/ui/avanzado-a-transferencia.spec.ts` |
| B · El saldo de punta a punta | Capas y soporte | Reto 3 | `src/soporte/dinero.ts` y `tests/ui/avanzado-b-saldo.spec.ts` |
| C · Una clase intermedia | Herencia | Reto 5 | `src/paginas/PaginaConSesion.ts` y `tests/ui/avanzado-c-salir.spec.ts` |
| D · BUG-01 por API | Capa de API | Reto 4 | `tests/api/avanzado-d-monto-minimo.spec.ts` |

**Ruta 2 (GitHub):** los archivos nuevos se crean con **Add file → Create new file**. Escribe la ruta completa en el nombre (por ejemplo, `tests/ui/avanzado-a-transferencia.spec.ts`) y GitHub crea las carpetas.

Al terminar, `npm.cmd run verificar-clase` debe seguir en **TODO EN ORDEN**: tus pruebas nuevas aparecen en "PRUEBAS BASE" y los hallazgos en "HALLAZGOS ESPERADOS".

---

## A · Del espagueti al framework

Abre `tests/antes/espagueti.spec.ts` y busca la prueba **"transferencia válida desde Ahorros entrega comprobante"**: son 27 líneas con localizadores, URLs y la clave escritos a mano.

**Tu trabajo:** escribe la misma prueba en `tests/ui/avanzado-a-transferencia.spec.ts` usando las capas.

**Criterio de éxito:** el archivo no tiene ni un `getBy`, ni `'Clave123'`, ni `http://`.

**Pistas:**

- Las piezas se piden en la prueba: `async ({ paginas, paginaTransferir }) => { … }`.
- Para entrar: `iniciarSesionPorUi(paginas, usuarios.ana)`.
- Para transferir: `paginaTransferir.abrir()` y `paginaTransferir.transferir({ destino: cuentas.destino, monto: 100_000 })`.
- Para revisar: `esperarResultado()` y `paginaTransferir.comprobante`.

**Revisa:** `npx.cmd playwright test avanzado-a --project=ui`

**Para conversar:** cuenta las líneas de las dos versiones. ¿Cuál le mostrarías a tu líder?

## B · El saldo de punta a punta

**Tu trabajo:** lee el saldo de Ahorros en "Mis cuentas", transfiere $100.000 y comprueba en pantalla que el saldo bajó **el monto más el 4x1000**.

**Pistas:**

- La pantalla muestra `"$1.500.000"`, que es texto. Convertirlo en número es una utilidad que van a usar muchas pruebas, así que va en **soporte**: crea `src/soporte/dinero.ts` con `aNumero(texto)` y `gmf(monto)`.
- `paginaInicio.saldoDe('Ahorros')` devuelve el saldo que ve el cliente.
- Para entrar sin pasar por el login: `abrirConSesion(page, cliente)`.

**Segunda prueba:** haz lo mismo desde **Corriente** con $50.000. El banco no descuenta el 4x1000, y tu prueba lo encuentra **por pantalla**. Escríbela con el resultado correcto y márcala con `hallazgoEsperado('BUG-02', '…')`.

**Revisa:** `npx.cmd playwright test avanzado-b --project=ui`. La de Ahorros pasa. La de Corriente cuenta como hallazgo esperado: falla con `Expected: 199800` y `Received: 200000`.

**Para conversar:** ¿por qué `aNumero` va en soporte y no en la página ni en la prueba?

## C · Una clase intermedia

Solo **Mis cuentas** y **Transferir** tienen el nombre del cliente y el botón **Salir**. Login, OTP y Buzón no.

**Tu trabajo:**

1. Crea `src/paginas/PaginaConSesion.ts`: una clase **abstracta** que hereda de `PaginaBase` y tiene el localizador del botón Salir (privado) y el método `salir()`.
2. Haz que `PaginaInicio` y `PaginaTransferir` hereden de `PaginaConSesion` en lugar de `PaginaBase`. Mueve `nombreDelCliente` de `PaginaInicio` a la clase nueva.
3. Escribe `tests/ui/avanzado-c-salir.spec.ts`: entra con `iniciarSesionPorUi`, sal con `paginaInicio.salir()` y comprueba que, al volver a abrir Mis cuentas, el banco te devuelve al ingreso (`paginaLogin.esperarQueCargue()`).

**Revisa:** `npx.cmd playwright test avanzado-c --project=ui` y luego `npm.cmd run verificar-clase` para comprobar que los retos de la S3 siguen en RESUELTO.

**Para conversar:**

- ¿Por qué no poner `salir()` en `PaginaBase`? Pista: ¿qué pasaría con `paginaLogin.salir()`? Esa pregunta vuelve en la S4, en los retos 3 y 4.
- **¿Herencia o composición?** Otra opción es un componente `BarraDeSesion` (con `salir()` y el nombre del cliente) que `PaginaInicio` y `PaginaTransferir` *tienen* en lugar de *heredar*. ¿Cuál preferirías si mañana aparece una pantalla con sesión pero sin barra?

**Extra:** cambia `iniciarSesionPorUi` por `abrirConSesion` y córrela. La prueba se queda esperando. ¿Por qué? (Pista: lee qué hace `page.addInitScript` en `src/flujos/sesion.ts` y cuándo se ejecuta.)

## D · BUG-01 por API

Para quien vive en Postman.

**Tu trabajo:** en `tests/api/avanzado-d-monto-minimo.spec.ts`, inicia sesión con el `cliente`, transfiere **exactamente $1.000** desde Ahorros y espera un `201`.

**Pistas:**

- `await cliente.iniciarSesion(usuarios.ana)` deja el token guardado: la prueba no lo ve.
- `cliente.transferir(cuentas.ahorros.numero, cuentas.destino, 1_000)` devuelve `{ estado, datos }`.
- `expect(estado, datos.error).toBe(201)`: el segundo argumento hace que el reporte muestre el mensaje del banco si falla.

El banco responde `400` con «El monto mínimo es $1.000». Márcala con `hallazgoEsperado('BUG-01', '…')`.

**Revisa:** `npx.cmd playwright test avanzado-d --project=api`

**Para conversar:** el mismo bug apareció en el reto 3 por pantalla. ¿Cuál de las dos pruebas le darías a desarrollo, y por qué?
