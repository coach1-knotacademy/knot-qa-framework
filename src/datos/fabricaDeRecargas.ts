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
};
