/*
 * MOTOR DE LOCALIZADORES del laboratorio S6: un Playwright MÍNIMO que corre en el navegador, sin red.
 *
 * Busca sobre la copia real de la pantalla de Recargas del Banco Demo (la de hoy y la del rediseño),
 * cargada en un iframe, con las mismas reglas que Playwright 1.63:
 *   getByRole (rol implícito o explícito + nombre accesible; deja fuera lo oculto), getByLabel, getByText,
 *   getByTestId, getByPlaceholder, getByTitle, getByAltText, locator(css | xpath=…), first/last/nth/or/filter.
 * Modo estricto, «no encontrado», acciones (click, fill, selectOption…) y aserciones que reintentan
 * (toHaveText, toBeVisible, toHaveCount…), con mensajes que imitan los de Playwright.
 *
 * Simplificado: el Playwright real hace más (shadow DOM, frames, teclado y ratón de verdad, red, trazas…).
 * Lo generó laboratorio/generar/generar_s6.py; se incrusta en laboratorio_S6.html.
 */
var Motor = (function () {
  'use strict';
  var TIEMPO = 5000; // espera máxima de una acción o una aserción (en Playwright: expect.timeout = 5000)

  function dormir(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function normalizar(s) { return String(s == null ? '' : s).replace(/​/g, '').trim().replace(/\s+/g, ' '); }
  function comillas(s) { return "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n') + "'"; }
  function literal(v) { return v instanceof RegExp ? String(v) : typeof v === 'string' ? comillas(v) : String(v); }
  function recortar(s, n) { return s.length <= n ? s : s.substring(0, n - 1) + '…'; }
  function unaLinea(s) { return s.replace(/\n/g, '↵').replace(/\t/g, '⇆'); }
  function estilo(el) { return el.ownerDocument.defaultView.getComputedStyle(el); }
  function ordenar(lista) {
    var unicos = lista.filter(function (e, i) { return lista.indexOf(e) === i; });
    return unicos.sort(function (a, b) { return a === b ? 0 : (a.compareDocumentPosition(b) & 4 ? -1 : 1); });
  }
  function todos(raiz) { return Array.prototype.slice.call(raiz.querySelectorAll('*')); }

  // ---------- texto de un elemento (como elementText de Playwright: sin <script>, <style> ni <head>)
  function saltaTexto(el) {
    var n = el.nodeName, doc = el.ownerDocument;
    return n === 'SCRIPT' || n === 'NOSCRIPT' || n === 'STYLE' || !!(doc.head && doc.head.contains(el));
  }
  function textoDe(nodo) {
    if (nodo.nodeType === 3) return nodo.nodeValue;
    if (nodo.nodeType !== 1 || saltaTexto(nodo)) return '';
    if (nodo.nodeName === 'INPUT' && (nodo.type === 'submit' || nodo.type === 'button')) return nodo.value;
    var t = '';
    for (var c = nodo.firstChild; c; c = c.nextSibling) t += textoDe(c);
    return t;
  }
  /** El comparador de texto de Playwright: por defecto parcial y sin mayúsculas; exact: completo y exacto; o una expresión regular. */
  function comparador(buscado, exacto) {
    if (buscado instanceof RegExp) return function (texto) { buscado.lastIndex = 0; return buscado.test(texto); };
    var b = normalizar(buscado);
    if (exacto) return function (texto) { return normalizar(texto) === b; };
    b = b.toLowerCase();
    return function (texto) { return normalizar(texto).toLowerCase().indexOf(b) >= 0; };
  }
  /** 'self' si el texto está en el elemento y en ninguno de sus hijos; 'hijos' si también está en un hijo. */
  function coincideTexto(el, cmp) {
    if (saltaTexto(el) || !cmp(textoDe(el))) return 'no';
    for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (cmp(textoDe(c))) return 'hijos';
    return 'self';
  }

  // ---------- visibilidad, roles y nombre accesible (lo que «ve y oye» el usuario)
  function visible(el) {
    var st = estilo(el);
    if (st.display === 'contents') {
      for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (visible(c)) return true;
      return false;
    }
    if (el.checkVisibility && !el.checkVisibility()) return false;
    if (st.visibility !== 'visible') return false;
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function ocultoParaAria(el) {
    if (/^(STYLE|SCRIPT|NOSCRIPT|TEMPLATE)$/.test(el.nodeName)) return true;
    var st = estilo(el);
    if (st.display === 'contents') {
      for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (!ocultoParaAria(c)) return false;
      return true;
    }
    var opcionEnLista = el.nodeName === 'OPTION' && !!el.closest('select');
    if (!opcionEnLista && st.visibility !== 'visible') return true;
    for (var e = el; e; e = e.parentElement) {
      if (estilo(e).display === 'none') return true;
      if ((e.getAttribute('aria-hidden') || '').toLowerCase() === 'true') return true;
    }
    return false;
  }
  var ROLES_VALIDOS = ('alert alertdialog application article banner blockquote button caption cell checkbox code columnheader combobox ' +
    'complementary contentinfo definition deletion dialog directory document emphasis feed figure form generic grid gridcell group heading img ' +
    'insertion link list listbox listitem log main mark marquee math meter menu menubar menuitem menuitemcheckbox menuitemradio navigation none ' +
    'note option paragraph presentation progressbar radio radiogroup region row rowgroup rowheader scrollbar search searchbox separator slider ' +
    'spinbutton status strong subscript superscript switch tab table tablist tabpanel term textbox time timer toolbar tooltip tree treegrid treeitem').split(' ');
  function tieneNombrePropio(el) { return !!(normalizar(el.getAttribute('aria-label')) || el.getAttribute('aria-labelledby') || normalizar(el.getAttribute('title'))); }
  function dentroDeSeccion(el) { return !!(el.parentElement && el.parentElement.closest('article, aside, main, nav, section')); }
  function rolImplicito(el) {
    var t = el.nodeName;
    if (/^H[1-6]$/.test(t)) return 'heading';
    switch (t) {
      case 'A': case 'AREA': return el.hasAttribute('href') ? 'link' : null;
      case 'BUTTON': return 'button';
      case 'INPUT': {
        var ty = (el.type || 'text').toLowerCase();
        if (ty === 'search') return el.hasAttribute('list') ? 'combobox' : 'searchbox';
        if (['email', 'tel', 'text', 'url', ''].indexOf(ty) >= 0) return el.hasAttribute('list') ? 'combobox' : 'textbox';
        if (ty === 'hidden') return null;
        if (ty === 'file') return 'button';
        return { button: 'button', checkbox: 'checkbox', image: 'button', number: 'spinbutton', radio: 'radio', range: 'slider', reset: 'button', submit: 'button' }[ty] || 'textbox';
      }
      case 'SELECT': return (el.multiple || el.size > 1) ? 'listbox' : 'combobox';
      case 'TEXTAREA': return 'textbox';
      case 'OPTION': return 'option';
      case 'IMG': return (el.getAttribute('alt') === '' && !tieneNombrePropio(el)) ? 'presentation' : 'img';
      case 'FORM': return tieneNombrePropio(el) ? 'form' : null;
      case 'SECTION': return tieneNombrePropio(el) ? 'region' : null;
      case 'HEADER': return dentroDeSeccion(el) ? null : 'banner';
      case 'FOOTER': return dentroDeSeccion(el) ? null : 'contentinfo';
      case 'OUTPUT': return 'status';
    }
    return { ARTICLE: 'article', ASIDE: 'complementary', BLOCKQUOTE: 'blockquote', CAPTION: 'caption', CODE: 'code', DATALIST: 'listbox', DD: 'definition',
      DEL: 'deletion', DETAILS: 'group', DFN: 'term', DIALOG: 'dialog', DT: 'term', EM: 'emphasis', FIELDSET: 'group', FIGURE: 'figure', HR: 'separator',
      HTML: 'document', INS: 'insertion', LI: 'listitem', MAIN: 'main', MARK: 'mark', MATH: 'math', MENU: 'list', METER: 'meter', NAV: 'navigation', OL: 'list',
      OPTGROUP: 'group', P: 'paragraph', PROGRESS: 'progressbar', STRONG: 'strong', SUB: 'subscript', SUP: 'superscript', TABLE: 'table', TBODY: 'rowgroup',
      TD: 'cell', TFOOT: 'rowgroup', THEAD: 'rowgroup', TH: 'columnheader', TIME: 'time', TR: 'row', UL: 'list' }[t] || null;
  }
  function rolDe(el) {
    var explicito = (el.getAttribute('role') || '').trim().toLowerCase().split(/\s+/).filter(function (r) { return ROLES_VALIDOS.indexOf(r) >= 0; })[0];
    return explicito || rolImplicito(el);
  }
  var NOMBRE_DEL_CONTENIDO = 'button cell checkbox columnheader gridcell heading link menuitem menuitemcheckbox menuitemradio option radio row rowheader switch tab tooltip treeitem'.split(' ');
  function etiquetable(el) {
    return ['BUTTON', 'METER', 'OUTPUT', 'PROGRESS', 'SELECT', 'TEXTAREA'].indexOf(el.nodeName) >= 0 || (el.nodeName === 'INPUT' && el.type !== 'hidden');
  }
  function porIds(el, attr) {
    var ids = (el.getAttribute(attr) || '').split(/\s+/).filter(Boolean), doc = el.ownerDocument;
    return ids.map(function (id) { return doc.getElementById(id); }).filter(Boolean);
  }
  function contenido(el, excluir) {
    var t = '';
    for (var c = el.firstChild; c; c = c.nextSibling) {
      if (c.nodeType === 3) { t += c.nodeValue; continue; }
      if (c.nodeType !== 1 || c === excluir || ocultoParaAria(c)) continue;
      var bloque = c.nodeName === 'BR' || estilo(c).display.indexOf('inline') !== 0 ? ' ' : '';
      var al = normalizar(c.getAttribute('aria-label'));
      t += bloque + (al || (c.nodeName === 'IMG' ? (c.getAttribute('alt') || '') : contenido(c, excluir))) + bloque;
    }
    return t;
  }
  function nombreAccesible(el) {
    var ref = porIds(el, 'aria-labelledby');
    if (ref.length) return normalizar(ref.map(function (r) { return contenido(r); }).join(' '));
    var al = normalizar(el.getAttribute('aria-label'));
    if (al) return al;
    if (el.nodeName === 'INPUT' && ['button', 'submit', 'reset'].indexOf(el.type) >= 0) return normalizar(el.value || ({ submit: 'Submit', reset: 'Reset' }[el.type] || ''));
    if (el.nodeName === 'INPUT' && el.type === 'image') return normalizar(el.getAttribute('alt') || el.getAttribute('title') || 'Submit');
    if (etiquetable(el) && el.labels && el.labels.length) {
      var n = normalizar(Array.prototype.map.call(el.labels, function (l) { return contenido(l, el); }).join(' '));
      if (n) return n;
    }
    if (el.nodeName === 'IMG' && el.hasAttribute('alt')) return normalizar(el.getAttribute('alt'));
    if (el.nodeName === 'FIELDSET') { var lg = el.querySelector(':scope > legend'); if (lg) return normalizar(contenido(lg)); }
    if (el.nodeName === 'TABLE') { var cp = el.querySelector(':scope > caption'); if (cp) return normalizar(contenido(cp)); }
    if (NOMBRE_DEL_CONTENIDO.indexOf(rolDe(el)) >= 0) { var c = normalizar(contenido(el)); if (c) return c; }
    if (normalizar(el.getAttribute('title'))) return normalizar(el.getAttribute('title'));
    if ((el.nodeName === 'INPUT' || el.nodeName === 'TEXTAREA') && el.getAttribute('placeholder')) return normalizar(el.getAttribute('placeholder'));
    return '';
  }
  /** Las etiquetas de un campo, como las usa getByLabel: aria-labelledby, aria-label o los <label> del campo. */
  function etiquetasDe(el) {
    var ref = porIds(el, 'aria-labelledby');
    if (ref.length) return ref.map(textoDe);
    var al = el.getAttribute('aria-label');
    if (al !== null && al.trim()) return [al];
    if (etiquetable(el) && el.labels) return Array.prototype.map.call(el.labels, textoDe);
    return [];
  }

  // ---------- los buscadores: cada uno recibe el alcance (documento o elemento) y devuelve elementos
  function porAtributo(attr, valor, exacto) {
    var cmp = comparador(valor, exacto);
    return function (raiz) { return todos(raiz).filter(function (e) { return e.hasAttribute(attr) && cmp(e.getAttribute(attr)); }); };
  }
  var BUSCAR = {
    role: function (rol, op) {
      op = op || {};
      var cmpNombre = op.name === undefined ? null : (op.name instanceof RegExp ? comparador(op.name) : comparador(op.name, !!op.exact));
      return function (raiz) {
        return todos(raiz).filter(function (e) {
          if (rolDe(e) !== rol) return false;
          if (op.level !== undefined && (/^H([1-6])$/.exec(e.nodeName) || [])[1] != op.level && e.getAttribute('aria-level') != op.level) return false;
          if (!op.includeHidden && ocultoParaAria(e)) return false;
          if (op.disabled !== undefined && deshabilitado(e) !== !!op.disabled) return false;
          if (op.checked !== undefined && !!e.checked !== !!op.checked) return false;
          if (op.selected !== undefined && !!e.selected !== !!op.selected) return false;
          return !cmpNombre || cmpNombre(nombreAccesible(e));
        });
      };
    },
    label: function (texto, op) {
      var cmp = comparador(texto, op && op.exact);
      return function (raiz) { return todos(raiz).filter(function (e) { return etiquetasDe(e).some(cmp); }); };
    },
    text: function (texto, op) {
      var cmp = comparador(texto, op && op.exact);
      return function (raiz) {
        var candidatos = (raiz.nodeType === 1 ? [raiz] : []).concat(todos(raiz));
        return candidatos.filter(function (e) { return coincideTexto(e, cmp) === 'self'; });
      };
    },
    testid: function (id) { return function (raiz) { return todos(raiz).filter(function (e) { return e.getAttribute('data-testid') === id; }); }; },
    placeholder: function (t, op) { return porAtributo('placeholder', t, op && op.exact); },
    title: function (t, op) { return porAtributo('title', t, op && op.exact); },
    alt: function (t, op) { return porAtributo('alt', t, op && op.exact); },
    selector: function (sel) { return function (raiz) { return seleccionar(raiz, sel); }; },
  };

  // locator('…'): CSS (con :has-text, :text, :text-is y :visible de Playwright), xpath=…, css=…, text=…, y cadenas con >>
  function partirCadena(sel) {
    var partes = [], q = null, ini = 0;
    for (var i = 0; i < sel.length; i++) {
      var c = sel[i];
      if (q) { if (c === '\\') i++; else if (c === q) q = null; continue; }
      if (c === '"' || c === "'") { q = c; continue; }
      if (c === '>' && sel[i + 1] === '>') { partes.push(sel.slice(ini, i).trim()); ini = i + 2; i++; }
    }
    partes.push(sel.slice(ini).trim());
    return partes;
  }
  function seleccionar(raiz, sel) {
    var partes = partirCadena(sel), actuales = [raiz];
    partes.forEach(function (p) {
      var res = [];
      actuales.forEach(function (r) { res = res.concat(seleccionarUno(r, p)); });
      actuales = ordenar(res);
    });
    return actuales;
  }
  function quitarComillas(s) { s = s.trim(); return /^(["']).*\1$/.test(s) ? s.slice(1, -1) : s; }
  function seleccionarUno(raiz, sel) {
    var doc = raiz.ownerDocument || raiz;
    if (/^xpath=/.test(sel) || /^\(*\/\//.test(sel) || /^\.\./.test(sel) || /^\/[a-z]/i.test(sel)) {
      var xp = sel.replace(/^xpath=/, '');
      if (raiz.nodeType === 1 && xp[0] === '/') xp = '.' + xp;
      var r;
      try { r = doc.evaluate(xp, raiz, null, 7, null); }
      catch (e) { throw new Error('Error: la expresión XPath no es válida: ' + xp); }
      var out = [];
      for (var i = 0; i < r.snapshotLength; i++) if (r.snapshotItem(i).nodeType === 1) out.push(r.snapshotItem(i));
      return out;
    }
    if (/^text=/.test(sel)) {
      var t = sel.slice(5), exacto = /^(["']).*\1$/.test(t.trim());
      return BUSCAR.text(quitarComillas(t), { exact: exacto })(raiz);
    }
    if (/^id=/.test(sel)) return todos(raiz).filter(function (e) { return e.id === quitarComillas(sel.slice(3)); });
    if (/^data-testid=/.test(sel)) return BUSCAR.testid(quitarComillas(sel.slice(12)))(raiz);
    if (/^internal:/.test(sel)) throw new Error('Error: el laboratorio no entiende los selectores internal:. Usa getByRole, getByLabel… directamente.');
    return css(raiz, sel.replace(/^css=/, ''), doc);
  }
  function css(raiz, sel, doc) {
    var marcas = [], n = 0;
    var limpio = sel.replace(/:(has-text|text-is|text|visible)(\((?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|[^)]*)\))?/g, function (m, tipo, arg) {
      var attr = 'data-lab-p' + (n++), elementos;
      var valor = arg ? quitarComillas(arg.slice(1, -1)) : '';
      if (tipo === 'visible') elementos = todos(doc).filter(visible);
      else if (tipo === 'has-text') { var c1 = comparador(valor); elementos = todos(doc).filter(function (e) { return !saltaTexto(e) && c1(textoDe(e)); }); }
      else { var c2 = comparador(valor, tipo === 'text-is'); elementos = todos(doc).filter(function (e) { return coincideTexto(e, c2) === 'self'; }); }
      elementos.forEach(function (e) { e.setAttribute(attr, ''); });
      marcas.push(attr);
      return '[' + attr + ']';
    });
    try { return Array.prototype.slice.call(raiz.querySelectorAll(limpio)); }
    catch (e) { throw new Error('Error: «' + sel + '» no es un selector CSS válido.'); }
    finally { marcas.forEach(function (a) { todos(doc).forEach(function (e) { e.removeAttribute(a); }); }); }
  }

  // ---------- cómo Playwright muestra un elemento en sus mensajes
  var VACIOS = { AREA: 1, BASE: 1, BR: 1, COL: 1, EMBED: 1, HR: 1, IMG: 1, INPUT: 1, LINK: 1, META: 1, PARAM: 1, SOURCE: 1, TRACK: 1, WBR: 1 };
  var BOOLEANOS = { checked: 1, selected: 1, disabled: 1, readonly: 1, multiple: 1 };
  function vista(el) {
    var attrs = [];
    for (var i = 0; i < el.attributes.length; i++) {
      var a = el.attributes[i];
      if (a.name === 'style' || a.name.indexOf('data-lab-') === 0) continue;
      attrs.push(!a.value && BOOLEANOS[a.name] ? ' ' + a.name : ' ' + a.name + '="' + a.value + '"');
    }
    attrs.sort(function (x, y) { return x.length - y.length; });
    var tag = el.nodeName.toLowerCase(), at = recortar(attrs.join(''), 500);
    if (VACIOS[el.nodeName]) return unaLinea('<' + tag + at + '/>');
    var hijos = el.childNodes, soloTexto = hijos.length <= 5;
    for (var j = 0; soloTexto && j < hijos.length; j++) soloTexto = hijos[j].nodeType === 3;
    var texto = soloTexto ? (el.textContent || '') : (hijos.length ? '…' : '');
    return unaLinea('<' + tag + at + '>' + recortar(texto, 50) + '</' + tag + '>');
  }
  /** «aka»: un localizador que sí encuentra ese elemento. Aproximado: Playwright usa un generador más completo. */
  function aka(el) {
    var rol = rolDe(el);
    if (rol && !ocultoParaAria(el) && ['combobox', 'listbox'].indexOf(rol) < 0) {
      var n = nombreAccesible(el);
      if (n && ['button', 'link', 'heading', 'textbox', 'searchbox', 'spinbutton', 'checkbox', 'radio', 'tab', 'option', 'menuitem', 'cell', 'img', 'switch', 'slider'].indexOf(rol) >= 0) {
        return 'getByRole(' + comillas(rol) + ', { name: ' + comillas(n) + ' })';
      }
    }
    if (el.getAttribute('data-testid')) return 'getByTestId(' + comillas(el.getAttribute('data-testid')) + ')';
    var et = etiquetasDe(el).map(normalizar).filter(Boolean)[0];
    if (et) return 'getByLabel(' + comillas(et) + ')';
    var tx = normalizar(textoDe(el)), contenedor = el.childElementCount > 0 && tx.length > 30;
    if (el.id && contenedor) return "locator('#" + el.id + "')";
    if (tx) return 'getByText(' + comillas(tx.length > 30 ? tx.slice(0, 27).trim() : tx) + ')';
    if (el.id) return "locator('#" + el.id + "')";
    return 'locator(' + comillas(el.nodeName.toLowerCase()) + ')';
  }
  function listaDeElementos(els) {
    return els.slice(0, 10).map(function (e, i) { return '    ' + (i + 1) + ') ' + vista(e) + ' aka ' + aka(e); }).join('\n') +
      (els.length > 10 ? '\n    ...' : '');
  }
  function mensajeEstricto(loc, els) {
    return 'strict mode violation: ' + loc + ' resolved to ' + els.length + ' elements:\n' + listaDeElementos(els);
  }
  function errorPW(texto) { var e = new Error(texto); e.esPlaywright = true; return e; }

  // ---------- estado de un elemento
  function deshabilitado(el) {
    if (/^(BUTTON|INPUT|SELECT|TEXTAREA|OPTION|OPTGROUP|FIELDSET)$/.test(el.nodeName) && el.matches(':disabled')) return true;
    for (var e = el; e; e = e.parentElement) if ((e.getAttribute('aria-disabled') || '').toLowerCase() === 'true') return true;
    return false;
  }
  function apuntar(el) { return el.nodeName === 'LABEL' && el.control ? el.control : el; } // Playwright usa el campo de un <label>
  function disparar(el, tipo) { el.dispatchEvent(new el.ownerDocument.defaultView.Event(tipo, { bubbles: true })); }

  // ---------- el Localizador: perezoso, como en Playwright (no busca hasta que se usa)
  function Localizador(page, pasos, texto) { this._page = page; this._pasos = pasos; this._texto = texto; }
  Localizador.prototype.__esLocalizador = true;
  Localizador.prototype.toString = function () { return this._texto; };
  Localizador.prototype._resolver = function () {
    var doc = this._page._documento();
    if (!doc) return [];
    var actuales = [doc];
    this._pasos.forEach(function (p) {
      if (p.tipo === 'nth') { var i = p.i < 0 ? actuales.length + p.i : p.i; actuales = actuales[i] ? [actuales[i]] : []; return; }
      if (p.tipo === 'or') { actuales = ordenar(actuales.filter(function (e) { return e.nodeType === 1; }).concat(p.otro._resolver())); return; }
      if (p.tipo === 'filtro') { actuales = actuales.filter(p.fn); return; }
      var res = [];
      actuales.forEach(function (raiz) { res = res.concat(p.fn(raiz)); });
      actuales = ordenar(res);
    });
    return actuales.filter(function (e) { return e.nodeType === 1; });
  };
  function encadenar(base, paso, texto) {
    var pasos = base ? base._pasos.concat([paso]) : [paso];
    return new Localizador(base ? base._page : paso.page, pasos, base ? base._texto + '.' + texto : texto);
  }
  function opcionesTexto(op) {
    if (!op) return '';
    var partes = [];
    Object.keys(op).forEach(function (k) { if (op[k] !== undefined && !(k === 'exact' && !op[k])) partes.push(k + ': ' + literal(op[k])); });
    return partes.length ? ', { ' + partes.join(', ') + ' }' : '';
  }
  var METODOS = {
    getByRole: function (rol, op) { return { fn: BUSCAR.role(rol, op), texto: 'getByRole(' + comillas(rol) + opcionesTexto(op) + ')' }; },
    getByLabel: function (t, op) { return { fn: BUSCAR.label(t, op), texto: 'getByLabel(' + literal(t) + opcionesTexto(op) + ')' }; },
    getByText: function (t, op) { return { fn: BUSCAR.text(t, op), texto: 'getByText(' + literal(t) + opcionesTexto(op) + ')' }; },
    getByTestId: function (t) { return { fn: BUSCAR.testid(t), texto: 'getByTestId(' + literal(t) + ')' }; },
    getByPlaceholder: function (t, op) { return { fn: BUSCAR.placeholder(t, op), texto: 'getByPlaceholder(' + literal(t) + opcionesTexto(op) + ')' }; },
    getByTitle: function (t, op) { return { fn: BUSCAR.title(t, op), texto: 'getByTitle(' + literal(t) + opcionesTexto(op) + ')' }; },
    getByAltText: function (t, op) { return { fn: BUSCAR.alt(t, op), texto: 'getByAltText(' + literal(t) + opcionesTexto(op) + ')' }; },
    locator: function (sel) {
      if (sel && sel.__esLocalizador) throw new Error('El laboratorio solo acepta locator(\'selector\') con un texto.');
      if (typeof sel !== 'string') throw new Error('locator() necesita un selector entre comillas, por ejemplo locator(\'#saldo\').');
      return { fn: BUSCAR.selector(sel), texto: 'locator(' + comillas(sel) + ')' };
    },
  };
  Object.keys(METODOS).forEach(function (m) {
    Localizador.prototype[m] = function () { var r = METODOS[m].apply(null, arguments); return encadenar(this, { tipo: 'buscar', fn: r.fn }, r.texto); };
  });
  Localizador.prototype.first = function () { return encadenar(this, { tipo: 'nth', i: 0 }, 'first()'); };
  Localizador.prototype.last = function () { return encadenar(this, { tipo: 'nth', i: -1 }, 'last()'); };
  Localizador.prototype.nth = function (i) { return encadenar(this, { tipo: 'nth', i: i }, 'nth(' + i + ')'); };
  Localizador.prototype.or = function (otro) { return encadenar(this, { tipo: 'or', otro: otro }, 'or(' + otro + ')'); };
  Localizador.prototype.filter = function (op) {
    op = op || {};
    var si = op.hasText !== undefined ? comparador(op.hasText) : null, no = op.hasNotText !== undefined ? comparador(op.hasNotText) : null;
    return encadenar(this, { tipo: 'filtro', fn: function (e) { var t = textoDe(e); return (!si || si(t)) && (!no || !no(t)); } }, 'filter(' + opcionesTexto(op).slice(2) + ')');
  };

  // Esperar a que haya UN elemento que cumpla la condición (modo estricto incluido), como una acción de Playwright.
  function esperarUno(loc, accion, condicion, motivo) {
    var t0 = Date.now(), ultimo = null;
    function intento() {
      var els = loc._resolver();
      if (els.length > 1) return Promise.reject(errorPW('locator.' + accion + ': Error: ' + mensajeEstricto(loc, els) + '\n\nCall log:\n  - waiting for ' + loc + '\n'));
      if (els.length === 1) {
        var el = els[0];
        if (!condicion || condicion(el)) return Promise.resolve(el);
        ultimo = el;
      }
      if (Date.now() - t0 >= TIEMPO) {
        var log = '\nCall log:\n  - waiting for ' + loc;
        if (ultimo) log += '\n    - locator resolved to ' + vista(ultimo) + '\n  - attempting ' + accion + ' action\n    - waiting for element to be ' + motivo.espera + '\n      - ' + motivo.fallo(ultimo);
        return Promise.reject(errorPW('locator.' + accion + ': Timeout ' + TIEMPO + 'ms exceeded.' + log + '\n'));
      }
      return dormir(50).then(intento);
    }
    return intento();
  }
  var LISTO = {
    espera: 'visible, enabled and stable',
    fallo: function (el) { return !visible(el) ? 'element is not visible' : 'element is not enabled'; },
  };
  function listoParaClic(el) { return visible(el) && !deshabilitado(el); }
  Localizador.prototype.count = function () { return Promise.resolve(this._resolver().length); };
  Localizador.prototype.all = function () { var self = this; return Promise.resolve(this._resolver().map(function (e, i) { return self.nth(i); })); };
  Localizador.prototype.click = function () {
    return esperarUno(this, 'click', listoParaClic, LISTO).then(function (el) { el.focus(); el.click(); return dormir(20); });
  };
  Localizador.prototype.fill = function (valor) {
    var loc = this;
    return esperarUno(this, 'fill', function (el) { el = apuntar(el); return visible(el) && !deshabilitado(el) && !el.readOnly; },
      { espera: 'visible, enabled and editable', fallo: function (el) { el = apuntar(el); return !visible(el) ? 'element is not visible' : deshabilitado(el) ? 'element is not enabled' : 'element is not editable'; } })
      .then(function (el) {
        el = apuntar(el);
        var tipo = (el.type || '').toLowerCase();
        var esCampo = (el.nodeName === 'INPUT' && ['checkbox', 'radio', 'file', 'button', 'submit', 'reset', 'image', 'range', 'color'].indexOf(tipo) < 0) || el.nodeName === 'TEXTAREA' || el.isContentEditable;
        if (!esCampo) throw errorPW('locator.fill: Error: Element is not an <input>, <textarea> or [contenteditable] element\nCall log:\n  - waiting for ' + loc + '\n    - locator resolved to ' + vista(el) + '\n    - fill(' + JSON.stringify(String(valor)) + ')\n');
        el.focus();
        if (el.isContentEditable) el.textContent = String(valor); else el.value = String(valor);
        disparar(el, 'input'); disparar(el, 'change');
        return dormir(10);
      });
  };
  Localizador.prototype.selectOption = function (valores) {
    var loc = this, lista = [].concat(valores);
    var t0 = Date.now();
    function intento() {
      return esperarUno(loc, 'selectOption', function (el) { el = apuntar(el); return visible(el) && !deshabilitado(el); },
        { espera: 'visible and enabled', fallo: function (el) { return !visible(apuntar(el)) ? 'element is not visible' : 'element is not enabled'; } })
        .then(function (el) {
          el = apuntar(el);
          if (el.nodeName !== 'SELECT') throw errorPW('locator.selectOption: Error: Element is not a <select> element\nCall log:\n  - waiting for ' + loc + '\n    - locator resolved to ' + vista(el) + '\n  - attempting select option action\n    - waiting for element to be visible and enabled\n');
          var opciones = Array.prototype.slice.call(el.options);
          var elegidas = lista.map(function (v) {
            return opciones.filter(function (o) {
              if (typeof v === 'object' && v) return (v.value !== undefined && o.value === v.value) || (v.label !== undefined && o.label === v.label) || (v.index !== undefined && o.index === v.index);
              return o.value === String(v) || o.label === String(v);
            })[0];
          });
          if (elegidas.some(function (o) { return !o; })) {
            if (Date.now() - t0 >= TIEMPO) throw errorPW('locator.selectOption: Timeout ' + TIEMPO + 'ms exceeded.\nCall log:\n  - waiting for ' + loc + '\n    - locator resolved to ' + vista(el) + '\n  - attempting select option action\n    - waiting for element to be visible and enabled\n      - did not find some options\n');
            return dormir(100).then(intento);
          }
          opciones.forEach(function (o) { o.selected = elegidas.indexOf(o) >= 0; });
          disparar(el, 'input'); disparar(el, 'change');
          return elegidas.map(function (o) { return o.value; });
        });
    }
    return intento();
  };
  Localizador.prototype.innerText = function () { return esperarUno(this, 'innerText').then(function (el) { return el.innerText; }); };
  Localizador.prototype.textContent = function () { return esperarUno(this, 'textContent').then(function (el) { return el.textContent; }); };
  Localizador.prototype.inputValue = function () { return esperarUno(this, 'inputValue').then(function (el) { return apuntar(el).value; }); };
  Localizador.prototype.getAttribute = function (n) { return esperarUno(this, 'getAttribute').then(function (el) { return el.getAttribute(n); }); };
  Localizador.prototype.isVisible = function () {
    var els = this._resolver();
    if (els.length > 1) return Promise.reject(errorPW('locator.isVisible: Error: ' + mensajeEstricto(this, els) + '\n\nCall log:\n  - checking visibility of ' + this + '\n'));
    return Promise.resolve(els.length === 1 && visible(els[0]));
  };
  Localizador.prototype.isHidden = function () { return this.isVisible().then(function (v) { return !v; }); };
  Localizador.prototype.isEnabled = function () { return esperarUno(this, 'isEnabled').then(function (el) { return !deshabilitado(el); }); };
  Localizador.prototype.waitFor = function (op) {
    var estado = (op && op.state) || 'visible', loc = this, t0 = Date.now();
    function intento() {
      var els = loc._resolver();
      if (els.length > 1 && estado !== 'detached') return Promise.reject(errorPW('locator.waitFor: Error: ' + mensajeEstricto(loc, els) + '\n\nCall log:\n  - waiting for ' + loc + ' to be ' + estado + '\n'));
      var el = els[0], ok = estado === 'attached' ? !!el : estado === 'detached' ? !el : estado === 'visible' ? !!el && visible(el) : !el || !visible(el);
      if (ok) return Promise.resolve();
      if (Date.now() - t0 >= TIEMPO) return Promise.reject(errorPW('locator.waitFor: Timeout ' + TIEMPO + 'ms exceeded.\nCall log:\n  - waiting for ' + loc + ' to be ' + estado + '\n'));
      return dormir(50).then(intento);
    }
    return intento();
  };
  ['check', 'uncheck', 'hover', 'press', 'type', 'pressSequentially', 'dblclick', 'focus', 'screenshot', 'evaluate', 'dragTo', 'setInputFiles'].forEach(function (m) {
    Localizador.prototype[m] = function () { return Promise.reject(new Error('locator.' + m + ' no está en este laboratorio simplificado (el Playwright real sí lo tiene). Usa click, fill o selectOption.')); };
  });

  // ---------- expect(localizador): aserciones que REINTENTAN hasta 5 s (auto-wait), con los mensajes de Playwright
  function fmtEsperado(v) { return v instanceof RegExp ? String(v) : typeof v === 'string' ? JSON.stringify(v) : String(v); }
  function aserciones(loc, mensaje) {
    function crear(negado) {
      function revisar(nombre, firma, esperadoTxt, opciones, medir) {
        var t0 = Date.now(), timeout = (opciones && opciones.timeout) || TIEMPO, intentos = 0;
        var cab = (mensaje ? mensaje + '\n\n' : '') + 'expect(locator)' + (negado ? '.not' : '') + '.' + nombre + '(' + firma + ') failed\n\n';
        var log = '\nCall log:\n  - Expect "' + (negado ? 'not ' : '') + nombre + '" ' + loc + ' with timeout ' + timeout + 'ms\n  - waiting for ' + loc;
        function intento() {
          intentos++;
          var els = loc._resolver(), r;
          if (nombre !== 'toHaveCount' && els.length > 1) {
            return Promise.reject(errorPW(cab + 'Locator: ' + loc + '\nExpected: ' + esperadoTxt + '\nError: ' + mensajeEstricto(loc, els) + '\n' + log + '\n'));
          }
          r = medir(els);
          if (r.ok !== negado) return Promise.resolve();
          if (Date.now() - t0 >= timeout) {
            if (r.noEncontrado && !negado) return Promise.reject(errorPW(cab + 'Locator: ' + loc + '\nExpected: ' + esperadoTxt + '\nTimeout: ' + timeout + 'ms\nError: element(s) not found\n' + log + '\n'));
            var resuelto = els.length === 1 ? vista(els[0]) : els.length + ' elements';
            return Promise.reject(errorPW(cab + 'Locator:  ' + loc + '\nExpected: ' + (negado ? 'not ' : '') + esperadoTxt + '\nReceived: ' + r.recibido + '\nTimeout:  ' + timeout + 'ms\n' + log +
              '\n    ' + intentos + ' × locator resolved to ' + resuelto + '\n       - unexpected value ' + JSON.stringify(String(r.recibidoCrudo !== undefined ? r.recibidoCrudo : r.recibido).replace(/^"|"$/g, '')) + '\n'));
          }
          return dormir(100).then(intento);
        }
        return intento();
      }
      function texto(nombre, parcial) {
        return function (esperado, op) {
          var cmp = esperado instanceof RegExp ? function (t) { esperado.lastIndex = 0; return esperado.test(t); }
            : parcial ? function (t) { return t.indexOf(normalizar(esperado)) >= 0; } : function (t) { return t === normalizar(esperado); };
          return revisar(nombre, 'expected', fmtEsperado(esperado), op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var t = normalizar(op && op.useInnerText ? els[0].innerText : els[0].textContent);
            return { ok: cmp(t), recibido: JSON.stringify(t), recibidoCrudo: t };
          });
        };
      }
      var m = {
        toHaveText: texto('toHaveText', false),
        toContainText: texto('toContainText', true),
        toBeVisible: function (op) {
          return revisar('toBeVisible', '', 'visible', op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true, recibido: 'hidden' };
            var v = visible(els[0]); return { ok: v, recibido: v ? 'visible' : 'hidden' };
          });
        },
        toBeHidden: function (op) {
          return revisar('toBeHidden', '', 'hidden', op, function (els) { var v = els.length === 1 && visible(els[0]); return { ok: !v, recibido: v ? 'visible' : 'hidden' }; });
        },
        toBeEnabled: function (op) {
          return revisar('toBeEnabled', '', 'enabled', op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var d = deshabilitado(els[0]); return { ok: !d, recibido: d ? 'disabled' : 'enabled' };
          });
        },
        toBeDisabled: function (op) {
          return revisar('toBeDisabled', '', 'disabled', op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var d = deshabilitado(els[0]); return { ok: d, recibido: d ? 'disabled' : 'enabled' };
          });
        },
        toHaveCount: function (n, op) {
          return revisar('toHaveCount', 'expected', String(n), op, function (els) { return { ok: els.length === n, recibido: String(els.length) }; });
        },
        toHaveValue: function (v, op) {
          return revisar('toHaveValue', 'expected', fmtEsperado(v), op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var el = apuntar(els[0]);
            if (!/^(INPUT|SELECT|TEXTAREA)$/.test(el.nodeName)) return { ok: false, recibido: 'Error: Not an input element', recibidoCrudo: 'Not an input element' };
            var ok = v instanceof RegExp ? v.test(el.value) : el.value === String(v);
            return { ok: ok, recibido: JSON.stringify(el.value), recibidoCrudo: el.value };
          });
        },
        toHaveAccessibleName: function (nombre, op) {
          return revisar('toHaveAccessibleName', 'expected', fmtEsperado(nombre), op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var n = nombreAccesible(els[0]);
            var ok = nombre instanceof RegExp ? nombre.test(n) : (op && op.ignoreCase ? n.toLowerCase() === normalizar(nombre).toLowerCase() : n === normalizar(nombre));
            return { ok: ok, recibido: JSON.stringify(n), recibidoCrudo: n };
          });
        },
        toHaveAttribute: function (attr, v, op) {
          return revisar('toHaveAttribute', 'expected', fmtEsperado(v), op, function (els) {
            if (!els.length) return { ok: false, noEncontrado: true };
            var a = els[0].getAttribute(attr);
            var ok = v === undefined ? a !== null : v instanceof RegExp ? a !== null && v.test(a) : a === String(v);
            return { ok: ok, recibido: JSON.stringify(a), recibidoCrudo: a };
          });
        },
      };
      return m;
    }
    var si = crear(false);
    si.not = crear(true);
    return si;
  }

  // ---------- page falso: lo que una prueba usa de "page" en este laboratorio
  function crearPagina(opciones) {
    var page = {
      _documento: function () { return opciones.documento(); },
      goto: function (url) { return opciones.ir ? opciones.ir(String(url)) : Promise.resolve(); },
      url: function () { return opciones.url ? opciones.url() : 'about:blank'; },
      waitForTimeout: function (ms) { return dormir(ms); },
      waitForLoadState: function () { return Promise.resolve(); },
    };
    Object.keys(METODOS).forEach(function (m) {
      page[m] = function () { var r = METODOS[m].apply(null, arguments); return new Localizador(page, [{ tipo: 'buscar', fn: r.fn }], r.texto); };
    });
    ['fill', 'click', 'selectOption', 'innerText', 'textContent', 'isVisible'].forEach(function (m) {
      page[m] = function (sel) { var l = page.locator(sel); return l[m].apply(l, Array.prototype.slice.call(arguments, 1)); };
    });
    return page;
  }

  // ---------- el patio: leer un localizador escrito por la persona (solo literales: nada de eval)
  function tokenizar(s) {
    var toks = [], i = 0;
    while (i < s.length) {
      var c = s[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === "'" || c === '"' || c === '`') {
        var j = i + 1, v = '';
        while (j < s.length && s[j] !== c) {
          if (s[j] === '\\') { var e = s[j + 1]; v += e === 'n' ? '\n' : e === 't' ? '\t' : e; j += 2; continue; }
          if (c === '`' && s[j] === '$' && s[j + 1] === '{') throw new Error('En el patio no se pueden usar ${…} dentro de las comillas: escribe el texto tal cual.');
          v += s[j++];
        }
        if (j >= s.length) throw new Error('Falta cerrar una comilla ' + c + '.');
        toks.push({ t: 'str', v: v }); i = j + 1; continue;
      }
      if (/[A-Za-z_$]/.test(c)) { var id = /^[A-Za-z_$][\w$]*/.exec(s.slice(i))[0]; toks.push({ t: 'id', v: id }); i += id.length; continue; }
      if (/[0-9]/.test(c) || (c === '-' && /[0-9]/.test(s[i + 1] || ''))) { var num = /^-?\d+(\.\d+)?/.exec(s.slice(i))[0]; toks.push({ t: 'num', v: Number(num) }); i += num.length; continue; }
      if (c === '/') {
        var prev = toks[toks.length - 1];
        if (prev && prev.t === 'p' && '(,:'.indexOf(prev.v) >= 0) {
          var k = i + 1, cuerpo = '', clase = false;
          while (k < s.length && (s[k] !== '/' || clase)) {
            if (s[k] === '\\') { cuerpo += s[k] + (s[k + 1] || ''); k += 2; continue; }
            if (s[k] === '[') clase = true; else if (s[k] === ']') clase = false;
            cuerpo += s[k++];
          }
          if (k >= s.length) throw new Error('Falta cerrar la expresión regular con /.');
          var banderas = /^[gimsuy]*/.exec(s.slice(k + 1))[0];
          toks.push({ t: 're', v: new RegExp(cuerpo, banderas) }); i = k + 1 + banderas.length; continue;
        }
      }
      if ('.(),{}:;'.indexOf(c) >= 0) { toks.push({ t: 'p', v: c }); i++; continue; }
      throw new Error('No entiendo el carácter «' + c + '». El patio lee solo localizadores, como getByRole(\'button\', { name: \'Recargar\' }).');
    }
    return toks;
  }
  var EN_CADENA = Object.keys(METODOS).concat(['first', 'last', 'nth', 'or', 'filter']);
  var ACCIONES = ['click', 'fill', 'selectOption', 'innerText', 'textContent', 'count', 'isVisible', 'waitFor', 'inputValue', 'check', 'hover', 'press'];
  function analizar(texto) {
    var toks = tokenizar(texto), i = 0, accion = null;
    function ver(t, v) { var k = toks[i]; return k && k.t === t && (v === undefined || k.v === v); }
    function tomar(t, v, error) { if (!ver(t, v)) throw new Error(error || ('Esperaba «' + v + '» y encontré ' + (toks[i] ? '«' + (toks[i].v instanceof RegExp ? toks[i].v : toks[i].v) + '»' : 'el final') + '.')); return toks[i++]; }
    function valor() {
      var k = toks[i];
      if (!k) throw new Error('Falta un valor antes del final.');
      if (k.t === 'str' || k.t === 'num' || k.t === 're') { i++; return k.v; }
      if (k.t === 'id' && (k.v === 'true' || k.v === 'false')) { i++; return k.v === 'true'; }
      if (k.t === 'id' && k.v === 'undefined') { i++; return undefined; }
      if (k.t === 'p' && k.v === '{') {
        i++; var obj = {};
        while (!ver('p', '}')) {
          var clave = toks[i]; if (!clave || (clave.t !== 'id' && clave.t !== 'str')) throw new Error('Dentro de { } va un nombre, por ejemplo { name: \'Recargar\' }.');
          i++; tomar('p', ':'); obj[clave.v] = valor();
          if (ver('p', ',')) i++; else break;
        }
        tomar('p', '}');
        return obj;
      }
      if (k.t === 'id') return { cadena: cadena() };
      throw new Error('No entiendo «' + k.v + '».');
    }
    function cadena() {
      if (ver('id', 'await')) i++;
      if (ver('id', 'this') && toks[i + 1] && toks[i + 1].v === '.') i += 2;
      if (ver('id', 'page') && toks[i + 1] && toks[i + 1].v === '.') i += 2;
      var pasos = [];
      while (true) {
        var m = tomar('id', undefined, 'Esperaba un método, como getByRole o locator.').v;
        tomar('p', '(');
        var args = [];
        while (!ver('p', ')')) { args.push(valor()); if (ver('p', ',')) i++; else break; }
        tomar('p', ')');
        if (EN_CADENA.indexOf(m) < 0) {
          if (ACCIONES.indexOf(m) >= 0 && pasos.length) { accion = m; break; }
          throw new Error('El patio no conoce «' + m + '». Usa getByRole, getByLabel, getByText, getByTestId, getByPlaceholder, locator, first, last, nth, or o filter.');
        }
        if (!pasos.length && ['first', 'last', 'nth', 'or', 'filter'].indexOf(m) >= 0) throw new Error('Empieza con page.getBy… o page.locator(…), y después ' + m + '().');
        pasos.push({ m: m, args: args });
        if (ver('p', '.')) { i++; continue; }
        break;
      }
      return pasos;
    }
    var pasos = cadena();
    if (ver('p', ';')) i++;
    if (i < toks.length) throw new Error('Sobra algo al final: «' + toks[i].v + '». Escribe un solo localizador.');
    return { pasos: pasos, accion: accion };
  }
  function construir(pasos, page) {
    var loc = page;
    pasos.forEach(function (p) {
      var args = p.args.map(function (a) { return a && a.cadena ? construir(a.cadena, page) : a; });
      if (typeof loc[p.m] !== 'function') throw new Error('«' + p.m + '» no se puede usar ahí.');
      loc = loc[p.m].apply(loc, args);
    });
    if (!loc || !loc.__esLocalizador) throw new Error('Eso no es un localizador.');
    return loc;
  }
  /** Lo que el patio muestra para una versión de la pantalla: cuántos, cuáles y el mensaje que daría Playwright. */
  function probar(texto, page) {
    var a = analizar(texto), loc = construir(a.pasos, page), els = loc._resolver();
    var r = { localizador: String(loc), cuantos: els.length, elementos: els, accion: a.accion };
    r.detalle = els.map(function (e) { return { vista: vista(e), aka: aka(e), visible: visible(e) }; });
    if (els.length > 1) r.mensaje = 'Error: locator.click: Error: ' + mensajeEstricto(loc, els) + '\n\nCall log:\n  - waiting for ' + loc;
    else if (!els.length) r.mensaje = 'Error: locator.click: Timeout ' + TIEMPO + 'ms exceeded.\nCall log:\n  - waiting for ' + loc;
    else r.mensaje = '';
    return r;
  }

  return {
    TIEMPO: TIEMPO, dormir: dormir, crearPagina: crearPagina, aserciones: aserciones, probar: probar, analizar: analizar,
    vista: vista, aka: aka, visible: visible, nombreAccesible: nombreAccesible, rolDe: rolDe,
  };
})();

/*
 * EL BANCO DEMO SIMULADO: lo mínimo que hace la pantalla de Recargas, sin servidor ni red.
 * Copia la lógica de banco-demo/public/recargas.html (y las reglas de banco-demo/reglas.js):
 * el saldo llega 600 ms después (a propósito: para ver que toHaveText espera solo), el formulario
 * valida con las reglas del banco y el comprobante sale con role="status".
 */
var BancoSimulado = (function () {
  'use strict';
  var ID = {
    hoy: { saldo: 'saldo', form: 'f', operador: 'operador', numero: 'numero', valor: 'valor', boton: 'recargar',
      formCodigo: 'fc', codigo: 'codigo', comprobante: 'comprobante', numeroComprobante: 'numeroComprobante', valorRecargado: 'valorRecargado' },
    'rediseño': { saldo: 'rd-saldo-ahorros', form: 'rd-form-recarga', operador: 'rd-operador', numero: 'rd-celular', valor: 'rd-monto', boton: 'rd-enviar',
      formCodigo: 'rd-form-codigo', codigo: 'rd-codigo', comprobante: 'rd-aviso-ok', numeroComprobante: 'rd-comprobante-numero', valorRecargado: 'rd-comprobante-valor' },
  };
  var OPERADORES = ['Claro', 'Movistar', 'Tigo', 'WOM'];
  function pesos(n) { return '$' + String(Math.round(Number(n))).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function validar(r, s) {
    if (OPERADORES.indexOf(r.operador) < 0) return 'Elige un operador';
    if (!/^3\d{9}$/.test(String(r.numero == null ? '' : r.numero))) return 'El celular debe tener 10 dígitos y empezar por 3';
    if (!Number.isInteger(r.monto) || r.monto <= 0) return 'El monto debe ser un número entero positivo';
    if (r.monto < 1000) return 'La recarga mínima es $1.000';
    if (r.monto > 100000) return 'La recarga máxima es $100.000';
    if (s.recargadoHoy + r.monto > 200000) return 'Superaste el límite diario de recargas ($200.000)';
    if (r.monto > s.saldo) return 'Saldo insuficiente';
    return null;
  }
  function nuevaSesion() { return { saldo: 1500000, recargadoHoy: 0, comprobante: 482913 }; }

  /** Carga la pantalla en el iframe (sin ejecutar sus scripts) y le conecta la lógica simulada. */
  function montar(marco, html, version, sesion, opciones) {
    opciones = opciones || {};
    return new Promise(function (listo) {
      marco.onload = function () {
        var doc = marco.contentDocument, id = ID[version];
        if (version === 'rediseño') doc.querySelector('main').replaceWith(doc.getElementById('plantilla-rediseno').content.cloneNode(true));
        var el = function (k) { return doc.getElementById(id[k]); };
        var nombre = doc.getElementById('nombre'); if (nombre) nombre.textContent = 'Ana Pérez';
        doc.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('a[href]'); if (a) e.preventDefault(); }, true);
        function pintarError(t) { var caja = doc.getElementById('error') || doc.querySelector('[role="alert"]'); caja.textContent = t; caja.hidden = !t; }
        function saldo(demora) { setTimeout(function () { el('saldo').textContent = pesos(sesion.saldo); }, demora); }
        if (opciones.saldoInmediato) el('saldo').textContent = pesos(sesion.saldo); else saldo(600);
        function mostrar(estado, datos) {
          var boton = el('boton'); boton.disabled = false; boton.textContent = 'Recargar';
          if (estado === 202) { el('form').hidden = true; el('formCodigo').hidden = false; return; }
          el('form').hidden = false; el('formCodigo').hidden = true;
          saldo(600);
          if (estado !== 201) return pintarError(datos.error || 'No pudimos hacer la recarga. Intenta más tarde.');
          var c = el('comprobante');
          c.innerHTML = '<strong>Recarga exitosa</strong><br>Comprobante: <span id="' + id.numeroComprobante + '">' + datos.comprobante + '</span><br>' +
            datos.operador + ' · ' + datos.numero + '<br>Valor: <span id="' + id.valorRecargado + '">' + pesos(datos.monto) + '</span>';
          c.hidden = false;
        }
        doc.addEventListener('submit', function (e) {
          e.preventDefault();
          if (e.target.id === id.form) {
            pintarError(''); el('comprobante').hidden = true;
            var boton = el('boton'); boton.disabled = true; boton.textContent = 'Recargando…';
            var r = { operador: el('operador').value, numero: el('numero').value.trim(), monto: Number(el('valor').value.trim()) };
            var error = validar(r, sesion);
            if (error) return setTimeout(function () { mostrar(400, { error: error }); }, 80);
            if (r.monto > 50000) return setTimeout(function () { mostrar(202, {}); }, 80);
            sesion.saldo -= r.monto;
            if (r.numero === '3000000504') return setTimeout(function () { mostrar(504, { error: 'El operador no responde. Intenta más tarde.' }); }, 1500);
            sesion.recargadoHoy += r.monto; sesion.comprobante += 7;
            setTimeout(function () { mostrar(201, { comprobante: sesion.comprobante, operador: r.operador, numero: r.numero, monto: r.monto }); }, 400);
          } else if (e.target.id === id.formCodigo) {
            pintarError('En el laboratorio no hay buzón de SMS: prueba con una recarga de $50.000 o menos.');
          }
        }, true);
        listo(doc);
      };
      marco.srcdoc = html + '\n<!-- ' + (montar.n = (montar.n || 0) + 1) + ' -->';
    });
  }
  return { montar: montar, nuevaSesion: nuevaSesion, pesos: pesos };
})();
