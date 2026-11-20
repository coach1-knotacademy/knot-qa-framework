"""Genera laboratorio/laboratorio_S6.html: los retos de la S6 con sus pruebas, para correr en el navegador sin instalar nada.

Usa el mismo motor de pruebas que el de la S5, en una copia extendida de la plantilla (plantilla_s6.html), más el
motor de localizadores (motor_localizadores.js): un Playwright mínimo sobre la copia real de la pantalla de Recargas
(banco-demo/public/recargas.html, hoy y con el rediseño), y el patio de localizadores.

Toma el código de inicio del árbol de trabajo (estado s06-inicio) y la solución de laboratorio/generar/s06_solucion/
(espejo de rutas; esa carpeta no se publica). Deja una copia en ../para_enviar/.
Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_s6.py
"""
import json, re, shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
SOLUCION = D / 's06_solucion'
PARA_ENVIAR = RAIZ.parent / 'para_enviar'


def leer(ruta):
    return (RAIZ / ruta).read_text(encoding='utf-8')


def cambiar(texto, viejo, nuevo):
    assert viejo in texto, f'No encontré: {viejo[:70]}'
    return texto.replace(viejo, nuevo, 1)


def f(nombre, ruta, rol, codigo=None, ejecuta=True, nota=None):
    c = codigo if codigo is not None else leer(ruta)
    solucion = None
    if rol == 'editar':
        s = SOLUCION / ruta
        assert s.exists(), f'Falta la solución {s}'
        solucion = s.read_text(encoding='utf-8')
    a = {'nombre': nombre, 'ruta': ruta, 'rol': rol, 'codigo': c, 'solucion': solucion, 'ejecuta': ejecuta}
    if nota:
        a['nota'] = nota
    return a


# ---------- La prueba del reto 2, adaptada al laboratorio: los mismos pasos, nombres y mensajes PENDIENTE, sin el inicio de sesión.
SPEC2 = 'tests/retos-s06/reto2-localizadores.spec.ts'
spec2 = leer(SPEC2)
spec2 = cambiar(spec2, ' * Corre con navegador y con el Banco Demo (se inicia solo): npx.cmd playwright test reto2 --project=retos-s06-ui\n',
                ' * En tu equipo corre con navegador y con el Banco Demo (se inicia solo): npx.cmd playwright test reto2 --project=retos-s06-ui\n'
                ' * LABORATORIO: aquí corre contra una copia de la pantalla (hoy y rediseño) con un Playwright simplificado.\n'
                ' * Lo único distinto: no hay inicio de sesión (la pantalla ya abre con la sesión de Ana).\n')
spec2 = cambiar(spec2, "import { usuarios } from '../../src/datos/usuarios';\n", '')
spec2 = cambiar(spec2, "import { abrirConSesion } from '../../src/flujos/sesion';\n", '')
spec2 = cambiar(spec2, 'test.beforeEach(async ({ page, cliente }) => {\n  await abrirConSesion(page, cliente, usuarios.ana);\n});\n',
                '// En tu equipo, antes de cada prueba se abre la sesión de Ana: abrirConSesion(page, cliente, usuarios.ana).\n'
                '// En el laboratorio no hace falta: la copia de la pantalla ya abre con su sesión.\n')
for pendiente in ['PENDIENTE (S6): con el rediseño, ${nombre} no encuentra nada', "test('paso 5 · botonRecargar"]:
    assert pendiente in spec2

