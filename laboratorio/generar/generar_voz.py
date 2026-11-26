"""Genera laboratorio/voz.html: el kit de voz para participantes (agente de voz con IA, cobranza amable ficticia).

El laboratorio corre en el navegador, sin instalar nada: elegir una llamada, escucharla, ver (y editar) la transcripción
y correr las aserciones. El oráculo de la página es EXACTAMENTE src/voz/oraculo.ts: este generador lo compila a JS con el
TypeScript del repo (por eso necesita Node y node_modules) y lo pega en la página. Los datos salen de voz/guiones.json y
voz/transcripciones.json (los deja `npm run voz:generar`).

En Pages se publica como voz.html, con los audios en voz/audios/ del sitio (rutas relativas). La copia de ../para_enviar/voz.html
lleva los audios con la dirección completa de Pages, para que funcione con doble clic. No carga nada de internet salvo las
fuentes de Google (y si no cargan se usan las del sistema). El CSS y los tokens son los de proyecto.html (generar_proyecto.py).

Uso, desde la raíz del repo:  python3 laboratorio/generar/generar_voz.py
"""
import html, json, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
D = Path(__file__).parent
sys.path.insert(0, str(D))
from fichas_s6 import PAGES, a_html  # noqa: E402

PARA_ENVIAR = RAIZ.parent / 'para_enviar'
e = lambda t: html.escape(str(t), quote=True)

# El visual Knot: el mismo CSS de proyecto.html y el logo de la plantilla.
CSS_BASE = re.search(r'^CSS = """(.*?)"""', (D / 'generar_proyecto.py').read_text(encoding='utf-8'), re.S | re.M).group(1)
LOGO = re.search(r'<img src="(data:image/png;base64,[^"]+)"', (D / 'plantilla.html').read_text(encoding='utf-8')).group(1)

GUIONES = json.loads((RAIZ / 'voz' / 'guiones.json').read_text(encoding='utf-8'))
TRANSCRIPCIONES = json.loads((RAIZ / 'voz' / 'transcripciones.json').read_text(encoding='utf-8'))
for g in GUIONES['llamadas']:
    assert g['id'] in TRANSCRIPCIONES['llamadas'], f"{g['id']} no está en voz/transcripciones.json: corre npm run voz:generar"
    assert (RAIZ / 'voz' / 'audios' / g['audio']).is_file(), f"falta voz/audios/{g['audio']}: corre npm run voz:generar"


def oraculo_js():
    """src/voz/oraculo.ts → JS, con el compilador del repo. Mismo algoritmo que las pruebas."""
    codigo = r"""
const ts = require('typescript'); const fs = require('fs');
const fuente = fs.readFileSync(process.argv[1], 'utf8');
process.stdout.write(ts.transpileModule(fuente, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 } }).outputText);
"""
    salida = subprocess.run(['node', '-e', codigo, str(RAIZ / 'src' / 'voz' / 'oraculo.ts')], cwd=RAIZ, capture_output=True, text=True, check=True).stdout
    assert 'function revisarLlamada' in salida and '</script' not in salida.lower()
    return 'var Oraculo = (function () { var exports = {}; var module = { exports: exports };\n' + salida + '\nreturn module.exports; })();'


