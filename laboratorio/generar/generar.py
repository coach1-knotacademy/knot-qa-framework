"""Genera laboratorio/laboratorio_S4.html: los retos de la S4 con sus pruebas, para correr en el navegador sin instalar nada.

Toma el código de las etiquetas s04-inicio (lo que se edita) y s04-solucion (la solución que muestra el laboratorio).
Uso, desde la raíz del repo:  python3 laboratorio/generar/generar.py
"""
import json, subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
RUTAS = {}

def _git(tag, ruta):
    r = subprocess.run(['git', 'show', f'{tag}:{ruta}'], cwd=RAIZ, capture_output=True, text=True, encoding='utf-8')
    return r.stdout if r.returncode == 0 else None

def ini(n): return _git('s04-inicio', RUTAS[n])
def sol(n): return _git('s04-solucion', RUTAS[n]) or ini(n)

USUARIOS = """/**
 * Versión simplificada para el laboratorio: en el repo, la clave sale de src/config/entorno.ts.
 */
export interface Usuario {
  usuario: string;
  clave: string;
  nombre: string;
}

export const usuarios = {
  ana: { usuario: 'ana', clave: '1234', nombre: 'Ana Pérez' },
  luis: { usuario: 'luis', clave: '1234', nombre: 'Luis Gómez' },
};
"""
CUENTA = """/** Una cuenta, como la entrega el banco: GET /api/cuentas (en el repo vive en src/api/ClienteBanco.ts). */
export interface Cuenta {
  numero: string;
  tipo: string;
  saldo: number;
}
"""

def f(nombre, ruta, rol, codigo=None, solucion=None, ejecuta=True):
    RUTAS[nombre] = ruta.split(' ')[0]
    c = codigo if codigo is not None else ini(nombre)
    return {'nombre': nombre, 'ruta': ruta, 'rol': rol, 'codigo': c,
            'solucion': (solucion if solucion is not None else (sol(nombre) if rol == 'editar' else None)),
            'ejecuta': ejecuta}