# ---------- La pantalla real de Recargas, sin red: el CSS adentro y los scripts sin ejecutar (el laboratorio simula el banco).
pantalla = leer('banco-demo/public/recargas.html')
pantalla = cambiar(pantalla, '<link rel="stylesheet" href="/estilos.css">', '<style>' + leer('banco-demo/public/estilos.css') + '</style>')
pantalla = cambiar(pantalla, '<script src="/comun.js"></script>', '<script type="text/x-laboratorio" data-src="/comun.js"></script>')
assert pantalla.count('<script>') == 1, 'recargas.html cambió: revisa cuántos <script> tiene'
pantalla = pantalla.replace('<script>', '<script type="text/x-laboratorio">')
motor = (D / 'motor_localizadores.js').read_text(encoding='utf-8')
for ident in re.findall(r"(?:saldo|form|operador|numero|valor|boton|formCodigo|codigo|comprobante): '([\w-]+)'", motor):
    assert f'id="{ident}"' in pantalla, f'El banco simulado busca id="{ident}" y recargas.html ya no lo tiene'
assert 'id="plantilla-rediseno"' in pantalla and 'data-testid="saldo-disponible"' in pantalla

RETOS = [
 {'id': 'a1', 'n': 1, 'corto': 'Ambientes', 'capa': 'src/config/', 'titulo': 'Ambientes: local, qa, uat… y producción bloqueada', 'sugerido': 'Empiecen aquí',
  'mision': 'Mañana las mismas pruebas tienen que correr en QA y en UAT. Es lo que hacen en Postman con los <i>environments</i>: '
            'el mismo pedido, otro ambiente. <code>configurarAmbiente()</code> arma la configuración desde un catálogo '
            '(<code>local</code>, <code>qa</code>, <code>uat</code>). El ambiente <code>local</code> ya funciona: es el <b>modelo</b>, en verde. '
            'Faltan los otros dos y tres controles de un banco real. Son funciones puras: la prueba les pasa un objeto con las variables, '
            'como si las hubieras escrito con <code>$env:</code>.',
  'pasos': ['<code>urlDelAmbiente()</code>: <code>qa</code> y <code>uat</code> usan su dirección del catálogo; si la terminal trae <code>URL_BANCO</code>, esa manda.',
            '<code>claveDelAmbiente()</code>: fuera de <code>local</code>, si falta <code>CLAVE_BANCO</code>, falla <b>de inmediato</b> y dice qué hacer. Nunca se inventa una clave.',
            '<code>elegirAmbiente()</code>: solo se aceptan los del catálogo. <code>produccion</code>, <code>PRODUCCION</code>, <code>prod</code> o cualquier otro nombre se bloquean.',
            '<code>congelar()</code>: la configuración queda congelada. Si una prueba hace <code>entorno.usuario = \'luis\'</code>, se lanza un error ahí mismo.'],
  'pistas': ['Paso 1: deja una sola línea para los tres ambientes: <code>return leer(variables, \'URL_BANCO\') ?? catalogoDeAmbientes[nombre].urlBase;</code>',
             'Paso 2: <code>const clave = leer(variables, \'CLAVE_BANCO\');</code> y después <code>if (!clave) throw new Error(...)</code> con el mensaje del <code>TODO</code>; si está, <code>return clave;</code>',
             'Paso 3: <code>if (Object.keys(catalogoDeAmbientes).includes(nombre)) return nombre as NombreDeAmbiente;</code> y si no, <code>throw new Error(...)</code> con el mensaje del <code>TODO</code>. '
             'Es una <b>lista blanca</b>: se dice qué SÍ se permite, en lugar de adivinar cómo van a escribir «producción» (acuérdate del BUG-03 con <code>BLOQUEADO</code>).',
             'Paso 4: <code>return Object.freeze(config);</code>'],
  'archivos': [f('ambientes.ts', 'src/config/ambientes.ts', 'editar'),
               f('entorno.ts', 'src/config/entorno.ts', 'apoyo', ejecuta=False, nota='No corre aquí: lee la terminal (process.env)'),
               f('reto1-ambientes.spec.ts', 'tests/retos-s06/reto1-ambientes.spec.ts', 'pruebas')],
  'orden': ['ambientes.ts', 'reto1-ambientes.spec.ts'],
  'comando': 'npx.cmd playwright test reto1 --project=retos-s06',
  'enEquipo': 'Sin navegador ni banco: 5 en verde. Y pruébalo de verdad: <code>$env:AMBIENTE = \'produccion\'</code> y luego '
              '<code>npx.cmd playwright test --list</code> debe detenerse con el mensaje del paso 3. Con <code>$env:AMBIENTE = \'qa\'</code> (sin clave) '
              'debe pedirte <code>CLAVE_BANCO</code>. Para volver: <code>Remove-Item Env:AMBIENTE</code>.'},
 {'id': 'l2', 'n': 2, 'corto': 'Localizadores', 'capa': 'src/paginas/', 'titulo': 'Localizadores robustos: la página heredada', 'sugerido': 'Después de la pausa',
  'mision': '<code>PaginaRecargasHeredada</code> es el Page Object que nos dejó otro equipo. Hoy funciona. Desarrollo rediseñó la pantalla '
            '(<code>/recargas?rediseno=1</code>) sin cambiar nada de lo que ve el cliente… y sus cinco localizadores se caen. '
            'Cambia cada uno por uno robusto, de lo más alto de la escalera: <b>rol y nombre → etiqueta → texto → test-id pactado</b>. CSS o XPath, nunca primero.',
  'rotulo': 'Simplificado: el Playwright real hace más; lo que pasa aquí, pasa allá.',
  'pasos': ['<code>campoValor</code>: hoy usa una clase CSS (<code>input.campo-valor</code>). El usuario ve la etiqueta «Valor de la recarga».',
            '<code>campoNumero</code>: hoy usa una posición (<code>:nth-child(4)</code>). El usuario ve la etiqueta «Número de celular».',
            '<code>listaOperador</code>: hoy usa un XPath absoluto (<code>/html/body/main/form[1]/select</code>). El usuario ve la etiqueta «Operador».',
            '<code>saldoDisponible</code>: hoy usa un id (<code>#saldo</code>). No tiene nada visible propio: desarrollo pactó <code>data-testid="saldo-disponible"</code>.',
            '<code>botonRecargar</code>: hoy usa texto parcial con CSS (<code>form &gt; button:has-text("Recargar")</code>). Es un botón que se llama «Recargar».'],
  'pistas': ['Pasos 1 a 3: <code>page.getByLabel(\'...\')</code> con el texto exacto de la etiqueta. Y borra el comentario <code>TODO</code> cuando termines.',
             'Paso 4: <code>page.getByTestId(\'saldo-disponible\')</code>.',
             'Paso 5: <code>page.getByRole(\'button\', { name: \'Recargar\' })</code>. Pruébalo antes en el patio: ¿qué pasa si quitas <code>{ name: \'Recargar\' }</code>?',
             'Si una prueba dice <code>encontró 2 elementos</code>, es el <b>modo estricto</b> de Playwright: tu localizador no es único. Si dice <code>Timeout 5000ms exceeded</code>, no encontró nada: revisa el texto de la etiqueta, letra por letra.'],
  'patio': '¿No sabes si tu localizador encuentra uno solo? Pruébalo en el patio, contra las dos versiones de la pantalla, antes de escribirlo.',
  'archivos': [f('PaginaRecargasHeredada.ts', 'src/paginas/heredadas/PaginaRecargasHeredada.ts', 'editar'),
               f('PaginaRecargas.ts', 'src/paginas/PaginaRecargas.ts', 'referencia', ejecuta=False, nota='El modelo: casi todo por etiqueta y rol… menos el saldo'),
               f('PaginaBase.ts', 'src/paginas/PaginaBase.ts', 'apoyo'),
               f('fabricaDeRecargas.ts', 'src/datos/fabricaDeRecargas.ts', 'apoyo'),
               f('recargas.html', 'banco-demo/public/recargas.html', 'apoyo', ejecuta=False, nota='La pantalla: la de hoy arriba; el rediseño, en el <template>'),
               f('reto2-localizadores.spec.ts', SPEC2, 'pruebas', codigo=spec2, nota='Adaptada al laboratorio: sin el inicio de sesión')],
  'orden': ['fabricaDeRecargas.ts', 'PaginaBase.ts', 'PaginaRecargasHeredada.ts', 'reto2-localizadores.spec.ts'],
  'comando': 'npx.cmd playwright test reto2 --project=retos-s06-ui',
  'enEquipo': 'Abre navegador y usa el Banco Demo (se inicia solo): 6 en verde, los 5 pasos y «al final», la recarga completa con la página heredada en las dos versiones.',
  'fixtures': 'function (page) { return { page: page, paginaRecargasHeredada: new PaginaRecargasHeredada(page) }; }',
  'timeout': 30000},
]

