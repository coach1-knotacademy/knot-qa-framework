import { Page } from '@playwright/test';
import { entorno } from '../config/entorno';

/** Lo que responde el "servicio" del Banco Demo: un estado HTTP y el JSON (distinto en cada ruta). */
interface Respuesta {
  estado: number;
  datos: any;
}

/**
 * FLUJO: deja el navegador con la sesión abierta SIN pasar por las pantallas de ingreso.
 * Úsalo en las pruebas cuyo objetivo NO es el ingreso: son más rápidas y estables.
 *
 * En el Banco Demo de GitHub Pages no hay servidor: el "servicio" corre dentro de la misma página
 * (api-estatica.js). Por eso se le habla desde la página. En tu proyecto, aquí va tu cliente de API.
 */
export async function abrirConSesion(page: Page, usuario = entorno.usuario, clave = entorno.clave): Promise<void> {
  await page.goto('index.html');
  const error = await page.evaluate(async ({ usuario, clave }) => {
    const api = (window as unknown as { apiEstatica: (ruta: string, opciones?: { method: string; body: string }) => Promise<Respuesta> }).apiEstatica;
    const enviar = (ruta: string, cuerpo: object) => api(ruta, { method: 'POST', body: JSON.stringify(cuerpo) });

    const ingreso = await enviar('/api/login', { usuario, clave });
    if (ingreso.estado !== 200) return ingreso.datos.error ?? `Ingreso: estado ${ingreso.estado}`;
    const buzon = await api(`/api/buzon?usuario=${encodeURIComponent(usuario)}`);
    const codigo = await enviar('/api/otp', { idDesafio: ingreso.datos.idDesafio, codigo: buzon.datos[0]?.codigo });
    if (codigo.estado !== 200) return codigo.datos.error ?? `Código: estado ${codigo.estado}`;

    localStorage.setItem('token', String(codigo.datos.token));
    localStorage.setItem('nombre', String(codigo.datos.nombre));
    return null;
  }, { usuario, clave });
  if (error) throw new Error(`No se pudo abrir la sesión de ${usuario} en ${entorno.nombre}: ${error}`);
}
