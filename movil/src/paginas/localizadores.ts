/**
 * LA ESCALERA DE LOCALIZADORES MÓVILES (la misma idea que la de la S6, pero en un celular).
 *
 * Se sube un peldaño SOLO si el de abajo no existe en esa pantalla. Nunca XPath.
 *
 *   1. Accessibility id   ~Tap to login with given credentials
 *      Es el "content-desc" de Android (el que lee TalkBack). Lo pone el desarrollador a propósito,
 *      no cambia con el diseño ni con el idioma de la pantalla. Es el getByRole/getByTestId del móvil.
 *
 *   2. resource-id        id=com.saucelabs.mydemoapp.android:id/nameET
 *      El "id" que la app le da a cada control. Estable, pero es un nombre técnico: si el equipo
 *      refactoriza la pantalla, puede cambiar. Siempre con el paquete adelante.
 *
 *   3. UiAutomator        android=new UiSelector().text("Sauce Labs Backpack")
 *      Para cuando lo único que distingue al elemento es su texto (un producto de una lista).
 *      .text("…") es el texto EXACTO. Para "contiene" se usa .textContains("…").
 *      OJO: en UiAutomator2 no existe text() de XPath; el //*[contains(text(),'…')] del proyecto viejo
 *      no encuentra nada, porque en Android el texto es un atributo (@text), no un nodo.
 *
 *   4. XPath              NUNCA. Es lento en móvil (Appium arma TODO el árbol de la pantalla para
 *      cada búsqueda), se rompe con cualquier cambio de diseño y casi siempre hay un peldaño 1-3.
 *      Si no lo hay, se le pide al equipo de desarrollo un content-desc: eso también es QA.
 *
 * ¿Cómo sé qué tiene cada elemento? Appium Inspector (ver GUIA_INSTALACION_WINDOWS.md) o
 * driver.getPageSource(), que devuelve el árbol con text, content-desc y resource-id.
 */
import { entorno } from '../config/entorno';

/** Peldaño 1: accessibility id (content-desc). */
export const porAccesibilidad = (nombre: string): string => `~${nombre}`;

/** Peldaño 2: resource-id. Solo se escribe el final; el paquete de la app se pone solo. */
export const porId = (id: string): string => `id=${entorno.paquete}:id/${id}`;

/** Peldaño 3: UiAutomator por texto exacto. */
export const porTexto = (texto: string): string => `android=new UiSelector().text("${texto}")`;

/**
 * Peldaño 3, compuesto: el elemento con ese resource-id que está JUNTO al texto (mismo contenedor).
 * Sirve en listas: «la imagen del producto que se llama Sauce Labs Backpack».
 */
export const porIdJuntoAlTexto = (id: string, texto: string): string =>
  `android=new UiSelector().text("${texto}").fromParent(new UiSelector().resourceId("${entorno.paquete}:id/${id}"))`;