PATIO = {
  'intro': 'Escribe un localizador como lo pondrías en un Page Object y toca «Probar». Lo buscamos en las dos versiones de Recargas: '
           'la de hoy y la del rediseño. Un localizador robusto encuentra <b>exactamente 1</b> en las dos. Los ejemplos se pueden tocar.',
  'inicial': "getByRole('button', { name: 'Recargar' })",
  'grupos': [
    {'titulo': 'Los 5 frágiles de la página heredada (funcionan hoy)', 'clase': 'fragil', 'ejemplos': [
      "locator('input.campo-valor')", "locator('main > form:first-of-type > :nth-child(4)')", "locator('xpath=/html/body/main/form[1]/select')",
      "locator('#saldo')", "locator('form > button:has-text(\"Recargar\")')"]},
    {'titulo': 'Los 5 robustos (la escalera)', 'clase': 'robusto', 'ejemplos': [
      "getByLabel('Valor de la recarga')", "getByLabel('Número de celular')", "getByLabel('Operador')",
      "getByTestId('saldo-disponible')", "getByRole('button', { name: 'Recargar' })"]},
    {'titulo': 'Para provocar errores (y leerlos)', 'clase': 'error', 'ejemplos': [
      "getByRole('button')", "getByText('recarga')", "getByLabel('Código de seguridad')", "getByRole('status')",
      "getByText('Recargar', { exact: true })", "getByLabel('valor')"]},
  ],
}

