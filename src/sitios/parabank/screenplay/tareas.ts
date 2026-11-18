/**
 * SCREENPLAY en ParaBank (S5): la habilidad, las tareas y las preguntas.
 * Compara tests/parabank/screenplay.spec.ts con tests/parabank/cuentas.spec.ts:
 * es la misma prueba, contada de otra forma.
 */
import { Actor, Pregunta, Tarea } from '../../../screenplay/Actor';
import { ClienteParaBank, ClienteRegistrado, TipoDeCuenta } from '../ClienteParaBank';
import { DatosDeCliente, fabricaDeClientes } from '../fabricaDeClientes';

/** HABILIDAD: usar los servicios de ParaBank (por dentro, la capa de API de siempre). */
export class UsarLaApiDeParaBank {
  constructor(readonly api: ClienteParaBank) {}

  static con(api: ClienteParaBank): UsarLaApiDeParaBank {
    return new UsarLaApiDeParaBank(api);
  }
}

/** TAREA: registrarse como cliente nuevo. Recuerda su cuenta principal como "principal". */
export class RegistrarseComoClienteNuevo implements Tarea {
  private constructor(private readonly datos: DatosDeCliente) {}

  static conDatosDePrueba(): RegistrarseComoClienteNuevo {
    return new RegistrarseComoClienteNuevo(fabricaDeClientes.nuevo());
  }

  async realizadaPor(actor: Actor): Promise<void> {
    await EntrarComo.cliente(await actor.usa(UsarLaApiDeParaBank).api.registrar(this.datos)).realizadaPor(actor);
  }
}

/** TAREA: el actor toma la identidad de un cliente que ya existe. Recuerda su cuenta como "principal". */
export class EntrarComo implements Tarea {
  private constructor(private readonly cliente: ClienteRegistrado) {}

  static cliente(cliente: ClienteRegistrado): EntrarComo {
    return new EntrarComo(cliente);
  }

  async realizadaPor(actor: Actor): Promise<void> {
    actor.recuerda('cliente', this.cliente);
    actor.recuerda('principal', this.cliente.cuentaPrincipal);
  }
}

/** TAREA: abrir una cuenta nueva con $100 de la cuenta principal. */
export class AbrirCuenta implements Tarea {
  private nombre = 'nueva';

  private constructor(private readonly tipo: TipoDeCuenta) {}

  static deAhorros(): AbrirCuenta {
    return new AbrirCuenta('SAVINGS');
  }

  static corriente(): AbrirCuenta {
    return new AbrirCuenta('CHECKING');
  }

  /** Con qué nombre la recuerda el actor para los pasos siguientes. */
  llamada(nombre: string): AbrirCuenta {
    this.nombre = nombre;
    return this;
  }

  async realizadaPor(actor: Actor): Promise<void> {
    const cliente = actor.recuerdo<ClienteRegistrado>('cliente');
    const cuenta = await actor.usa(UsarLaApiDeParaBank).api.abrirCuenta(cliente.id, this.tipo, cliente.cuentaPrincipal);
    actor.recuerda(this.nombre, cuenta.id);
  }
}

/** TAREA: transferir entre dos cuentas que el actor recuerda por su nombre. */
export class Transferir implements Tarea {
  private destino = '';
  private monto = 0;

  private constructor(private readonly origen: string) {}

  static desde(cuenta: string): Transferir {
    return new Transferir(cuenta);
  }

  hacia(cuenta: string): Transferir {
    this.destino = cuenta;
    return this;
  }

  por(monto: number): Transferir {
    this.monto = monto;
    return this;
  }

  async realizadaPor(actor: Actor): Promise<void> {
    const { estado, mensaje } = await actor
      .usa(UsarLaApiDeParaBank)
      .api.transferir(actor.recuerdo<number>(this.origen), actor.recuerdo<number>(this.destino), this.monto);
    if (estado !== 200) throw new Error(`${actor.nombre} no pudo transferir: ${mensaje}`);
  }
}

/** PREGUNTA: ¿cuánto hay en una cuenta que el actor recuerda? */
export class SaldoDe implements Pregunta<number> {
  private constructor(private readonly cuenta: string) {}

  static cuenta(cuenta: string): SaldoDe {
    return new SaldoDe(cuenta);
  }

  respondidaPor(actor: Actor): Promise<number> {
    return actor.usa(UsarLaApiDeParaBank).api.saldoDe(actor.recuerdo<number>(this.cuenta));
  }
}
