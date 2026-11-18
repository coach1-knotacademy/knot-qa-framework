/**
 * PATRÓN SCREENPLAY (S5) · el núcleo, en 50 líneas.
 *
 * La prueba se escribe como un caso de prueba manual, contado por un actor:
 *   await ana.intenta(Transferir.desde('principal').hacia('ahorros').por(50));
 *   expect(await ana.pregunta(SaldoDe.cuenta('ahorros'))).toBe(150);
 *
 * Las cuatro piezas, comparadas con un caso manual:
 *   - ACTOR: quién ejecuta el caso (el rol: cliente, cajero, administrador).
 *   - HABILIDAD: con qué lo hace (el navegador, la API de un servicio, una billetera).
 *   - TAREA: un paso de negocio ("transferir $50 a ahorros"), que por dentro tiene varios clics.
 *   - PREGUNTA: el resultado esperado que se revisa ("¿cuál es el saldo de ahorros?").
 *
 * Page Object organiza PANTALLAS. Screenplay organiza TAREAS. Se pueden usar juntos:
 * una tarea puede llamar a un Page Object por dentro.
 */

/** Un paso de negocio que el actor puede intentar. */
export interface Tarea {
  realizadaPor(actor: Actor): Promise<void>;
}

/** Algo que el actor averigua para compararlo con el resultado esperado. */
export interface Pregunta<T> {
  respondidaPor(actor: Actor): Promise<T>;
}

/** Cualquier clase sirve de habilidad: el actor la busca por su tipo. */
type TipoDeHabilidad<T> = abstract new (...args: never[]) => T;

export class Actor {
  private readonly habilidades: object[] = [];
  private readonly memoria = new Map<string, unknown>();

  private constructor(readonly nombre: string) {}

  /** Actor.llamado('Ana') */
  static llamado(nombre: string): Actor {
    return new Actor(nombre);
  }

  /** Le da habilidades al actor: ana.puede(UsarLaApiDeParaBank.con(cliente)) */
  puede(...habilidades: object[]): Actor {
    this.habilidades.push(...habilidades);
    return this;
  }

  /** Lo usan las tareas por dentro: actor.usa(UsarLaApiDeParaBank) */
  usa<T>(tipo: TipoDeHabilidad<T>): T {
    const habilidad = this.habilidades.find((h) => h instanceof tipo);
    if (!habilidad) throw new Error(`${this.nombre} no tiene la habilidad ${tipo.name}. Dásela con .puede(...)`);
    return habilidad as T;
  }

  /** Hace las tareas en orden, como los pasos de un caso de prueba. */
  async intenta(...tareas: Tarea[]): Promise<void> {
    for (const tarea of tareas) await tarea.realizadaPor(this);
  }

  /** Responde una pregunta para compararla con el resultado esperado. */
  pregunta<T>(pregunta: Pregunta<T>): Promise<T> {
    return pregunta.respondidaPor(this);
  }

  /** El actor anota algo para un paso siguiente (por ejemplo, el número de la cuenta que abrió). */
  recuerda(clave: string, valor: unknown): void {
    this.memoria.set(clave, valor);
  }

  recuerdo<T>(clave: string): T {
    if (!this.memoria.has(clave)) throw new Error(`${this.nombre} no recuerda "${clave}". ¿Faltó una tarea antes?`);
    return this.memoria.get(clave) as T;
  }
}