# Los 10 localizadores del reto 2 tienen que estar en el patio tal cual los escribe el repo (si alguien los cambia, avisa).
heredada = leer('src/paginas/heredadas/PaginaRecargasHeredada.ts')
solucion2 = (SOLUCION / 'src/paginas/heredadas/PaginaRecargasHeredada.ts').read_text(encoding='utf-8')
for ej in PATIO['grupos'][0]['ejemplos']:
    assert 'page.' + ej in heredada, f'El frágil {ej} no está en PaginaRecargasHeredada.ts'
for ej in PATIO['grupos'][1]['ejemplos']:
    assert 'page.' + ej in solucion2, f'El robusto {ej} no está en la solución'

tpl = (D / 'plantilla_s6.html').read_text(encoding='utf-8')
logo = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)
sucrase = (D / 'sucrase.min.js').read_text(encoding='utf-8')
data = json.dumps({'retos': RETOS, 'pantalla': pantalla, 'patio': PATIO}, ensure_ascii=False).replace('</', '<\\/')
for marca in ['%%LOGO%%', '/*DATA*/', '/*MOTOR*/', '/*SUCRASE*/']:
    assert tpl.count(marca) == 1, f'La plantilla debe tener una sola marca {marca}'
out = (tpl.replace('%%LOGO%%', logo).replace('/*DATA*/', data)
          .replace('/*MOTOR*/', motor.replace('</script', '<\\/script'))
          .replace('/*SUCRASE*/', sucrase.replace('</script', '<\\/script')))
destino = RAIZ / 'laboratorio' / 'laboratorio_S6.html'
destino.write_text(out, encoding='utf-8')
if PARA_ENVIAR.is_dir():
    shutil.copyfile(destino, PARA_ENVIAR / 'laboratorio_S6.html')
print('laboratorio_S6.html listo', len(out), '(copia en para_enviar)' if PARA_ENVIAR.is_dir() else '')