CSS_VOZ = """
.llamadas { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:10px 0 4px; }
@media (max-width:820px) { .llamadas { grid-template-columns:minmax(0,1fr) minmax(0,1fr); } }
@media (max-width:480px) { .llamadas { grid-template-columns:minmax(0,1fr); } }
.llamadas button { text-align:left; margin:0; padding:10px 12px; border-radius:12px; box-shadow:3px 3px 0 var(--ink); min-width:0; }
.llamadas button b { display:block; font:400 16px var(--f-display); color:var(--morado-osc); }
.llamadas button span { display:block; font-weight:700; font-size:14px; }
.llamadas button[aria-pressed="true"] { background:var(--neon); }
.llamadas button[aria-pressed="true"] b { color:var(--ink); }
audio { width:100%; margin:6px 0; }
.estado-audio { font-size:14px; color:var(--muted); min-height:1.4em; }
.estado-audio.mal { color:var(--bad); font-weight:800; }
textarea.transcripcion { width:100%; min-height:220px; font:14px/1.55 var(--f-mono); border:2px solid var(--ink); border-radius:10px; padding:10px; background:var(--surface); color:var(--ink); resize:vertical; }
.controles { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:10px 0; }
.controles label { font-weight:800; display:flex; align-items:center; gap:6px; }
.controles input[type=number] { width:5.2em; font:700 16px var(--f-body); border:2px solid var(--ink); border-radius:8px; padding:5px 6px; background:var(--surface); color:var(--ink); }
ul.aserciones { list-style:none; padding:0; margin:8px 0; }
ul.aserciones li { display:grid; grid-template-columns:2em minmax(0,1fr); gap:6px; padding:8px 0; border-top:2px solid var(--ink); }
ul.aserciones li .i { font:400 20px var(--f-display); }
ul.aserciones li.pasa .i { color:var(--ok); } ul.aserciones li.falla .i { color:var(--bad); }
ul.aserciones li.falla { background:#fff1ec; }
ul.aserciones .det { color:var(--muted); font-size:14px; display:block; }
.resumen { font:400 20px var(--f-display); margin:6px 0; }
.resumen.verde { color:var(--ok); } .resumen.rojo { color:var(--bad); }
.diff { font:14px/1.9 var(--f-mono); background:var(--surface); border:2px solid var(--ink); border-radius:10px; padding:10px; overflow-wrap:anywhere; }
.diff .s { background:var(--peach); border-radius:4px; padding:0 3px; } .diff .b { background:#ffd0d0; text-decoration:line-through; border-radius:4px; padding:0 3px; }
.diff .n { background:var(--lime); border-radius:4px; padding:0 3px; }
.diff .s, .diff .b, .diff .n, .muestras span { color:var(--ink); }
.muestras { font:13px/1.9 var(--f-mono); }
.muestras span { border-radius:4px; padding:1px 6px; } .muestras .s { background:var(--peach); } .muestras .b { background:#ffd0d0; text-decoration:line-through; } .muestras .n { background:var(--lime); }
ul.aserciones li.falla { padding:8px 10px; } ul.aserciones li.falla .det { color:var(--ink); }
.leyenda { font-size:13px; color:var(--muted); }
details.guion { margin:8px 0; } details.guion summary { cursor:pointer; font-weight:800; }
.turno { margin:4px 0; } .turno b { color:var(--morado-osc); }
.chip.rojo { background:var(--peach); }
.sr, .sr-only { position:absolute; left:-9999px; width:1px; height:1px; overflow:hidden; }
"""

