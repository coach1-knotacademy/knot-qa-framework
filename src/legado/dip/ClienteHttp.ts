/**
 * CÓDIGO HEREDADO · Un cliente HTTP CONCRETO: habla de verdad con el Banco Demo (usa fetch).
 * Funciona bien. El problema no es esta clase, sino quién la crea (ver ResumenAcoplado.ts).
 */
import { Cuenta } from '../../api/ClienteBanco';
import { Usuario } from '../../datos/usuarios';

export class ClienteHttp {
  private token = '';

  constructor(private readonly urlBase: string) {}

  async iniciarSesion(usuario: Usuario): Promise<void> {
    const { idDesafio } = await this.pedir('POST', '/api/login', { usuario: usuario.usuario, clave: usuario.clave });
    const [ultimo] = await this.pedir('GET', `/api/buzon?usuario=${encodeURIComponent(usuario.usuario)}`);
    const { token } = await this.pedir('POST', '/api/otp', { idDesafio, codigo: ultimo.codigo });
    this.token = token;
  }

  async cuentas(): Promise<Cuenta[]> {
    return this.pedir('GET', '/api/cuentas');
  }

  private async pedir(metodo: string, ruta: string, cuerpo?: object) {
    const respuesta = await fetch(this.urlBase + ruta, {
      method: metodo,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token}` },
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
    if (!respuesta.ok) throw new Error(`${metodo} ${ruta} respondió ${respuesta.status}`);
    return respuesta.json();
  }
}
