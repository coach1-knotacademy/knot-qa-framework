import { driver } from '@wdio/globals';
import { entorno } from '../config/entorno';
import { PaginaCatalogo } from '../paginas/PaginaCatalogo';

/**
 * Cada prueba empieza con la app como recién instalada: sin sesión y con el carrito vacío.
 * Es el equivalente del "contexto nuevo" que Playwright da a cada prueba: así ninguna depende de otra.
 * ("mobile: clearApp" borra los datos de la app, como Ajustes → Apps → Borrar almacenamiento).
 */
export async function abrirAppLimpia(): Promise<void> {
  await driver.execute('mobile: clearApp', { appId: entorno.paquete });
  await driver.execute('mobile: activateApp', { appId: entorno.paquete });
  await new PaginaCatalogo().esperarQueCargue();
}
