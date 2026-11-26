# language: es
#
# Kit móvil · Los casos de la tienda de práctica (SauceLabs My Demo App, Android), en Gherkin.
#
# Es el mismo Gherkin de la S7: Dado (la precondición), Cuando (lo que hace el cliente) y Entonces
# (el resultado esperado), en el idioma del negocio, sin toques ni localizadores. Que la pantalla sea
# de un celular no cambia el escenario: cambia la capa de páginas.
#
# El ID del caso va en la etiqueta (@CP-401) y en el título de cada prueba de tests/tienda.spec.ts:
# cada paso es un paso() con el mismo texto, que deja su captura en evidencias/.
# Correr solo un caso:  npm.cmd test -- --mochaOpts.grep "CP-402"

Característica: Comprar en la tienda desde el celular
  Como cliente de la tienda
  quiero entrar con mi usuario y armar mi carrito desde la app
  para comprar sin ir a un computador

  @CP-401
  Escenario: Un comprador entra con su usuario y su clave
    Dado que el comprador abre la pantalla de inicio de sesión
    Cuando entra con su correo y su clave
    Entonces ve el catálogo «Products»
    Y el menú le ofrece «Log Out»

  @CP-402
  Escenario: Un usuario bloqueado no puede entrar
    Dado que el usuario bloqueado abre la pantalla de inicio de sesión
    Cuando entra con su correo y su clave
    Entonces ve el mensaje «Sorry this user has been locked out.»
    Y sigue en la pantalla «Login»

  @CP-403
  Escenario: Sin usuario, la app lo pide antes de intentar entrar
    Dado que alguien abre la pantalla de inicio de sesión
    Cuando intenta entrar sin escribir correo ni clave
    Entonces ve el mensaje «Username is required»

  @CP-404
  Escenario: Dos mochilas en el carrito suman el total correcto
    Dado que el cliente está en el catálogo con el carrito vacío
    Cuando agrega 2 «Sauce Labs Backpack» de $ 29.99 al carrito
    Entonces el carrito muestra 2 artículos
    Y el total es $ 59.98
