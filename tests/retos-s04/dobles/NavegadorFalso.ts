/**
 * DOBLE DE PRUEBA · Un navegador falso: no abre nada, solo anota lo que le piden.
 *
 * - acciones: la lista de lo que hizo, para comprobarlo en la prueba.
 * - textos: lo que debe "leer" en pantalla. Se prepara en el constructor.
 *
 * Es el modelo para el ClienteFalso del reto 5.
 */
import { Navegador } from '../../../src/legado/navegador';

export class NavegadorFalso implements Navegador {
  readonly acciones: string[] = [];

  constructor(private readonly textos: Record<string, string> = {}) {}

  async ir(ruta: string): Promise<void> {
    this.acciones.push(`ir ${ruta}`);
  }

  async escribir(campo: string, valor: string): Promise<void> {
    this.acciones.push(`escribir ${campo}: ${valor}`);
  }

  async pulsar(boton: string): Promise<void> {
    this.acciones.push(`pulsar ${boton}`);
  }

  async leer(elemento: string): Promise<string> {
    this.acciones.push(`leer ${elemento}`);
    return this.textos[elemento] ?? '';
  }

  async capturar(archivo: string): Promise<void> {
    this.acciones.push(`capturar ${archivo}`);
  }
}
