/**
 * CÓDIGO HEREDADO · S de SOLID: responsabilidad única (SRP).
 *
 * Esta clase hace CINCO cosas: inicia sesión, transfiere, toma capturas, lee CSV y escribe logs.
 * Tiene cinco razones para cambiar: si cambia la pantalla, el formato del CSV, la carpeta de
 * las capturas o el formato del log, siempre se toca este mismo archivo.
 *
 * No la modifiques: es el "antes". El reto 1 de la S4 reparte sus tareas en clases pequeñas.
 */
import * as fs from 'fs';
import { Navegador } from '../navegador';

export class AyudanteTodo {
  constructor(private readonly navegador: Navegador) {}

  async iniciarSesion(usuario: string, clave: string): Promise<void> {
    this.escribirLog(`Iniciando sesión como ${usuario}`);
    await this.navegador.ir('/');
    await this.navegador.escribir('Usuario', usuario);
    await this.navegador.escribir('Clave', clave);
    await this.navegador.pulsar('Ingresar');
  }

  async transferir(destino: string, monto: number): Promise<void> {
    this.escribirLog(`Transfiriendo ${monto} a ${destino}`);
    await this.navegador.ir('/transferir');
    await this.navegador.escribir('Cuenta destino', destino);
    await this.navegador.escribir('Monto', String(monto));
    await this.navegador.pulsar('Transferir');
    await this.tomarCaptura('transferencia');
  }

  async tomarCaptura(nombre: string): Promise<void> {
    const archivo = `evidencias/${nombre}-${Date.now()}.png`;
    await this.navegador.capturar(archivo);
    this.escribirLog(`Captura guardada en ${archivo}`);
  }

  leerCasosCsv(ruta: string): Record<string, string>[] {
    const texto = fs.readFileSync(ruta, 'utf8');
    const [encabezado, ...filas] = texto.split('\n');
    const columnas = encabezado.split(';');
    return filas.map((fila) => {
      const valores = fila.split(';');
      const caso: Record<string, string> = {};
      columnas.forEach((columna, i) => (caso[columna] = valores[i]));
      return caso;
    });
  }

  escribirLog(mensaje: string): void {
    const linea = `[${new Date().toISOString()}] ${mensaje}`;
    console.log(linea);
    fs.appendFileSync('ejecucion.log', linea + '\n');
  }
}