JS_LAB = r"""
(function () {
  var DATOS = JSON.parse(document.getElementById('datos-voz').textContent);
  var BASE = document.body.getAttribute('data-audios');
  // Abierta desde el repo (laboratorio/voz.html), los audios están en ../voz/audios/: plan B sin internet.
  var ALTERNA = document.body.getAttribute('data-audios-alterna') || '', usandoAlterna = false;
  if (ALTERNA && /\/laboratorio\/voz\.html$/.test(location.pathname)) { BASE = ALTERNA; ALTERNA = ''; }
  var POLITICA = DATOS.guiones.politica, LLAMADAS = DATOS.guiones.llamadas, TRANS = DATOS.transcripciones;
  var NOMBRE_INT = { promesa_de_pago: 'promesa de pago', ya_pago: 'ya pagó', no_reconoce_la_deuda: 'no reconoce la deuda', pide_una_persona: 'pide una persona', sin_intencion_clara: 'sin intención clara' };
  var $ = function (id) { return document.getElementById(id); };
  var actual = null;

  function aTexto(turnos) {
    return turnos.map(function (t) { return (t.hablante === 'cliente' ? 'Cliente: ' : t.hablante === 'agente' ? 'Agente: ' : '') + t.texto; }).join('\n');
  }
  function desdeTexto(texto) {
    var turnos = [];
    texto.split(/\r?\n/).forEach(function (linea) {
      var m = linea.match(/^\s*(agente|cliente)\s*:\s*(.*)$/i);
      if (m) turnos.push({ hablante: m[1].toLowerCase(), texto: m[2] });
      else if (linea.trim() && turnos.length) turnos[turnos.length - 1].texto += ' ' + linea.trim();
      else if (linea.trim()) turnos.push({ hablante: 'desconocido', texto: linea.trim() });
    });
    return { llamada: actual.id, motor: TRANS.motor, texto: turnos.map(function (t) { return t.texto; }).join(' '), turnos: turnos };
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pesos(n) { return n === null || n === undefined ? 'ninguno' : String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' pesos'; }
  function pct(x) { return (Math.round(x * 1000) / 10).toString().replace('.', ',') + ' %'; }

  function elegir(id) {
    actual = LLAMADAS.filter(function (g) { return g.id === id; })[0];
    document.querySelectorAll('.llamadas button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-id') === id)); });
    var audio = $('audio');
    $('estado-audio').textContent = 'Cargando el audio…'; $('estado-audio').className = 'estado-audio';
    usandoAlterna = false;
    audio.src = BASE + actual.audio;
    audio.load();
    $('titulo-llamada').textContent = actual.id + ' · ' + actual.caso;
    $('guion').innerHTML = actual.turnos.map(function (t) { return '<p class="turno"><b>' + (t.hablante === 'agente' ? 'Agente' : 'Cliente') + ':</b> ' + esc(t.texto) + '</p>'; }).join('');
    $('esperado').innerHTML = 'Esperado: intención <b>' + esc(NOMBRE_INT[actual.esperado.intencion]) + '</b> · monto <b>' + esc(pesos(actual.esperado.monto)) + '</b> · fecha <b>' + esc(actual.esperado.fecha || 'ninguna') + '</b> · acuerdo de pago <b>' + (actual.esperado.ofrece_acuerdo ? 'sí' : 'no') + '</b>';
    restaurar();
  }
  function restaurar() { $('transcripcion').value = aTexto(TRANS.llamadas[actual.id].turnos); correr(); }

  function correr() {
    var umbral = Math.max(0, Number(String($('umbral').value).replace(',', '.')) || 0) / 100;
    var t = desdeTexto($('transcripcion').value);
    var inf = Oraculo.revisarLlamada(actual, t, POLITICA, umbral);
    var esp = actual.esperado, filas = [];
    function fila(pasa, que, detalle) { filas.push({ pasa: pasa, que: que, detalle: detalle }); }
    inf.frases.forEach(function (f) {
      if (f.id === 'acuerdo') return;
      if (esp.frases.indexOf(f.id) < 0) return;
      fila(f.dicha, 'El agente ' + f.nombre, f.dicha ? 'Encontrada en lo que dijo el agente.' : 'No aparece ninguna de: «' + POLITICA.frases.filter(function (x) { return x.id === f.id; })[0].alternativas.join('», «') + '».');
    });
    fila(inf.prohibidas.length === 0, 'Sin amenazas ni lenguaje ofensivo', inf.prohibidas.length ? 'Dijo: «' + inf.prohibidas.join('», «') + '».' : 'Ninguna palabra de la lista de prohibidas.');
    fila(inf.ofreceAcuerdo === esp.ofrece_acuerdo, esp.ofrece_acuerdo ? 'Ofrece un acuerdo de pago' : 'No ofrece acuerdo (no corresponde en este caso)', 'Esperado: ' + (esp.ofrece_acuerdo ? 'sí' : 'no') + ' · obtenido: ' + (inf.ofreceAcuerdo ? 'sí' : 'no') + '.');
    fila(inf.intencion.intencion === esp.intencion, 'La intención del cliente es «' + NOMBRE_INT[esp.intencion] + '»', 'Obtenida: «' + NOMBRE_INT[inf.intencion.intencion] + '»' + (inf.intencion.evidencia ? ' · evidencia: «' + inf.intencion.evidencia + '»' : '') + '.');
    fila(inf.datos.monto === esp.monto, 'El monto es ' + pesos(esp.monto), 'Obtenido: ' + pesos(inf.datos.monto) + '.');
    fila(inf.datos.fecha === esp.fecha, 'La fecha es «' + (esp.fecha || 'ninguna') + '»', 'Obtenida: «' + (inf.datos.fecha || 'ninguna') + '».');
    var w = inf.wer;
    fila(w.valor <= umbral, 'WER de máximo ' + pct(umbral), 'WER: ' + pct(w.valor) + ' (' + w.sustituciones + ' cambiadas, ' + w.borrados + ' borradas, ' + w.inserciones + ' de más, sobre ' + w.palabrasDelGuion + ' palabras del guion).');
    var verdes = filas.filter(function (f) { return f.pasa; }).length;
    $('resultados').innerHTML = filas.map(function (f) {
      return '<li class="' + (f.pasa ? 'pasa' : 'falla') + '"><span class="i" aria-hidden="true">' + (f.pasa ? '✓' : '✗') + '</span><span><b>' + esc(f.que) + '</b><span class="det">' + esc(f.detalle) + '</span></span><span class="sr">' + (f.pasa ? ' pasa' : ' falla') + '</span></li>';
    }).join('');
    var r = $('resumen');
    r.textContent = verdes === filas.length ? '✓ ' + filas.length + ' de ' + filas.length + ' en verde' : '✗ ' + (filas.length - verdes) + ' en rojo · ' + verdes + ' de ' + filas.length + ' en verde';
    r.className = 'resumen ' + (verdes === filas.length ? 'verde' : 'rojo');
    $('diff').innerHTML = w.alineacion.map(function (p) {
      if (p.tipo === 'igual') return esc(p.guion);
      if (p.tipo === 'sustitucion') return '<span class="s" title="cambiada">' + esc(p.guion) + '→' + esc(p.transcripcion) + '</span>';
      if (p.tipo === 'borrado') return '<span class="b" title="borrada">' + esc(p.guion) + '</span>';
      return '<span class="n" title="de más">+' + esc(p.transcripcion) + '</span>';
    }).join(' ') || '(vacío)';
  }

  $('audio').addEventListener('loadedmetadata', function () {
    var s = Math.round($('audio').duration);
    $('estado-audio').textContent = 'Audio sintético listo · ' + s + ' s · ' + actual.audio;
  });
  $('audio').addEventListener('error', function () {
    if (ALTERNA && !usandoAlterna) { usandoAlterna = true; $('audio').src = ALTERNA + actual.audio; $('audio').load(); return; }
    var el = $('estado-audio');
    el.textContent = 'El audio no cargó. Ábrelo desde la página publicada del bootcamp; la transcripción y las aserciones sí funcionan.';
    el.className = 'estado-audio mal';
  });
  document.querySelectorAll('.llamadas button').forEach(function (b) { b.addEventListener('click', function () { elegir(b.getAttribute('data-id')); }); });
  $('correr').addEventListener('click', correr);
  $('restaurar').addEventListener('click', restaurar);
  $('umbral').addEventListener('change', correr);
  elegir(LLAMADAS[0].id);
})();
"""

