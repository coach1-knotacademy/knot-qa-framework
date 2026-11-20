/**
 * FÁBRICA DE DATOS: un solo lugar arma una recarga válida. La prueba pide lo que necesita con un
 * nombre de negocio y solo escribe lo que le importa. Nunca datos reales: solo datos de prueba.
 */

export type Operador = 'Claro' | 'Movistar' | 'Tigo' | 'WOM';

export interface Recarga {
  operador: Operador;
  numero: string;
  monto: number;
}

export const fabricaDeRecargas = {
  /**
   * Una recarga que el banco acepta sin pedir nada más (hasta $50.000 no pide código).
   *   fabricaDeRecargas.valida({ operador: 'Tigo' })
   * Cada llamada entrega un objeto NUEVO.
   */
  valida(cambios: Partial<Recarga> = {}): Recarga {
    return { operador: 'Claro', numero: '3001234567', monto: 10_000, ...cambios };
  },

  /** Más de $50.000: el banco pide un código de seguridad antes de recargar. */
  grande(cambios: Partial<Recarga> = {}): Recarga {
    return fabricaDeRecargas.valida({ monto: 60_000, ...cambios });
  },
};
