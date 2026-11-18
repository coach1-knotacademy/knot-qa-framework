"""Las fichas de los cuatro patrones de la S5: UNA sola fuente.

La usan: laboratorio/generar/generar_actividades_s5.py (pestaña Fichas y docs/patrones.md)
y el deck del instructor (sesion_05/generar_deck_S5.py). Así nunca dicen cosas distintas.

Marcado mínimo: `código` y **negrita**. md() lo deja para Markdown; a_html() lo pasa a HTML.
"""
import html, re

def a_html(texto):
    t = html.escape(texto, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)

# Las filas de cada ficha, siempre en el mismo orden.
FILAS = [
  ('problema', 'El problema que ya sufrías a mano'),
  ('idea', 'La idea, en una frase'),
  ('partes', 'Sus partes, en el repo'),
  ('si', 'Sí, cuando'),
  ('no', 'No, cuando'),
  ('lider', 'La frase para tu líder'),
  ('ia', 'Cómo pedírselo a la IA'),
]

FICHAS = [
  {
    'id': 'pom', 'nombre': 'Page Object', 'capa': 'src/paginas/',
    'desde': 'Lo construyeron en la S3: `PaginaLogin`, `PaginaOtp` y `PaginaTransferir` (retos 1 a 3). Hoy le ponemos nombre y reglas.',
    'problema': 'Cambian el botón «Ingresar» por «Entrar» y hay que corregir 40 casos en el ALM.',
    'idea': 'El **manual de una pantalla**: lo que la pantalla **tiene** (campos, botones) y lo que **sabe hacer** (transferir, recargar). La prueba dice **qué**; la página sabe **cómo**.',
    'partes': 'Localizadores `private` (lo que tiene) · métodos con nombre de negocio, como `recargar()` (lo que sabe hacer) · su `ruta` · hereda de `PaginaBase`.',
    'si': 'Toda pantalla que usa más de una prueba.',
    'no': 'Con `expect` adentro: la página no decide si algo está bien, eso lo dice la prueba. Tampoco una sola clase gigante para todo el sitio.',
    'lider': '«Si rediseñan el portal de transferencias, se arregla un archivo, no 200 casos.»',
    'ia': '«Usa `PaginaRecargas`; no escribas localizadores dentro de la prueba.»',
  },
  {
    'id': 'factory', 'nombre': 'Factory', 'capa': 'src/datos/',
    'desde': 'En la S3 era `usuarios.ana`: datos con nombre en un solo lugar. La fábrica es el paso siguiente.',
    'problema': '«El usuario de pruebas de siempre» ya lo usó otro y la prueba falla. O la hoja de datos tiene 30 copias del mismo monto y nadie sabe por qué es 60.000.',
    'idea': 'Pides los datos por su **nombre de negocio** («una recarga grande») y la fábrica te entrega un objeto **nuevo y válido** cada vez.',
    'partes': '`valida()`, el molde con valores por defecto · variantes con nombre: `grande()`, `aOperadorCaido()` · `cambios`: solo escribes lo que le importa a esa prueba.',
    'si': 'Datos que se repiten o que tienen reglas: el monto que pide código, el límite diario, un cliente único por corrida en ParaBank.',
    'no': 'Un dato que usa una sola prueba. **Nunca** datos copiados de producción: datos personales reales (habeas data).',
    'lider': '«Si el banco sube el umbral del código a $80.000, se cambia un número, no 30 pruebas. Y ningún dato sale de producción.»',
    'ia': '«Los datos salen de `fabricaDeRecargas`; no escribas montos ni números a mano.»',
  },
  {
    'id': 'screenplay', 'nombre': 'Screenplay', 'capa': 'src/flujos/ → src/screenplay/',
    'desde': 'En la S3, `iniciarSesionPorUi()` ya era una tarea, aunque no se llamara así. Screenplay ordena todas las tareas alrededor de quien las hace.',
    'problema': 'El caso dice «Ana transfiere $50 a ahorros», pero la prueba son 12 clics que no cuentan la historia. Y con dos roles (quien crea y quien aprueba) se vuelve un enredo.',
    'idea': 'La prueba contada por un **actor**: **quién** (Actor), **con qué** (Habilidad), **qué hace** (Tarea) y **qué revisa** (Pregunta).',
    'partes': '`Actor.llamado(\'Ana\')` · `.puede(...)` le da una Habilidad (el navegador, la API) · `.intenta(...)` hace Tareas · `.pregunta(...)` responde Preguntas.',
    'si': 'Hay varios roles con habilidades distintas. Ejemplo: **doble autorización** (maker-checker), donde un cliente crea una transferencia sobre el tope y un aprobador la autoriza. También prepara BDD (S7).',
    'no': 'Una suite pequeña con un solo rol: Page Object y flujos bastan. No es mejor ni peor: se usan juntos, porque una tarea usa un Page Object por dentro.',
    'lider': '«La prueba se lee como el caso del ALM: el negocio la puede revisar sin saber programar.»',
    'ia': '«Escribe la prueba con un Actor y las tareas de `src/screenplay/`.»',
  },
  {
    'id': 'singleton', 'nombre': 'Singleton', 'capa': 'src/config/',
    'desde': 'En la S3, `entorno.ts` ya era único: la dirección del ambiente en un solo lugar.',
    'problema': 'Cada tester anota su propia URL del ambiente: uno prueba en QA y otro, sin saberlo, en UAT.',
    'idea': 'De algunas cosas debe existir **una sola**: la configuración. De otras, **una por prueba**: el navegador, la sesión y el cliente.',
    'partes': 'Un solo objeto `entorno` (dirección, usuario, tiempos) que se lee de variables de entorno. En TypeScript un módulo ya es único: no hace falta la clase con `getInstance()`.',
    'si': 'La configuración de cada ambiente (QA, UAT) y las reglas de convivencia con un sitio real, como la pausa entre pruebas para que ParaBank no responda 429.',
    'no': 'Un navegador o una sesión compartidos (`DriverManager.getInstance()`): en paralelo, una prueba puede ver la cuenta de otro cliente. Es un **incidente de confidencialidad**, no una prueba inestable.',
    'lider': '«Nadie corre contra producción por error: el ambiente vive en un solo lugar.»',
    'ia': '«La dirección sale de la configuración; nunca la escribas dentro de la prueba.»',
  },
]