NOMBRE_INT = {'promesa_de_pago': 'promesa de pago', 'ya_pago': 'ya pagó', 'no_reconoce_la_deuda': 'no reconoce la deuda',
              'pide_una_persona': 'pide una persona', 'sin_intencion_clara': 'sin intención clara'}

PRUEBA_TS = """for (const g of guionesDeVoz) {
  test(`${g.id} · ${g.caso}`, async () => {
    const lucia = Actor.llamado('Lucía').puede(UsarElAgenteDeVoz.con(new TranscriptorDeArchivo()));

    await test.step(`Dado la llamada «${g.id}» transcrita del audio sintético`, async () => {
      await lucia.intenta(EscucharLaLlamada.numero(g.id));                 // TAREA
    });
    await test.step('Cuando el oráculo revisa la transcripción contra el guion', async () => {
      informe = await lucia.pregunta(CumplimientoDelGuion.contra(g));      // PREGUNTA
    });
    await test.step('Entonces el agente dice las frases obligatorias…', async () => {
      expect(informe.faltantes).toEqual([]);
      expect(informe.prohibidas).toEqual([]);
    });
    await test.step('Y la intención del cliente es…', async () => {
      expect(await lucia.pregunta(IntencionDelCliente.enLaLlamada())).toBe(g.esperado.intencion);
      expect(informe.datos).toEqual({ monto: g.esperado.monto, fecha: g.esperado.fecha });
    });
    await test.step('Y el WER contra el guion es de máximo 15 %', async () => {
      expect(informe.wer.valor).toBeLessThanOrEqual(0.15);                // umbral, nunca igualdad exacta
    });
  });
}"""

