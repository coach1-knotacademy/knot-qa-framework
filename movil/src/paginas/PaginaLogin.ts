import { $ } from '@wdio/globals';
import { PaginaBase } from './PaginaBase';
import { porAccesibilidad, porId } from './localizadores';
import type { Usuario } from '../datos/usuarios';

/**
 * PAGE OBJECT de la pantalla de inicio de sesión.
 * La prueba dice QUÉ hace el cliente (entrarCon); aquí está el CÓMO (qué tocar y en qué orden).
 */
export class PaginaLogin extends PaginaBase {
  // Peldaño 2 (resource-id): el título y los campos no tienen content-desc en esta app.
  get titulo() {
    return $(porId('loginTV'));
  }

  get campoUsuario() {
    return $(porId('nameET'));
  }

  get campoClave() {
    return $(porId('passwordET'));
  }

  // Peldaño 1 (accessibility id): el botón sí lo tiene. Se usa aunque el texto diga "Login".
  get botonEntrar() {
    return $(porAccesibilidad('Tap to login with given credentials'));
  }

  // Peldaño 2: los mensajes de error, uno debajo de cada campo.
  get errorDelUsuario() {
    return $(porId('nameErrorTV'));
  }

  get errorDeLaClave() {
    return $(porId('passwordErrorTV'));
  }

  async esperarQueCargue(): Promise<void> {
    await this.campoUsuario.waitForDisplayed();
  }

  async entrarCon(usuario: Usuario): Promise<void> {
    await this.campoUsuario.setValue(usuario.correo);
    await this.campoClave.setValue(usuario.clave);
    await this.botonEntrar.click();
  }
}
