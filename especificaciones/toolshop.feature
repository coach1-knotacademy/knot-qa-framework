# language: es
#
# Kit «web real» · Practice Software Testing (la Toolshop), una tienda pública hecha para practicar.
# Es comercio electrónico, no banca: el mismo framework por capas sirve para cualquier sitio web.
#
# Se escriben igual que los CP del Banco Demo: el negocio en Dado, Cuando y Entonces, sin clics ni localizadores.
# El ID del caso va en la etiqueta (@CP-501). Cada escenario está ejecutado en tests/toolshop/ (cada paso es un test.step).
# Los textos esperados están en inglés porque así los muestra el sitio.
# Revisar los escenarios:  npm.cmd run revisar-escenarios -- especificaciones/toolshop.feature

Característica: Comprar herramientas en una tienda en línea
  Como cliente de la tienda
  quiero encontrar un producto, ver su detalle y llevarlo al carrito
  para comprar sin equivocarme de producto ni de total

  @CP-501
  Escenario: La búsqueda muestra solo los productos que coinciden
    Dado que Ana está en el catálogo de la tienda
    Cuando busca «Pliers»
    Entonces ve el título «Searched for: Pliers»
    Y todos los productos que ve tienen «Pliers» en el nombre

  @CP-502
  Escenario: El filtro por categoría deja solo esa categoría
    Dado que Ana está en el catálogo de la tienda
    Cuando filtra por la categoría «Hammer»
    Entonces todos los productos que ve tienen «Hammer» en el nombre

  @CP-503
  Escenario: El detalle de un producto muestra el mismo precio del catálogo
    Dado que Ana está en el catálogo de la tienda
    Cuando abre el detalle de «Combination Pliers»
    Entonces ve el nombre «Combination Pliers» y su descripción
    Y el precio es el mismo que mostraba el catálogo, por ejemplo $14.15

  @CP-504
  Escenario: Dos unidades en el carrito suman el doble del precio
    Dado que Ana tiene el carrito vacío
    Cuando lleva 2 unidades de «Pliers» al carrito
    Entonces el carrito muestra 2 unidades de «Pliers»
    Y el total es 2 veces el precio unitario, por ejemplo $24.02 si cuesta $12.01

  @CP-505
  Escenario: El contacto sin datos pide los obligatorios
    Dado que Ana está en el formulario de contacto
    Cuando lo envía sin datos
    Entonces ve «First name is required», «Email is required» y «Message is required»

  @CP-506
  Escenario: El contacto con un correo mal escrito se rechaza
    Dado que Ana está en el formulario de contacto
    Cuando lo envía con el correo «ana.prueba@»
    Entonces ve «Email format is invalid»

  @CP-507
  Escenario: El ingreso sin correo ni clave pide los dos
    Dado que Ana está en la pantalla de ingreso
    Cuando intenta ingresar sin escribir nada
    Entonces ve «Email is required» y «Password is required»
