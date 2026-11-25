import { Operador, fabricaDeRecargas } from '../../datos/fabricaDeRecargas';
import { PaginaRecargas } from '../../paginas/PaginaRecargas';
import { Actor, Tarea } from '../Actor';
import { NavegarLaWeb } from '../navegador/NavegarLaWeb';

/**
 * TAREA (S7): recargar un celular POR LA PANTALLA.
 *   await ana.intenta(RecargarDesdeLaPantalla.celular('3001234567').por(10_000));
 *
 * Aquí se ve que Screenplay y Page Object SE COMBINAN: la tarea dice el paso de negocio
 * («recargar $10.000») y por dentro usa el Page Object, que sabe cómo se hace en la pantalla.
 * Page Object no es "para proyectos chicos": es la base sobre la que se paran las tareas.
 *
 * Es la tarea que llama el paso de Gherkin «Cuando Ana recarga $10.000 a un Claro 3001234567».
 * Tarea ≠ acción de página: recargar() de PaginaRecargas es un clic en una pantalla; esta tarea
 * es el paso con nombre de negocio, y podría juntar más pantallas (el código del buzón, por ejemplo).
 */
export class RecargarDesdeLaPantalla implements Tarea {
  private monto = fabricaDeRecargas.valida().monto;
  private operador: Operador = fabricaDeRecargas.valida().operador;

  private constructor(private readonly numero: string) {}

  static celular(numero: string): RecargarDesdeLaPantalla {
    return new RecargarDesdeLaPantalla(numero);
  }

  por(monto: number): RecargarDesdeLaPantalla {
    this.monto = monto;
    return this;
  }

  con(operador: Operador): RecargarDesdeLaPantalla {
    this.operador = operador;
    return this;
  }

  async realizadaPor(actor: Actor): Promise<void> {
    const pagina = new PaginaRecargas(actor.usa(NavegarLaWeb).page);
    await pagina.abrir();
    // El dato sale de la fábrica: la tarea solo dice lo que cambia (número, monto, operador).
    await pagina.recargar(fabricaDeRecargas.valida({ numero: this.numero, monto: this.monto, operador: this.operador }));
    actor.recuerda('resultadoDeLaRecarga', await pagina.esperarResultado());
  }
}
