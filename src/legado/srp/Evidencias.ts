/**
 * DESPUÉS (SRP) · Ejemplo ya resuelto: una clase con UNA sola tarea, guardar capturas.
 * Úsala como modelo para LectorDeCasos y Bitacora.
 *
 * ¿Y el login y la transferencia de AyudanteTodo? Ya tienen dueño desde la S3:
 * PaginaLogin y PaginaTransferir (src/paginas).
 */
import { Navegador } from '../navegador';

export class Evidencias {
  constructor(
    private readonly navegador: Navegador,
    private readonly carpeta = 'evidencias',
  ) {}

  /** Guarda una captura y devuelve la ruta del archivo. */
  async capturar(nombre: string): Promise<string> {
    const archivo = `${this.carpeta}/${nombre}.png`;
    await this.navegador.capturar(archivo);
    return archivo;
  }
}
