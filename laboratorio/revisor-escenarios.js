/*
 * S7 · REVISOR DE ESCENARIOS: revisa un texto en Gherkin con las reglas de la lista de cotejo.
 * Lo usan la página de actividades (en el navegador, sin instalar nada) y `npm run revisar-escenarios`.
 * Es una ayuda, no un juez: señala lo típico (clics, localizadores, falta de ID, «Entonces» sin dato).
 * Lo que no puede saber (si el esperado es el correcto) lo decide la persona.
 */
(function (raiz) {
  const PALABRAS = /^\s*(Dado|Dada|Dados|Dadas|Cuando|Entonces|Y|E|Pero)\b/i;
  const IMPERATIVO = /\b(clic|click|cliquea|pulsa|pulso|pulsar|presiona|oprime|da clic|hace clic|hago clic|selecciona|seleccionar|escribe en|digita|llena|llenar|ingresa en|botón|boton|campo|casilla|desplegable|scroll|navega a|abre la url|url)\b/i;
  const TECNICO = /(getBy\w+|locator\(|xpath|css|#[a-z][\w-]*|\.[a-z][\w-]*\b(?=\s*(?:>|$))|data-testid|nth-child|\/\/[a-z]+\[|<[a-z]+)/i;
  const ESPERA_FIJA = /\b(espera|esperar|esperamos)\s+\d+\s*(s|seg|segundos|ms|milisegundos)\b/i;
  const CLAVE = /\b(clave|contraseña|password)\b\s*[:=«"']?\s*[\w@#$%&*]{4,}/i;
  const DATO = /(\$\s?[\d.]+|\d|«[^»]+»|"[^"]+"|“[^”]+”)/;

  function revisar(texto) {
    const lineas = String(texto || '').split(/\r?\n/);
    const escenarios = [];
    let etiquetas = [];
    let actual = null;
    lineas.forEach((cruda, i) => {
      const linea = cruda.trim();
      if (!linea || linea.startsWith('#')) return;
      if (linea.startsWith('@')) { etiquetas = etiquetas.concat(linea.split(/\s+/)); return; }
      const esc = linea.match(/^(Escenario|Ejemplo|Esquema del escenario|Scenario|Scenario Outline)\s*:\s*(.*)$/i);
      if (esc) {
        actual = { titulo: esc[2] || '(sin título)', linea: i + 1, etiquetas, pasos: [] };
        escenarios.push(actual);
        etiquetas = [];
        return;
      }
      if (/^(Característica|Caracteristica|Feature|Antecedentes|Background|Regla|Rule)\s*:/i.test(linea)) { actual = null; etiquetas = []; return; }
      const p = linea.match(PALABRAS);
      if (p) {
        if (!actual) { actual = { titulo: '(pasos sin «Escenario:»)', linea: i + 1, etiquetas, pasos: [] }; escenarios.push(actual); etiquetas = []; }
        actual.pasos.push({ tipo: p[1].toLowerCase(), texto: linea, linea: i + 1 });
      }
    });
    return escenarios.map(evaluar);
  }

  function evaluar(e) {
    const h = [];
    const agregar = (nivel, texto) => h.push({ nivel, texto });
    // El tipo real de Y/Pero es el del paso anterior.
    let previo = null;
    const pasos = e.pasos.map((p) => {
      let tipo = p.tipo;
      if (/^(y|e|pero)$/.test(tipo)) tipo = previo || 'dado';
      if (/^dad/.test(tipo)) tipo = 'dado';
      previo = tipo;
      return Object.assign({}, p, { tipoReal: tipo });
    });
    const tiene = (t) => pasos.some((p) => p.tipoReal === t);

    const id = e.etiquetas.find((t) => /^@CP-\d+/i.test(t));
    if (id) agregar('ok', `Trazable: ${id} (el ID del caso va en la etiqueta)`);
    else agregar('error', 'Sin ID del caso: agrega una etiqueta como @CP-102 encima de «Escenario:»');

    if (!pasos.length) { agregar('error', 'Todavía no tiene pasos (Dado, Cuando, Entonces)'); return { titulo: e.titulo, linea: e.linea, hallazgos: h, pasos: 0 }; }
    ['dado', 'cuando', 'entonces'].forEach((t) => {
      if (!tiene(t)) agregar('error', `Falta un «${t[0].toUpperCase() + t.slice(1)}»`);
    });
    const orden = pasos.map((p) => p.tipoReal);
    if (orden.indexOf('cuando') > -1 && orden.indexOf('dado') > orden.indexOf('cuando')) agregar('aviso', 'El «Dado» va antes del «Cuando»: primero la precondición');
    if (orden.filter((t, i) => t === 'cuando' && orden[i - 1] !== 'cuando').length > 1) agregar('aviso', 'Tiene más de un «Cuando»: ¿son dos escenarios? Si el caso lo pide (pedir código y confirmar), está bien');
    if (pasos.length > 5) agregar('aviso', `Tiene ${pasos.length} pasos: con más de 5 suele estar contando la pantalla y no el negocio`);

    pasos.forEach((p) => {
      if (TECNICO.test(p.texto)) agregar('error', `Línea ${p.linea}: tiene un localizador o código («${p.texto}»). El escenario es del negocio; el localizador vive en el Page Object`);
      else if (IMPERATIVO.test(p.texto)) agregar('error', `Línea ${p.linea}: describe la pantalla («${p.texto}»). Di QUÉ hace el cliente, no DÓNDE hace clic: «Cuando recarga $10.000…». El clic es asunto del Page Object`);
      if (ESPERA_FIJA.test(p.texto)) agregar('error', `Línea ${p.linea}: una espera fija no es un paso del negocio. Playwright espera solo`);
      if (CLAVE.test(p.texto)) agregar('error', `Línea ${p.linea}: la clave nunca va escrita en el escenario (sale del entorno)`);
      if (p.tipoReal === 'entonces' && !DATO.test(p.texto)) agregar('aviso', `Línea ${p.linea}: este «Entonces» no tiene un dato que se pueda verificar (un monto, un texto entre «comillas»)`);
    });
    if (!h.some((x) => x.nivel !== 'ok')) agregar('ok', 'Declarativo, con Dado, Cuando y Entonces, y un esperado verificable');
    return { titulo: e.titulo, linea: e.linea, hallazgos: h, pasos: pasos.length };
  }

  const api = { revisar };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.RevisorDeEscenarios = api;
})(typeof window !== 'undefined' ? window : globalThis);
