/**
 * CAPA DE FLUJOS: pasos de negocio que combinan varias pantallas o servicios.
 * Una prueba dice "inicia sesión" y no se preocupa por los 6 pasos que hay detrás.
 */
import { Page } from '@playwright/test';
import { ClienteBanco } from '../api/ClienteBanco';
import { Usuario, usuarios } from '../datos/usuarios';
import { PaginaBuzon } from '../paginas/PaginaBuzon';
import { PaginaInicio } from '../paginas/PaginaInicio';
import { PaginaLogin } from '../paginas/PaginaLogin';
import { PaginaOtp } from '../paginas/PaginaOtp';

/** Las pantallas que participan en el ingreso. Las entrega el fixture "paginas". */
export interface PaginasDeIngreso {
  login: PaginaLogin;
  otp: PaginaOtp;
  buzon: PaginaBuzon;
  inicio: PaginaInicio;
}

/**
 * Ingreso completo por la pantalla, como lo haría el cliente.
 * Úsalo solo en las pruebas cuyo objetivo ES el ingreso.
 */
export async function iniciarSesionPorUi(paginas: PaginasDeIngreso, usuario: Usuario): Promise<void> {
  await paginas.login.abrir();
  await paginas.login.ingresar(usuario.usuario, usuario.clave);
  await paginas.otp.esperarQueCargue();
  const codigo = await paginas.buzon.leerUltimoCodigo(usuario.usuario);
  await paginas.otp.validar(codigo);
  await paginas.inicio.esperarQueCargue();
}

/**
 * Deja el navegador con la sesión abierta, SIN pasar por las pantallas de ingreso.
 * Inicia sesión por API y guarda el token donde la página lo busca (localStorage).
 * Úsalo en las pruebas cuyo objetivo NO es el ingreso: son más rápidas y estables.
 */
export async function abrirConSesion(page: Page, cliente: ClienteBanco, usuario: Usuario = usuarios.ana): Promise<void> {
  const { token, nombre } = await cliente.iniciarSesion(usuario);
  await page.addInitScript(([t, n]) => {
    localStorage.setItem('token', t);
    localStorage.setItem('nombre', n);
  }, [token, nombre]);
}
