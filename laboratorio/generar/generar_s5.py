"""Genera laboratorio/laboratorio_S5.html: los retos de la S5 con sus pruebas, para correr en el navegador sin instalar nada.

Usa la misma plantilla y el mismo motor que el de la S4. Toma el código de las etiquetas s05-inicio
(lo que se edita) y s05-solucion (la solución que muestra el laboratorio).
Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_s5.py
"""
import json, subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
RUTAS = {}

def _git(tag, ruta):
    r = subprocess.run(['git', 'show', f'{tag}:{ruta}'], cwd=RAIZ, capture_output=True, text=True, encoding='utf-8')
    return r.stdout if r.returncode == 0 else None

def ini(n): return _git('s05-inicio', RUTAS[n])
def sol(n): return _git('s05-solucion', RUTAS[n]) or ini(n)

USUARIOS = """/**
 * Versión simplificada para el laboratorio: en el repo, este archivo también tiene los usuarios
 * y la clave sale de src/config/entorno.ts.
 */
export const cuentas = {
  ahorros: { numero: '1000000001', tipo: 'Ahorros', saldoInicial: 1_500_000 },
  corriente: { numero: '1000000002', tipo: 'Corriente', saldoInicial: 250_000 },
  /** Una cuenta de otro cliente, para recibir transferencias. */
  destino: '2000000001',
};
"""

def f(nombre, ruta, rol, codigo=None, ejecuta=True):
    RUTAS[nombre] = ruta.split(' ')[0]
    c = codigo if codigo is not None else ini(nombre)
    assert c, f'No encontré {ruta} en s05-inicio'
    return {'nombre': nombre, 'ruta': ruta, 'rol': rol, 'codigo': c,
            'solucion': sol(nombre) if rol == 'editar' else None, 'ejecuta': ejecuta}

RETOS = [
 {'id': 'f1', 'n': 1, 'letra': 'F', 'titulo': 'La fábrica de transferencias', 'sugerido': 'Empiecen aquí',
  'mision': 'Hoy cada prueba de transferencias escribe a mano cuentas y montos. Si el banco cambia el monto mínimo, hay que corregir 30 pruebas. '
            'Vamos a armar una <b>fábrica</b>: un solo lugar que entrega transferencias listas, con nombres de negocio. '
            'El modelo es la fábrica de recargas (pestaña «modelo»), que ya está completa.',
  'pasos': ['<code>desdeCorriente()</code>: la misma transferencia de <code>valida()</code>, pero saliendo de la cuenta Corriente.',
            '<code>alMontoMinimo()</code>: por exactamente $1.000.',
            '<code>aLaMismaCuenta()</code>: el destino es la misma cuenta de origen.'],
  'pistas': ['Paso 1: mira <code>grande()</code> en la pestaña modelo. Es la misma forma: <code>return fabricaDeTransferencias.valida({ origen: cuentas.corriente.numero, ...cambios });</code> Y borra la línea del <code>throw</code>.',
             'Paso 2: copia lo que hiciste en el paso 1 y cambia <code>origen: cuentas.corriente.numero</code> por <code>monto: 1_000</code>.',
             'Paso 3: primero <code>const base = fabricaDeTransferencias.valida(cambios);</code> y después <code>return { ...base, destino: base.origen };</code> Los tres puntos copian todo lo de <code>base</code>.'],
  'archivos': [f('fabricaDeTransferencias.ts', 'src/datos/fabricaDeTransferencias.ts', 'editar'),
               f('fabricaDeRecargas.ts', 'src/datos/fabricaDeRecargas.ts', 'referencia', ejecuta=False),
               f('usuarios.ts', 'src/datos/usuarios.ts (solo las cuentas)', 'apoyo', codigo=USUARIOS),
               f('reto1-fabrica.spec.ts', 'tests/retos-s05/reto1-fabrica.spec.ts', 'pruebas')],
  'orden': ['usuarios.ts', 'fabricaDeTransferencias.ts', 'reto1-fabrica.spec.ts']},
 {'id': 'f2', 'n': 2, 'letra': 'SP', 'titulo': 'Ana recarga su celular (Screenplay)', 'sugerido': 'Extra',
  'mision': 'La prueba se escribe como un caso manual: <i>Ana intenta recargar $20.000 al 3109876543; su saldo queda en $80.000</i>. '
            'Falta la <b>tarea</b> <code>Recargar</code>: el paso de negocio que por dentro usa la billetera de Ana. '
            'La billetera de la prueba es falsa y vive en memoria: no hay banco ni navegador.',
  'pasos': ['Arma la recarga con la fábrica: <code>fabricaDeRecargas.valida({ numero: this.numero, monto: this.monto })</code>.',
            'Pídesela a la billetera de Ana: <code>await actor.usa(UsarLaBilletera).billetera.recargar(recarga)</code>.',
            'Si el estado no es 201, lanza el error con el mensaje de la billetera.'],
  'pistas': ['Mira <code>SaldoDisponible.ts</code>: también usa <code>actor.usa(UsarLaBilletera).billetera</code>. Tu tarea hace lo mismo, pero llama a <code>recargar</code>.',
             '<code>const recarga = fabricaDeRecargas.valida({ numero: this.numero, monto: this.monto });</code> y en la línea siguiente <code>const resultado = await actor.usa(UsarLaBilletera).billetera.recargar(recarga);</code>',
             '<code>if (resultado.estado !== 201) throw new Error(`${actor.nombre} no pudo recargar: ${resultado.error}`);</code> Y borra el <code>throw</code> que dice PENDIENTE.'],
  'archivos': [f('Recargar.ts', 'src/screenplay/billetera/Recargar.ts', 'editar'),
               f('SaldoDisponible.ts', 'src/screenplay/billetera/SaldoDisponible.ts', 'referencia'),
               f('Actor.ts', 'src/screenplay/Actor.ts', 'apoyo'),
               f('UsarLaBilletera.ts', 'src/screenplay/billetera/UsarLaBilletera.ts', 'apoyo'),
               f('BilleteraFalsa.ts', 'tests/retos-s05/dobles/BilleteraFalsa.ts', 'apoyo'),
               f('fabricaDeRecargas.ts', 'src/datos/fabricaDeRecargas.ts', 'apoyo'),
               f('reto2-screenplay.spec.ts', 'tests/retos-s05/reto2-screenplay.spec.ts', 'pruebas')],
  'orden': ['fabricaDeRecargas.ts', 'Actor.ts', 'UsarLaBilletera.ts', 'SaldoDisponible.ts', 'BilleteraFalsa.ts', 'Recargar.ts', 'reto2-screenplay.spec.ts']},
]