TU_TRANSCRIPTOR = """// src/screenplay/voz/TranscriptorDeMiEquipo.ts  (lo único nuevo)
export class TranscriptorDeMiEquipo implements Transcriptor {
  readonly motor = 'STT de mi equipo';

  async transcribir(llamada: string): Promise<Transcripcion> {
    const r = await herramientaDeMiEquipo.transcribir(llamada);  // la API o el SDK que ya usan
    return { llamada, motor: this.motor, texto: r.texto, turnos: r.turnos };
  }
}

// En la prueba solo cambia esta línea. La tarea, las preguntas, el oráculo y los guiones quedan igual:
const lucia = Actor.llamado('Lucía').puede(UsarElAgenteDeVoz.con(new TranscriptorDeMiEquipo()));"""


def pagina(base_audios, alterna=''):
    llamadas = GUIONES['llamadas']
    botones = ''.join(
        f'<button type="button" data-id="{e(g["id"])}" aria-pressed="false"><b>{e(g["id"])}</b><span>{e(g["caso"])}</span></button>'
        for g in llamadas)
    def fila(g):
        esp = g['esperado']
        monto = f"{esp['monto']:,}".replace(',', '.')
        marcas = (' <span class="chip rojo">defecto sembrado</span>' if g.get('defecto_sembrado') else '') + (' <span class="chip">ruido</span>' if g.get('ruido') else '')
        return (f'<tr><td class="id" data-k="Llamada">{e(g["id"])}</td><td data-k="Caso">{e(g["caso"])}{marcas}</td>'
                f'<td data-k="Intención esperada">{e(NOMBRE_INT[esp["intencion"]])}</td>'
                f'<td data-k="Monto y fecha">{monto} pesos · {e(esp["fecha"] or "sin fecha")}</td>'
                f'<td data-k="¿Acuerdo de pago?">{"sí" if esp["ofrece_acuerdo"] else "no"}</td></tr>')
    filas = ''.join(fila(g) for g in llamadas)
    frases = ''.join(f'<li><b>{e(f["nombre"].capitalize())}</b>: por ejemplo «{e(f["alternativas"][0])}».</li>' for f in GUIONES['politica']['frases'])
    datos = json.dumps({'guiones': GUIONES, 'transcripciones': TRANSCRIPCIONES}, ensure_ascii=False).replace('</', '<\\/')
    umbral = round(GUIONES['politica']['umbral_wer'] * 100)
    motor = TRANSCRIPCIONES['motor']
    fecha = TRANSCRIPCIONES['fecha'][:10]

    cuerpo = f'''
<h1>Probar un agente de voz <span class="acc">leyendo la llamada</span></h1>
<p class="lead">Un agente de voz con IA llama a un cliente. ¿Cómo sabe QA que hizo lo que debía, sin escuchar cada llamada a mano? Se transcribe el audio y se revisa el texto con un esperado verificable, como cualquier caso de prueba.</p>
<nav class="top" aria-label="Secciones">
<a href="#objetivo">Objetivo</a><a href="#caso">El caso</a><a href="#laboratorio">Laboratorio</a><a href="#capas">Las capas</a><a href="#no">Qué no se automatiza</a><a href="#datos">Reglas de datos</a><a href="#trabajo">En tu trabajo</a>
</nav>

<section id="objetivo">
<h2>Objetivo</h2>
<div class="card c-lav">
<p><b>Al terminar puedes revisar una llamada de un agente de voz como revisas un caso de prueba:</b> con aserciones sobre la transcripción, no con «me sonó bien».</p>
<ul class="lista">
<li><b>Frases obligatorias</b>: se identifica, dice el motivo y avisa que la llamada se graba.</li>
<li><b>Lo prohibido</b>: amenazas o lenguaje ofensivo.</li>
<li><b>El acuerdo de pago</b>: lo ofrece cuando corresponde, y no a quien ya pagó.</li>
<li><b>La intención del cliente</b>: promesa de pago con fecha, ya pagó, no reconoce la deuda o pide una persona.</li>
<li><b>Los datos</b>: monto y fecha.</li>
<li><b>El WER</b> contra el guion, con un umbral (≤ {umbral} %). Nunca coincidencia exacta: ningún reconocimiento de voz devuelve el texto idéntico.</li>
</ul>
</div>
</section>

<section id="caso">
<h2>El caso: <span class="acc">cobranza amable</span></h2>
<p>«Lía», la asistente virtual de <b>Servicios Los Alisos</b> (una empresa <b>ficticia</b>), llama a clientes <b>ficticios</b> por una cuota vencida. Los audios son <b>sintéticos</b>: los leyó una voz artificial a partir de un guion inventado.</p>
<div class="grid2">
<div class="card c-cyan"><p class="paso">la política de cobranza</p><ul class="lista">{frases}<li><b>Nunca</b>: amenazas («embargo», «demanda», «cárcel»…) ni insultos.</li></ul></div>
<div class="card c-yel"><p class="paso">cómo se lee el WER</p><p><b>WER = (palabras cambiadas + borradas + de más) ÷ palabras del guion.</b></p><p>0 % es idéntico. Con 70 palabras, 5 errores son un 7 %. El umbral lo fija el equipo según el riesgo: una llamada de cobro tolera menos que una encuesta.</p></div>
</div>
<div class="card"><table class="apilar"><thead><tr><th>Llamada</th><th>Caso</th><th>Intención esperada</th><th>Monto y fecha</th><th>¿Acuerdo?</th></tr></thead><tbody>{filas}</tbody></table>
<p class="nota">CP-305 tiene un defecto <b>sembrado</b>: el agente olvida avisar que la llamada se graba. La prueba se escribe con lo correcto y queda en rojo: es un hallazgo del agente, no de la prueba.</p></div>
</section>

<section id="laboratorio">
<h2>El <span class="acc">laboratorio</span></h2>
<p>Corre en este navegador, sin instalar nada. El oráculo es el mismo código de <code>src/voz/oraculo.ts</code> que usan las pruebas del repo.</p>
<div class="card">
<p class="paso">1 · elige una llamada</p>
<div class="llamadas" role="group" aria-label="Llamadas">{botones}</div>
</div>
<div class="card">
<p class="paso">2 · escúchala</p>
<h3 id="titulo-llamada">…</h3>
<audio id="audio" controls preload="metadata"></audio>
<p class="estado-audio" id="estado-audio" aria-live="polite"></p>
<details class="guion"><summary>Ver el guion (lo que el agente y el cliente debían decir)</summary><div id="guion"></div></details>
<p id="esperado" class="nota"></p>
</div>
<div class="card">
<p class="paso">3 · la transcripción (la puedes editar)</p>
<p class="nota">Motor: {e(motor)} · {e(fecha)}. Cada línea empieza con <code>Agente:</code> o <code>Cliente:</code>.</p>
<label for="transcripcion" class="sr-only">Transcripción</label>
<textarea id="transcripcion" class="transcripcion" spellcheck="false"></textarea>
<div class="controles">
<button type="button" class="grande" id="correr">Correr las aserciones</button>
<button type="button" id="restaurar">Restaurar la transcripción</button>
<label for="umbral">Umbral del WER <input type="number" id="umbral" min="0" max="100" step="1" value="{umbral}"> %</label>
</div>
</div>
<div class="card">
<p class="paso">4 · el resultado</p>
<p class="resumen" id="resumen" aria-live="polite"></p>
<ul class="aserciones" id="resultados"></ul>
<h3>Guion contra transcripción</h3>
<div class="diff" id="diff"></div>
<p class="leyenda"><span class="muestras"><span class="s">cambiada</span> <span class="b">borrada</span> <span class="n">+de más</span></span> · el texto ya normalizado: sin tildes ni signos y con los números en dígitos.</p>
</div>
<div class="card c-peach">
<p class="paso">provoca una falla (y mira cuál aserción se pone en rojo)</p>
<ol class="lista">
<li>En CP-301, borra «esta llamada es grabada». ¿Qué falla además del aviso? (Mira el WER.)</li>
<li>Agrega al agente: «si no paga, lo vamos a demandar».</li>
<li>Cambia «quince de diciembre» por «dieciséis de diciembre». Falla el dato, pero el WER casi no se mueve: por eso se revisan las dos cosas.</li>
<li>En CP-306, baja el umbral del WER a 5 %. ¿La llamada «falló» o el umbral es muy estricto para una línea con ruido?</li>
<li>En CP-302, cambia lo que dice el cliente por «quiero hablar con un asesor». ¿Qué intención detecta ahora?</li>
<li>En CP-305, agrega el aviso de grabación. Así se ve la corrección del agente: la prueba no se tocó.</li>
</ol>
</div>
</section>

<section id="capas">
<h2>Cómo se mapea a <span class="acc">las capas</span></h2>
<p>Es el mismo framework de la S3, con un canal nuevo. Nada del Banco Demo cambia.</p>
<div class="card"><table class="apilar"><thead><tr><th>Capa</th><th>Pieza</th><th>Qué hace</th></tr></thead><tbody>
<tr><td data-k="Capa"><b>Habilidad</b></td><td data-k="Pieza"><code>UsarElAgenteDeVoz</code></td><td data-k="Qué hace">Guarda un <code>Transcriptor</code>: <code>TranscriptorDeArchivo</code> (clase, sin red) o <code>TranscriptorElevenLabs</code> (motor real, con clave).</td></tr>
<tr><td data-k="Capa"><b>Tarea</b></td><td data-k="Pieza"><code>EscucharLaLlamada</code></td><td data-k="Qué hace">«Dado la llamada CP-301 transcrita»: transcribe y guarda el texto en la memoria del actor.</td></tr>
<tr><td data-k="Capa"><b>Pregunta</b></td><td data-k="Pieza"><code>IntencionDelCliente</code></td><td data-k="Qué hace">¿Qué quiere el cliente? Mira solo lo que dijo el cliente.</td></tr>
<tr><td data-k="Capa"><b>Pregunta</b></td><td data-k="Pieza"><code>CumplimientoDelGuion</code></td><td data-k="Qué hace">El informe: frases, prohibidas, acuerdo, datos y WER contra el umbral.</td></tr>
<tr><td data-k="Capa"><b>Oráculo</b></td><td data-k="Pieza"><code>src/voz/oraculo.ts</code></td><td data-k="Qué hace">Funciones puras: normalizar, WER (Levenshtein en palabras), frases, intención y datos.</td></tr>
<tr><td data-k="Capa"><b>Datos</b></td><td data-k="Pieza"><code>voz/guiones.json</code></td><td data-k="Qué hace">El guion y el esperado de cada llamada. Agregar un caso es agregar un guion.</td></tr>
<tr><td data-k="Capa"><b>Especificación</b></td><td data-k="Pieza"><code>especificaciones/cobranza-voz.feature</code></td><td data-k="Qué hace">Un «Esquema del escenario» con «Ejemplos»: una fila por llamada. Es el puente al DDT de la S8.</td></tr>
</tbody></table></div>
<p>La prueba (<code>tests/voz/cobranza.spec.ts</code>), resumida:</p>
<pre class="code">{e(PRUEBA_TS)}</pre>
<p class="nota">Correr en el repo: <code>npx.cmd playwright test --project=voz</code>. No abre navegador ni necesita el Banco Demo.</p>
</section>

<section id="no">
<h2>Qué <span class="acc">no</span> se automatiza (y por qué)</h2>
<div class="grid3">
<div class="card"><h3>El tono</h3><p>La transcripción pierde cómo se dijo: una frase correcta puede sonar brusca. El texto no lo muestra.</p></div>
<div class="card"><h3>La empatía</h3><p>Si el agente escuchó al cliente, o solo le respondió, es un juicio. Lo hace una persona con una rúbrica sobre una muestra de llamadas.</p></div>
<div class="card"><h3>La latencia real</h3><p>Los silencios, las interrupciones y lo que tarda en responder se miden en la plataforma de voz, en tiempo real. Un archivo ya grabado no los tiene.</p></div>
</div>
<p>Lo automatizado cubre lo <b>verificable</b> (lo que el agente debe decir y entender). Lo humano cubre la <b>calidad</b>. Las dos cosas van al informe.</p>
</section>

<section id="datos">
<h2>Reglas de <span class="acc">datos</span></h2>
<div class="card c-peach"><ul class="lista">
<li><b>Solo audio sintético de guiones ficticios.</b> Empresa, personas, montos y fechas son inventados.</li>
<li><b>Nunca llamadas reales</b>, ni para «probar rápido»: son datos personales (Ley 1581 de 2012), y la voz que identifica a una persona es un dato <b>biométrico</b>, es decir, sensible.</li>
<li><b>Ningún audio a un servicio en la nube sin aprobación.</b> Un STT en la nube es enviar datos a un tercero. El dictado de voz del navegador también manda el audio a la nube.</li>
<li><b>La clave del motor va en el <code>.env</code></b>, nunca en el código, en un reporte ni en un chat.</li>
<li><b>Sin marcas reales</b> en los guiones: el caso es de práctica, no de un cliente.</li>
</ul></div>
</section>

<section id="trabajo">
<h2>En <span class="acc">tu trabajo</span></h2>
<div class="card c-lime">
<p><b>Con la herramienta de STT de tu equipo, solo cambia el <code>Transcriptor</code>.</b> Es la D de SOLID de la S4 y la habilidad de Screenplay de la S5: la tarea, las preguntas, el oráculo y los guiones no se enteran.</p>
<pre class="code">{e(TU_TRANSCRIPTOR)}</pre>
<p>Y los guiones de tu equipo (el esperado de cada llamada) van en el mismo formato de <code>voz/guiones.json</code>, con la política de cobranza que firme el negocio.</p>
</div>
</section>
'''
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kit de voz</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&amp;family=Nunito:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>{CSS_BASE}{CSS_VOZ}</style>
</head>
<body data-audios="{e(base_audios)}" data-audios-alterna="{e(alterna)}">
<div class="wrap">
<div class="knot-bar"><span><img src="{LOGO}" alt="">knot academy × accenture</span><small>Bootcamp QA &amp; Automatización · kit de voz</small></div>
{cuerpo}
<p class="nota">Página del Bootcamp QA · Knot Academy, generada con <code>laboratorio/generar/generar_voz.py</code>. No carga nada de internet salvo las fuentes y los audios del bootcamp. Todo es ficticio: nunca escribas aquí datos reales.</p>
</div>
<script type="application/json" id="datos-voz">{datos}</script>
<script>{ORACULO}</script>
<script>{JS_LAB}</script>
</body>
</html>
'''


ORACULO = oraculo_js()
(RAIZ / 'laboratorio' / 'voz.html').write_text(pagina('voz/audios/', '../voz/audios/'), encoding='utf-8')
local = pagina(PAGES + 'voz/audios/')
assert 'claude.ai' not in local, 'voz.html: enlace de claude.ai'
assert not re.findall(r'href="(?!https?://|#|data:)([^"]+)"', local), 'voz.html: enlaces relativos en la copia local'
if PARA_ENVIAR.is_dir():
    (PARA_ENVIAR / 'voz.html').write_text(local, encoding='utf-8')
print('voz.html listo (laboratorio/ con audios relativos y para_enviar/ con audios en Pages)')
