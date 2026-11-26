/**
 * CAPA DE DATOS: los usuarios de prueba, con nombre de negocio.
 *
 * Son los usuarios de EJEMPLO que la propia app muestra en su pantalla de login (es una app pública
 * de práctica). No son de nadie. En un proyecto real, la clave NO va aquí: sale de la capa config
 * (una variable de entorno o la bóveda del equipo), igual que CLAVE_BANCO en el framework web.
 */
export interface Usuario {
  correo: string;
  clave: string;
}

export const usuarios = {
  /** Un comprador normal: entra sin problema. */
  comprador: { correo: 'bod@example.com', clave: '10203040' },
  /** La app lo trae bloqueado a propósito, para practicar el caso negativo. */
  bloqueado: { correo: 'alice@example.com', clave: '10203040' },
  /** Sin datos: para probar que la app pide el usuario. */
  vacio: { correo: '', clave: '' },
} satisfies Record<string, Usuario>;
