/**
 * PATRÓN FACTORY · los datos de la Toolshop (kit «web real»)
 *
 * Igual que fabricaDeClientes (ParaBank) y fabricaDeRecargas (Banco Demo): la prueba pide el dato
 * por su nombre de negocio ("una compra de dos unidades", "un contacto con el correo mal escrito")
 * y nunca escribe productos, cantidades ni correos a mano.
 *
 * Los productos son del catálogo de práctica del sitio. Si el sitio cambia su catálogo,
 * se cambia aquí, una sola vez.
 */

/** Lo que se busca, se filtra o se abre en el catálogo. */
export const catalogoDePrueba = {
  /** Una búsqueda que devuelve varios productos. */
  busqueda: 'Pliers',
  /** Una categoría del filtro "By category" (dentro de Hand Tools). */
  categoria: 'Hammer',
  /** Un producto con detalle completo (precio, descripción y especificaciones). */
  productoConDetalle: 'Combination Pliers',
};

/** Una compra: qué producto y cuántas unidades. */
export interface Compra {
  producto: string;
  cantidad: number;
}

export const fabricaDeCompras = {
  /** Una compra normal de un producto con existencias. Solo cambia lo que le importa a la prueba. */
  nueva(cambios: Partial<Compra> = {}): Compra {
    return { producto: 'Pliers', cantidad: 1, ...cambios };
  },
  /** Dos unidades: así se ve que el total multiplica (1 unidad no lo demuestra). */
  dosUnidades(cambios: Partial<Compra> = {}): Compra {
    return fabricaDeCompras.nueva({ cantidad: 2, ...cambios });
  },
};

/** Los datos del formulario de contacto. */
export interface Contacto {
  nombre: string;
  apellido: string;
  correo: string;
  asunto: string;
  mensaje: string;
}

export const fabricaDeContactos = {
  /** Un contacto que pasa todas las validaciones. Datos de mentira: es un sitio público. */
  valido(cambios: Partial<Contacto> = {}): Contacto {
    return {
      nombre: 'Ana',
      apellido: 'Prueba',
      correo: 'ana.prueba@example.com',
      asunto: 'Customer service',
      mensaje: 'Mensaje de prueba del bootcamp: no requiere respuesta.',
      ...cambios,
    };
  },
  /** El mismo contacto con el correo a medio escribir (sin dominio). */
  conCorreoInvalido(): Contacto {
    return fabricaDeContactos.valido({ correo: 'ana.prueba@' });
  },
};