# Cómo leer una prueba (para quien no programa). Cada fila: lo que se ve, cómo se lee.
LEYENDA = [
  ('`async` / `await`', '«espera a que este paso termine antes de seguir», como en el caso manual: un paso a la vez.'),
  ('`{ paginaRecargas, cliente }`', 'las piezas que la prueba **pide**; alguien más se las entrega (los fixtures, la D de la S4).'),
  ('`paginaRecargas.recargar(...)`', '«a esta pantalla, pídele que haga esto». El punto separa **quién** de **qué hace**.'),
  ('`class` · `new`', 'la clase es el molde; `new` saca un objeto del molde.'),
  ('`private`', 'solo la clase lo toca. Las pruebas no ven los localizadores.'),
  ('`this.`', '«lo mío»: el campo o el método de esta misma clase.'),
  ('`.desde(...).hacia(...).por(...)`', 'una frase de negocio dicha en pedazos: «transferir desde la principal hacia ahorros por 50».'),
]

# La prueba CP-021 del repo (tests/recargas/recargas.spec.ts), línea por línea, con el patrón que usa cada una.
CP021 = [
  ("test('CP-021 · una recarga de más de $50.000 pide código…',", 'Trazabilidad: el ID del caso del ALM va en el nombre.'),
  ("  async ({ paginaRecargas, cliente }) => {", 'Fixtures: la prueba pide sus piezas.'),
  ("  await paginaRecargas.recargar(fabricaDeRecargas.grande());", 'Page Object + Factory.'),
  ("  await expect(paginaRecargas.campoCodigo).toBeVisible();", 'La prueba decide qué está bien, no la página.'),
  ("  const codigo = await cliente.leerCodigo(usuarios.ana.usuario);", 'API + datos con nombre.'),
  ("  await paginaRecargas.confirmar(codigo);", 'Page Object.'),
  ("  expect(await paginaRecargas.esperarResultado())", ''),
  ("    .toContain('Valor: $60.000');", 'El esperado sale de la regla, no de la pantalla.'),
  ("});", ''),
]

# El boleto de salida: una pregunta por ficha. (pregunta, opciones, letra correcta, por qué)
BOLETO = [
  ('El botón «Recargar» pasa a llamarse «Recargar ya». ¿Dónde se corrige?',
   ['en cada prueba que recarga', 'en `PaginaRecargas`', 'en la fábrica'], 'b',
   'Page Object: el localizador vive en un solo lugar.'),
  ('Dos pruebas usan «el usuario de siempre» y una falla porque la otra le cambió el saldo. ¿Qué lo evita?',
   ['un Singleton del usuario', 'otro Page Object', 'una fábrica que entrega un cliente nuevo'], 'c',
   'Factory: un objeto nuevo y único en cada prueba.'),
  ('Un cliente crea una transferencia sobre el tope y un aprobador la autoriza. ¿Qué patrón cuenta mejor esa prueba?',
   ['Screenplay', 'Singleton', 'Factory'], 'a',
   'Screenplay: dos actores con habilidades distintas.'),
  ('¿Qué debe existir una sola vez en toda la corrida?',
   ['el navegador', 'la dirección del ambiente', 'la sesión del cliente'], 'b',
   'Singleton solo para la configuración; navegador y sesión, uno por prueba.'),
]