RETOS = [
 {'id': 'r2', 'n': 2, 'letra': 'O', 'titulo': 'Llegó la cuenta Nómina', 'sugerido': 'Empiecen aquí',
  'mision': 'El banco lanzó la cuenta <b>Nómina</b>, que no cobra por transferir. Hay que agregarla <b>sin tocar</b> <code>calcularCosto</code>, que ya funciona para Ahorros y Corriente. Si la abren, hay que volver a probar todo.',
  'pasos': ['En <code>reglasDeCosto.ts</code>, completa <code>ReglaCorriente.calcular</code>: 4x1000 más $2.000.',
            'Completa <code>RegistroDeReglas.costo</code>: busca la regla del tipo de cuenta; si no existe, lanza el error.',
            'Crea <code>ReglaNomina</code> (copia <code>ReglaAhorros</code>) y regístrala en <code>reglasDelBanco()</code>.'],
  'pistas': ['Paso 1: mira la línea de Corriente en <code>calcularCosto.ts</code>. Es la misma cuenta: <code>return cuatroPorMil(monto) + 2_000;</code> Y borra la línea del <code>throw</code>.',
             'Paso 2: <code>const regla = this.reglas.get(tipoCuenta);</code> Después, <code>if (!regla) { throw new Error(`Tipo de cuenta desconocido: ${tipoCuenta}`); }</code> y al final <code>return regla.calcular(monto);</code>',
             'Paso 3: copia las 6 líneas de <code>ReglaAhorros</code>, cambia el nombre a <code>ReglaNomina</code>, el tipo a <code>\'Nómina\'</code> (con tilde) y haz que <code>calcular</code> devuelva <code>0</code>. Luego agrega <code>.registrar(new ReglaNomina())</code>.'],
  'archivos': [f('reglasDeCosto.ts', 'src/legado/ocp/reglasDeCosto.ts', 'editar'),
               f('calcularCosto.ts', 'src/legado/ocp/calcularCosto.ts', 'antes'),
               f('reto2-ocp.spec.ts', 'tests/retos-s04/reto2-ocp.spec.ts', 'pruebas')],
  'orden': ['calcularCosto.ts', 'reglasDeCosto.ts', 'reto2-ocp.spec.ts']},
 {'id': 'r1', 'n': 1, 'letra': 'S', 'titulo': 'Casos fantasma en el CSV', 'sugerido': 'Segundo',
  'mision': 'Con un CSV guardado en Windows aparecen <b>casos fantasma</b> y una columna <code>monto</code> que no se encuentra. Además, la bitácora debe dejar la <b>hora exacta</b> de cada paso, como evidencia. <code>AyudanteTodo</code> hacía todo; ahora cada tarea tiene su archivo.',
  'pasos': ['En <code>LectorDeCasos.ts</code>, lleva la lógica de <code>AyudanteTodo.leerCasosCsv</code>, partiendo las líneas con o sin <code>\\r</code> y quitando las vacías.',
            'En <code>Bitacora.ts</code>, arma la línea con la hora de <code>this.reloj()</code> y guárdala en <code>this.registro</code>.'],
  'pistas': ['Abre <code>AyudanteTodo.ts</code> (pestaña «antes») y copia el cuerpo de <code>leerCasosCsv</code> desde <code>const [encabezado…</code> hasta el <code>return</code>. No copies <code>fs.readFileSync</code>: aquí el texto ya llega como parámetro.',
             'El defecto está en <code>texto.split(\'\\n\')</code>. Cámbialo por <code>const lineas = texto.split(/\\r?\\n/).filter((linea) =&gt; linea.trim() !== \'\');</code> y luego <code>const [encabezado, ...filas] = lineas;</code>',
             'Bitácora: <code>const linea = `[${this.reloj().toISOString()}] ${mensaje}`;</code> y <code>this.registro.push(linea);</code> Borra el <code>throw</code>.'],
  'archivos': [f('LectorDeCasos.ts', 'src/legado/srp/LectorDeCasos.ts', 'editar'),
               f('Bitacora.ts', 'src/legado/srp/Bitacora.ts', 'editar'),
               f('AyudanteTodo.ts', 'src/legado/srp/AyudanteTodo.ts', 'referencia', ejecuta=False),
               f('reto1-srp.spec.ts', 'tests/retos-s04/reto1-srp.spec.ts', 'pruebas')],
  'orden': ['LectorDeCasos.ts', 'Bitacora.ts', 'reto1-srp.spec.ts']},
 {'id': 'r3', 'n': 3, 'letra': 'L', 'titulo': 'La consulta que se hace pasar por transferencia', 'sugerido': 'Extra',
  'mision': '<code>PaginaConsulta</code> hereda de <code>PaginaTransferencia</code> solo para reutilizar <code>saldoDe</code>, y su <code>transferir()</code> lanza error. Si la suite nocturna le pide transferir a todas, revienta.',
  'pasos': ['Mueve <code>saldoDe()</code> a <code>PaginaDeCuentas</code>.',
            'Haz que las dos páginas hereden de <code>PaginaDeCuentas</code> y borra el constructor de <code>PaginaTransferencia</code>.',
            'Borra el <code>transferir()</code> de <code>PaginaConsulta</code>.'],
  'pistas': ['Corta las 3 líneas de <code>saldoDe</code> de <code>PaginaTransferencia</code> y pégalas dentro de <code>PaginaDeCuentas</code>, debajo de <code>abstract abrir()</code>.',
             '<code>export class PaginaTransferencia extends PaginaDeCuentas {</code> y <code>export class PaginaConsulta extends PaginaDeCuentas {</code>',
             'Si queda una llave <code>}</code> de más o de menos, el error dice la línea: <code>Unexpected token (37:7)</code> es línea 37, columna 7.'],
  'archivos': [f('paginasDeCuenta.ts', 'src/legado/lsp/paginasDeCuenta.ts', 'editar'),
               f('navegador.ts', 'src/legado/navegador.ts', 'apoyo'),
               f('NavegadorFalso.ts', 'tests/retos-s04/dobles/NavegadorFalso.ts', 'apoyo'),
               f('reto3-lsp.spec.ts', 'tests/retos-s04/reto3-lsp.spec.ts', 'pruebas')],
  'orden': ['navegador.ts', 'NavegadorFalso.ts', 'paginasDeCuenta.ts', 'reto3-lsp.spec.ts']},
 {'id': 'r4', 'n': 4, 'letra': 'I', 'titulo': 'Cinco métodos que dicen «No aplica»', 'sugerido': 'Extra',
  'mision': '<code>PaginaSaldos</code> solo sabe abrir, leer saldos y cerrar sesión, pero la interfaz gigante <code>PaginaDelBanco</code> la obliga a tener 8 métodos. Cinco responden «No aplica».',
  'pasos': ['En <code>capacidades.ts</code>, crea <code>ConsultaSaldos</code> y <code>CierraSesion</code>, con el estilo de <code>SeAbre</code>.',
            'En <code>PaginaSaldos.ts</code>, cambia <code>implements PaginaDelBanco</code> por <code>implements SeAbre, ConsultaSaldos, CierraSesion</code>.',
            'Borra los 5 métodos que lanzan «No aplica».'],
  'pistas': ['<code>export interface ConsultaSaldos { saldoDe(cuenta: string): Promise&lt;string&gt;; }</code>',
             'Si solo borras los métodos y dejas <code>implements PaginaDelBanco</code>, las pruebas pasan, pero el chequeo de tipos falla. Ese es el «verde que miente».',
             'En el repo, el import también cambia: <code>import { SeAbre, ConsultaSaldos, CierraSesion } from \'./capacidades\';</code>'],
  'archivos': [f('PaginaSaldos.ts', 'src/legado/isp/PaginaSaldos.ts', 'editar'),
               f('capacidades.ts', 'src/legado/isp/capacidades.ts', 'editar'),
               f('PaginaDelBanco.ts', 'src/legado/isp/PaginaDelBanco.ts', 'antes'),
               f('navegador.ts', 'src/legado/navegador.ts', 'apoyo'),
               f('NavegadorFalso.ts', 'tests/retos-s04/dobles/NavegadorFalso.ts', 'apoyo'),
               f('reto4-isp.spec.ts', 'tests/retos-s04/reto4-isp.spec.ts', 'pruebas')],
  'orden': ['navegador.ts', 'NavegadorFalso.ts', 'PaginaDelBanco.ts', 'capacidades.ts', 'PaginaSaldos.ts', 'reto4-isp.spec.ts']},
 {'id': 'r5', 'n': 5, 'letra': 'D', 'titulo': 'Probar sin el banco', 'sugerido': 'Extra',
  'mision': 'El ambiente se cayó, pero el resumen de saldos se tiene que probar. <code>ResumenAcoplado</code> crea su propio cliente HTTP por dentro: sin banco, <code>fetch failed</code>. <code>ResumenDeCuentas</code> recibe el cliente, y la prueba le pasa uno falso.',
  'pasos': ['En <code>Cliente.ts</code>, agrega <code>cuentas(): Promise&lt;Cuenta[]&gt;;</code> a la interfaz.',
            'En <code>ResumenDeCuentas.ts</code>, haz la suma usando <code>this.cliente</code>, sin <code>new</code>.',
            'En <code>ClienteFalso.ts</code>, anota la sesión y devuelve las cuentas preparadas.'],
  'pistas': ['Mira <code>ResumenAcoplado.ts</code>: son las mismas 3 líneas, pero con <code>this.cliente</code> en vez de <code>cliente</code>, y sin la línea del <code>new</code>.',
             '<code>await this.cliente.iniciarSesion(usuario);</code> <code>const cuentas = await this.cliente.cuentas();</code> <code>return cuentas.reduce((total, cuenta) =&gt; total + cuenta.saldo, 0);</code>',
             'ClienteFalso: <code>this.sesiones.push(usuario.usuario);</code> y <code>return this.cuentasPreparadas;</code>'],
  'archivos': [f('ResumenDeCuentas.ts', 'src/legado/dip/ResumenDeCuentas.ts', 'editar'),
               f('Cliente.ts', 'src/legado/dip/Cliente.ts', 'editar'),
               f('ClienteFalso.ts', 'tests/retos-s04/dobles/ClienteFalso.ts', 'editar'),
               f('ResumenAcoplado.ts', 'src/legado/dip/ResumenAcoplado.ts', 'referencia', ejecuta=False),
               f('usuarios.ts', 'src/datos/usuarios.ts', 'apoyo', codigo=USUARIOS),
               f('ClienteBanco.ts', 'src/api/ClienteBanco.ts (solo Cuenta)', 'apoyo', codigo=CUENTA),
               f('reto5-dip.spec.ts', 'tests/retos-s04/reto5-dip.spec.ts', 'pruebas')],
  'orden': ['ClienteBanco.ts', 'usuarios.ts', 'Cliente.ts', 'ClienteFalso.ts', 'ResumenDeCuentas.ts', 'reto5-dip.spec.ts']},
]

sucrase = (D / 'sucrase.min.js').read_text(encoding='utf-8')
data = json.dumps(RETOS, ensure_ascii=False).replace('</', '<\\/')
tpl = (D / 'plantilla.html').read_text(encoding='utf-8')
out = tpl.replace('/*SUCRASE*/', sucrase.replace('</script', '<\\/script')).replace('/*DATA*/', data)
(RAIZ / 'laboratorio' / 'laboratorio_S4.html').write_text(out, encoding='utf-8')
print('ok', len(out))
