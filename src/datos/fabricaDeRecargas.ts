/**
 * PATRÓN FACTORY (fábrica de datos de prueba) · S5
 *
 * Un solo lugar sabe armar una recarga válida. La prueba pide lo que necesita con un nombre
 * de negocio ("una recarga grande", "una recarga al operador caído") y solo escribe lo que
 * le importa. Si mañana cambia una regla (por ejemplo, el monto que pide código), se corrige
 * aquí y no en 30 pruebas.
 *
 * Es lo mismo que una hoja de datos de prueba en el trabajo manual, pero con nombres.
 */

export type Operador = 'Claro' | 'Movistar' | 'Tigo' | 'WOM';

/** Lo que se necesita para recargar un celular. */
export interface Recarga {
  operador: Operador;
  numero: string;
  monto: number;
}

export const operadores: Operador[] = ['Claro', 'Movistar', 'Tigo', 'WOM'];

/**
 * Números "mágicos" del ambiente de pruebas. Con ellos el operador simulado responde siempre
 * igual, como las tarjetas de prueba de una pasarela de pagos. Así se prueban los casos difíciles.
 */
export const numerosDePrueba = {
  /** Un celular cualquiera: el operador responde bien. */
  normal: '3001234567',
  /** El operador no responde (504). Sirve para probar qué pasa con la plata del cliente. */
  operadorCaido: '3000000504',
};

/** Montos con significado de negocio. Vienen de las reglas del Banco Demo. */
export const montos = {
  /** Lo que se usa si la prueba no dice nada. */
  normal: 10_000,
  /** Más de $50.000: el banco pide un código de seguridad adicional. */
  conCodigo: 60_000,
  /** S8 · El borde: el monto más alto que todavía NO pide código. */
  maximoSinCodigo: 50_000,
};

