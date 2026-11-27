/*
 * S7 y S8 · REVISOR DE ESCENARIOS: revisa un texto en Gherkin con las reglas de la lista de cotejo.
 * Lo usan las páginas de actividades (en el navegador, sin instalar nada) y `npm run revisar-escenarios`.
 * Es una ayuda, no un juez: señala lo típico (clics, localizadores, falta de ID, «Entonces» sin dato).
 * Lo que no puede saber (si el esperado es el correcto) lo decide la persona.
 *
 * S8 (council_S8): lee el «Esquema del escenario» con sus «Ejemplos» y dice cuántas pruebas salen
 * (una por fila); el ID del caso va exacto (@CP-104); un <marcador> fuera de un Esquema tiene su propio mensaje.
 *
 * Devuelve, por escenario:
 *   { titulo, linea, id, esquema, columnas, filas, pruebas, pasos, hallazgos: [{ nivel: 'ok'|'aviso'|'error', texto }] }
 */
(function (raiz) {
  const PALABRAS = /^\s*(Dado|Dada|Dados|Dadas|Cuando|Entonces|Y|E|Pero)\b/i;
  const IMPERATIVO = /\b(clic|click|cliquea|pulsa|pulso|pulsar|presiona|oprime|da clic|hace clic|hago clic|selecciona|seleccionar|escribe en|digita|llena|llenar|ingresa en|botón|boton|campo|casilla|desplegable|scroll|navega a|abre la url|url)\b/i;
  const TECNICO = /(getBy\w+|locator\(|xpath|css|#[a-z][\w-]*|\.[a-z][\w-]*\b(?=\s*(?:>|$))|data-testid|nth-child|\/\/[a-z]+\[|<[a-z]+)/i;
  const ESPERA_FIJA = /\b(espera|esperar|esperamos)\s+\d+\s*(s|seg|segundos|ms|milisegundos)\b/i;
  const CLAVE = /\b(clave|contraseña|password)\b\s*[:=«"']?\s*[\w@#$%&*]{4,}/i;
  const DATO = /(\$\s?[\d.]+|\d|«[^»]+»|"[^"]+"|“[^”]+”)/;
  // Un marcador de Esquema: <monto>, <ya_recargo>. Las etiquetas de HTML (<div>, <button>…) siguen siendo «código».
  const MARCADOR = /<([a-záéíóúñ_][a-záéíóúñ_0-9]*)>/gi;
  const HTML = /^(a|b|i|p|div|span|button|input|form|label|select|option|li|ul|ol|td|tr|th|table|img|h[1-6]|br|section|nav|header|footer)$/i;
  // El ID del caso: exacto, @CP- y tres dígitos. Es el puente con el reporte (-g "CP-104"), Trello y Jira.
  const ID_EXACTO = /^@CP-\d{3}$/;
  const ID_CASI = /cp/i;

  const marcadores = (texto) => Array.from(String(texto).matchAll(MARCADOR)).map((m) => m[1]).filter((m) => !HTML.test(m));
  const celdas = (linea) => linea.replace(/^\|/, '').replace(/\|\s*$/, '').split('|').map((c) => c.trim());

  function revisar(texto) {
    const lineas = String(texto || '').split(/\r?\n/);
    const escenarios = [];
    let etiquetas = [];
    let actual = null;
    let tabla = null; // el bloque «Ejemplos» que se está leyendo
    lineas.forEach((cruda, i) => {
      const linea = cruda.trim();
      if (!linea || linea.startsWith('#')) return;
      if (linea.startsWith('|')) {
        if (tabla) {
          if (!tabla.columnas) tabla.columnas = celdas(linea);
          else tabla.filas.push({ celdas: celdas(linea), linea: i + 1 });
        }
        return; // una tabla de datos de un paso (sin «Ejemplos») no se revisa
      }
      if (linea.startsWith('@')) { etiquetas = etiquetas.concat(linea.split(/\s+/)); return; }
      if (/^(Ejemplos|Examples|Escenarios)\s*:/i.test(linea)) {
        // Las etiquetas que estén encima de «Ejemplos» son de esa tabla, no del escenario siguiente.
        etiquetas = [];
        if (!actual) return;
        tabla = { columnas: null, filas: [], linea: i + 1 };
        actual.tablas.push(tabla);
        return;
      }
      tabla = null;
      const esc = linea.match(/^(Escenario|Ejemplo|Esquema del escenario|Scenario|Scenario Outline)\s*:\s*(.*)$/i);
      if (esc) {
        actual = { titulo: esc[2] || '(sin título)', linea: i + 1, etiquetas, pasos: [], tablas: [], esquema: /^(Esquema del escenario|Scenario Outline)$/i.test(esc[1]) };
        escenarios.push(actual);
        etiquetas = [];
        return;
      }
      if (/^(Característica|Caracteristica|Feature|Antecedentes|Background|Regla|Rule)\s*:/i.test(linea)) { actual = null; etiquetas = []; return; }
      const p = linea.match(PALABRAS);
      if (p) {
        if (!actual) { actual = { titulo: '(pasos sin «Escenario:»)', linea: i + 1, etiquetas, pasos: [], tablas: [], esquema: false }; escenarios.push(actual); etiquetas = []; }
        actual.pasos.push({ tipo: p[1].toLowerCase(), texto: linea, linea: i + 1 });
      }
    });
    return escenarios.map(evaluar);
  }

  function evaluar(e) {
    const h = [];
    // Desde Gherkin 6, «Escenario» y «Esquema del escenario» son sinónimos: con «Ejemplos», los dos dan una prueba por fila.
    const escenarioConTabla = !e.esquema && e.tablas.length > 0;
    if (escenarioConTabla) e = Object.assign({}, e, { esquema: true });
    const agregar = (nivel, texto) => h.push({ nivel, texto });
    // El tipo real de Y/Pero es el del paso anterior (la palabra es para leer mejor; los pasos corren en orden).
    let previo = null;
    const pasos = e.pasos.map((p) => {
      let tipo = p.tipo;
      if (/^(y|e|pero)$/.test(tipo)) tipo = previo || 'dado';
      if (/^dad/.test(tipo)) tipo = 'dado';
      previo = tipo;
      return Object.assign({}, p, { tipoReal: tipo });
    });
    const tiene = (t) => pasos.some((p) => p.tipoReal === t);

    // La tabla de Ejemplos (puede haber varias: se suman).
    const columnas = (e.tablas.find((t) => t.columnas) || {}).columnas || [];
    const filas = [].concat(...e.tablas.map((t) => t.filas));
    const pruebas = e.esquema ? filas.length : 1;
    const resumen = { titulo: e.titulo, linea: e.linea, id: null, esquema: !!e.esquema, columnas, filas: filas.map((f) => f.celdas), pruebas, pasos: pasos.length };

    // El ID del caso, exacto.
    const ids = e.etiquetas.filter((t) => ID_EXACTO.test(t));
    const casi = e.etiquetas.filter((t) => !ID_EXACTO.test(t) && ID_CASI.test(t));
    if (ids.length) {
      resumen.id = ids[0];
      agregar('ok', `Trazable: ${ids.join(' ')} (el ID del caso va en la etiqueta)`);
    } else if (casi.length) {
      const sugerido = (casi[0].match(/\d{3}/) || ['102'])[0];
      agregar('error', `Encontré «${casi[0]}», pero el ID va exacto: @CP-${sugerido}. Es el puente con el reporte, Trello y Jira; si está mal escrito, nadie lo encuentra`);
    } else {
      agregar('error', 'Sin ID del caso: agrega una etiqueta como @CP-102 encima de «Escenario:»');
    }

    if (!pasos.length) { agregar('error', 'Todavía no tiene pasos (Dado, Cuando, Entonces)'); resumen.hallazgos = h; return resumen; }
    ['dado', 'cuando', 'entonces'].forEach((t) => {
      if (!tiene(t)) agregar('error', `Falta un «${t[0].toUpperCase() + t.slice(1)}»`);
    });
    const orden = pasos.map((p) => p.tipoReal);
    if (orden.indexOf('cuando') > -1 && orden.indexOf('dado') > orden.indexOf('cuando')) agregar('aviso', 'El «Dado» va antes del «Cuando»: primero la precondición');
    if (orden.filter((t, i) => t === 'cuando' && orden[i - 1] !== 'cuando').length > 1) agregar('aviso', 'Tiene más de un «Cuando»: ¿son dos escenarios? Si el caso lo pide (pedir código y confirmar), está bien');
    if (pasos.length > 5) agregar('aviso', `Tiene ${pasos.length} pasos: con más de 5 suele estar contando la pantalla y no el negocio`);

    // Los marcadores que usan los pasos (y el título, que en un Esquema también se llena con la fila).
    const usados = new Set(marcadores(e.titulo));
    pasos.forEach((p) => marcadores(p.texto).forEach((m) => usados.add(m)));
    const conColumna = (m) => columnas.includes(m);

    pasos.forEach((p) => {
      const suyos = marcadores(p.texto);
      if (!e.esquema && suyos.length) {
        agregar('error', `Línea ${p.linea}: «<${suyos[0]}>» es un marcador del Esquema del escenario. Usa «Esquema del escenario:» con una tabla «Ejemplos» que tenga la columna «${suyos[0]}», o escribe el dato real (por ejemplo, $150.000)`);
        return;
      }
      // En un Esquema, <monto> se llena con la fila de «Ejemplos»: cuenta como dato, no como HTML.
      const texto = e.esquema ? p.texto.replace(MARCADOR, (todo, m) => (HTML.test(m) ? todo : '«X»')) : p.texto;
      if (TECNICO.test(texto)) agregar('error', `Línea ${p.linea}: tiene un localizador o código («${p.texto}»). El escenario es del negocio; el localizador vive en el Page Object`);
      else if (IMPERATIVO.test(p.texto)) agregar('error', `Línea ${p.linea}: describe la pantalla («${p.texto}»). Di QUÉ hace el cliente, no DÓNDE hace clic: «Cuando recarga $10.000…». El clic es asunto del Page Object`);
      if (ESPERA_FIJA.test(p.texto)) agregar('error', `Línea ${p.linea}: una espera fija no es un paso del negocio. Playwright espera solo`);
      if (CLAVE.test(p.texto)) agregar('error', `Línea ${p.linea}: la clave nunca va escrita en el escenario (sale del entorno)`);
      if (p.tipoReal === 'entonces' && !DATO.test(texto)) agregar('aviso', `Línea ${p.linea}: este «Entonces» no tiene un dato que se pueda verificar (un monto, un texto entre «comillas»)`);
    });

    // El Esquema y sus Ejemplos.
    if (e.esquema) {
      if (!e.tablas.length || !columnas.length) {
        agregar('error', 'Un «Esquema del escenario» necesita su tabla «Ejemplos»: la primera fila son los nombres de las columnas y cada fila siguiente es una prueba');
      } else {
        usados.forEach((m) => { if (!conColumna(m)) agregar('error', `«<${m}>» no tiene columna en «Ejemplos»: agrega la columna «${m}» o corrige el nombre`); });
        columnas.forEach((c) => { if (c && !usados.has(c)) agregar('aviso', `La columna «${c}» no se usa en ningún paso: ¿sobra o falta un <${c}>?`); });
        filas.forEach((f) => { if (f.celdas.length !== columnas.length) agregar('error', `Línea ${f.linea}: la fila tiene ${f.celdas.length} celdas y la tabla tiene ${columnas.length} columnas`); });
        const vistas = new Map();
        filas.forEach((f) => {
          const clave = f.celdas.join('|');
          if (vistas.has(clave)) agregar('aviso', `Línea ${f.linea}: la fila repite la de la línea ${vistas.get(clave)}: es la misma prueba dos veces`);
          else vistas.set(clave, f.linea);
        });
        if (!filas.length) agregar('error', 'La tabla «Ejemplos» no tiene filas de datos: cada fila es una prueba');
        else if (!marcadores(e.titulo).length) agregar('aviso', `El título no tiene ningún <marcador>: las ${filas.length} pruebas se llamarían igual en el reporte. Pon el dato en el título (por ejemplo «…: <monto>»)`);
        if (filas.length) agregar('ok', `Salen ${filas.length} prueba${filas.length === 1 ? '' : 's'}, una por fila de «Ejemplos»`);
      }
    }
    if (escenarioConTabla) agregar('aviso', 'Tiene «Ejemplos» bajo un «Escenario:». Cucumber igual saca una prueba por fila (desde Gherkin 6 son sinónimos), pero escribe «Esquema del escenario:» para que quien lo lea sepa que es una plantilla');

    if (!h.some((x) => x.nivel !== 'ok')) agregar('ok', 'Declarativo, con Dado, Cuando y Entonces, y un esperado verificable');
    resumen.hallazgos = h;
    return resumen;
  }

  /**
   * El texto para pegar en el chat de Teams (S8: lo que no está en el chat principal no pasó).
   * Primera línea: «Sala 2 · CP-104 · 0 errores · salen 3 pruebas»; debajo, el escenario.
   */
  function paraElChat(texto, sala) {
    const res = revisar(texto);
    const errores = res.reduce((n, e) => n + e.hallazgos.filter((x) => x.nivel === 'error').length, 0);
    const pruebas = res.reduce((n, e) => n + e.pruebas, 0);
    const ids = res.map((e) => (e.id || '').replace('@', '')).filter(Boolean);
    const cabeza = [sala, ids.length ? ids.join(', ') : 'sin ID', `${errores} error${errores === 1 ? '' : 'es'}`, `salen ${pruebas} prueba${pruebas === 1 ? '' : 's'}`].filter(Boolean).join(' · ');
    return cabeza + '\n' + String(texto || '').trim();
  }

  const api = { revisar, paraElChat };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.RevisorDeEscenarios = api;
})(typeof window !== 'undefined' ? window : globalThis);