tpl = (D / 'plantilla.html').read_text(encoding='utf-8')
CAMBIOS = [
    ('<title>Laboratorio S4 SOLID</title>', '<title>Laboratorio S5 Patrones</title>'),
    ('Bootcamp QA · Knot Academy × Accenture · S4 · SOLID', 'Bootcamp QA · Knot Academy × Accenture · S5 · Patrones de diseño'),
    ('Laboratorio S4: arregla código heredado sin instalar nada', 'Laboratorio S5: una fábrica y una tarea, sin instalar nada'),
    ('<li><span>Elige un reto. La meta de la sala es <b>uno en verde</b>; empiecen por el 2.</span></li>',
     '<li><span>Empiecen por el reto 1. <b>Cada paso tiene su propia prueba</b>: el verde avanza de a uno.</span></li>'),
    ('<li><span>Dilo como tester: ¿qué falla y cuándo? Después, busquen la línea.</span></li>',
     '<li><span>Antes de correr, predigan: ¿cuántas pruebas van a pasar? Dígalo en el chat.</span></li>'),
    ('Playwright no revisa tipos; en los retos 4 y 5, el «chequeo de tipos» imita lo que haría <code>npm run tipos</code>.',
     'Si te pierdes, «Restaurar archivo» lo deja como al principio y «Ver la solución» muestra la respuesta.'),
    ("referencia: 'antes · solo leer'", "referencia: 'modelo · solo leer'"),
    ('S4 · principios SOLID', 'S5 · patrones de diseño'),
    ("'s4lab:'", "'s5lab:'"),
    ('--project=unidad', '--project=retos-s05'),
]
for viejo, nuevo in CAMBIOS:
    assert viejo in tpl, f'No encontré en la plantilla: {viejo[:50]}'
    tpl = tpl.replace(viejo, nuevo)

sucrase = (D / 'sucrase.min.js').read_text(encoding='utf-8')
data = json.dumps(RETOS, ensure_ascii=False).replace('</', '<\\/')
out = tpl.replace('/*SUCRASE*/', sucrase.replace('</script', '<\\/script')).replace('/*DATA*/', data)
(RAIZ / 'laboratorio' / 'laboratorio_S5.html').write_text(out, encoding='utf-8')
print('laboratorio_S5.html listo')