export const fabricaDeRecargas = {
  /**
   * Una recarga que el banco acepta sin pedir nada más.
   * "cambios" deja reemplazar solo lo que le importa a la prueba:
   *   fabricaDeRecargas.valida({ operador: 'Tigo' })
   * Cada llamada entrega un objeto NUEVO: si una prueba lo modifica, no daña a las demás.
   */
  valida(cambios: Partial<Recarga> = {}): Recarga {
    return { operador: 'Claro', numero: numerosDePrueba.normal, monto: montos.normal, ...cambios };
  },

  /** Una recarga de más de $50.000: el banco pide un código antes de hacerla. */
  grande(cambios: Partial<Recarga> = {}): Recarga {
    return fabricaDeRecargas.valida({ monto: montos.conCodigo, ...cambios });
  },

  /** Una recarga al número de pruebas con el que el operador no responde. */
  aOperadorCaido(cambios: Partial<Recarga> = {}): Recarga {
    return fabricaDeRecargas.valida({ numero: numerosDePrueba.operadorCaido, ...cambios });
  },

  /** Una recarga válida por cada operador: sirve para correr la misma prueba con los cuatro. */
  paraCadaOperador(cambios: Partial<Recarga> = {}): Recarga[] {
    return operadores.map((operador) => fabricaDeRecargas.valida({ ...cambios, operador }));
  },

  // ───────────── S8 · Una prueba, muchos datos (Data Driven Testing) ─────────────
  //
  // Cada lista es la tabla «Ejemplos» de un Esquema de especificaciones/recargas-datos.feature,
  // con los MISMOS datos. Una fila = una prueba = una línea del reporte.
  //
  // La regla para que una fila entre en la tabla: MISMOS PASOS, OTRO DATO, EL MISMO TIPO DE «ENTONCES».
  // Si una fila cambia el camino o el resultado, es otro Esquema (y otra lista).
  //
  // Cada llamada entrega objetos NUEVOS, como valida(): si una prueba cambia una fila, no daña a las demás.

  /**
   * CP-104 · Montos fuera de rango: el banco rechaza y el saldo no se mueve.
   * $99.999 NO va aquí: todo monto de más de $50.000 pide código de seguridad, así que esa fila
   * sigue otro camino y tiene otro «Entonces» (va en el Esquema del CP-102).
   * $150.000 sí va: el banco revisa el máximo ANTES de pedir el código.
   */
  rechazosPorMonto(): RechazoPorMonto[] {
    return [
      { monto: 999, mensaje: mensajes.minima },
      { monto: 100_001, mensaje: mensajes.maxima },
      { monto: 150_000, mensaje: mensajes.maxima },
    ];
  },

  /** CP-103 · Celulares mal escritos: los tres dan el mismo mensaje, y cada uno prueba un pedazo de la regla. */
  celularesInvalidos(): CelularInvalido[] {
    return [
      { numero: '300123', caso: '6 dígitos' },
      { numero: '30012345678', caso: '11 dígitos' },
      { numero: '2001234567', caso: 'empieza por 2' },
    ];
  },

  /** CP-101 · Recargas válidas sin código, con el saldo que queda. $50.000 es el borde: el último monto sin código. */
  sinCodigo(): RecargaSinCodigo[] {
    return [
      { monto: 1_000, saldoFinal: 1_499_000 },
      { monto: 10_000, saldoFinal: 1_490_000 },
      { monto: 50_000, saldoFinal: 1_450_000 },
    ];
  },

  /**
   * CP-105 · Pasado el límite diario ($200.000): el dato del «Dado» (lo que ya recargó) también va en la tabla.
   * $180.000 + $20.000 NO va aquí: da justo $200.000 y PASA (el límite es «más de»). Otro resultado, otro Esquema.
   */
  pasadoElLimiteDiario(): PasadoElLimite[] {
    return [
      { yaRecargo: 190_000, monto: 20_000 },
      { yaRecargo: 200_000, monto: 1_000 },
      { yaRecargo: 160_000, monto: 50_000 },
    ];
  },

  /**
   * Las recargas que hay que hacer por API para que «hoy ya recargó» un total: de a $50.000 como máximo,
   * para que ninguna pida código. hastaHaberRecargado(190_000) → $50.000 + $50.000 + $50.000 + $40.000.
   */
  hastaHaberRecargado(total: number): Recarga[] {
    const partes: Recarga[] = [];
    for (let falta = total; falta > 0; falta -= montos.maximoSinCodigo) {
      partes.push(fabricaDeRecargas.valida({ monto: Math.min(falta, montos.maximoSinCodigo) }));
    }
    return partes;
  },
};

/** Los mensajes exactos del banco (banco-demo/reglas.js). Si cambia uno, se corrige aquí y no en cada prueba. */
export const mensajes = {
  minima: 'La recarga mínima es $1.000',
  maxima: 'La recarga máxima es $100.000',
  celular: 'El celular debe tener 10 dígitos y empezar por 3',
  limiteDiario: 'Superaste el límite diario de recargas ($200.000)',
};

/** Una fila del CP-104: el monto y el mensaje con que el banco lo rechaza. */
export interface RechazoPorMonto {
  monto: number;
  mensaje: string;
}

/** Una fila del CP-103: el celular y qué tiene de malo (va en el título de la prueba). */
export interface CelularInvalido {
  numero: string;
  caso: string;
}

/** Una fila del CP-101 sin código: el monto y el saldo de Ahorros que debe quedar. */
export interface RecargaSinCodigo {
  monto: number;
  saldoFinal: number;
}

/** Una fila del CP-105: lo que ya recargó hoy y el monto que intenta. */
export interface PasadoElLimite {
  yaRecargo: number;
  monto: number;
}

/**
 * Un monto como lo escribe el banco en la pantalla y en el Gherkin: 150000 → «$150.000».
 * Así el título de la prueba y el texto del test.step dicen lo mismo que la tabla que firma negocio.
 */
export function pesos(monto: number): string {
  // El punto cada tres cifras, a mano: sale igual en cualquier computador (no depende del idioma de Windows).
  return '$' + String(monto).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}
