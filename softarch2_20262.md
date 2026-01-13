softarch2_20262.md

Seleccion de su problema asignado depende de la cantidad de estudiantes y del valor seleccionado al azar, puede darse por ultimo digito par o impar, o de otra manera, pero la condicion es que la cantidad de asignados a los problemas sean similares.

2026 - Semestre 2, se aplicara Caso 1 y Caso 3.

## Caso 1

Reserva de tiquetes aéreos en una fábrica de software: ventas, conformación de equipos remotos y eventos técnicos.

Una empresa de outsorcing de personal tenia un alianza con una agencia de viajes que realizaba la gestion de tiquetes, alojamiento y transporte; sin embargo, para minizar costos y a que existen mas operadoras que permiten hacer alianzas directas, las directivas solicitan la creacion de un portal de autoservicio para que los empleados que necesitan hacer viajes puedan hacer la gestion directa.

El organigrama de la compañia estan clasificada en A, B y C (ascedente); y dentro de ella, estan en niveles de 1 a 5 (ascedente). Segun esta clasificacion esta las aprobaciones de viajes. Existen areas que tendrian un rol diferente como son: Finanzas y Auditoria.

Los viajes de confirmacion de equipos (team building) pueden durar 1 semana, y pueden ser cobrados al cliente posteriormente. Los eventos tecnicos tienen una duracion de 1 a 3 dias, y el resto suelen ser de 3 a 4 dias.

Son 60k empleados, con un estimado de empleados al año que realizan viajes 700, con un estimado de 5k viajes al año 2024. Crecimiento del 15% anual.
Las personas suelen movilizarse usando transporte privado en las ciudades durante el viaje y suelen usar Uber/Cabify/InDrive. Se puede permitir subir la categoria dependiendo de la aprobacion.

Las operadores estan por pais y por categoria (transporte aereo y terrestre) y ofrecen un API que puede variar, en los metodos la exposicion de la oferta, como para la reserva. Existen campos obligatorios para cada  servicio, sin embargo, no estan estandarizados, ejemplo: Nombre completo, ó Nombres y Apellidos.

Dispositivo a usar: Pagina Web, movil con funcionalidad reducida.

Extensibilidad: Sistema propio tipo PinBus, tiquetes baratos, aerolineas.

## Caso 2

Sistema de recaudo para transporte masivo para Bogotá (Transmilenio/SITP).

En Bogota, existe un sistema de transporte que usa una tarjeta para realizar la validacion al ingresar al sistema de transporte. Se desea que se diseñe la plataforma de recaudo (recarga y validacion en barreras) para generar un minimo de evasion al usar las tarjetas y que la experiencia al usuario sea excelente (Contractualmente -hipotetico- un malfuncionamiento obligacion abrir barreras sin validacion de manera ilimitada, y evaluado cada 10 minutos).
Existen diferentes actores: Ciudadano, Subsidiado, Funcionario Operador Bus, Funcionario SITP, Servicio Emergencia (Policia TM, Cruz Roja), sistema aliado (Movilred, Efecty, PagaTodo), banco aliado, Operador de Movilidad (Empresa Transporte).
Existen diferentes tarjetas: Anonima, Personalizada, Funcionario Operador Bus, Funcionario SITP, Servicio Emergencia.

Funcionalidad a mostrar: Listas negras (tarjetas bloqueadas - robo o fraude), Listas blancas (funcionarios o servicio de emergencia).

La volumetria y parametros (cantidad de estaciones, buses por operador) son de dominio publico. Anexar los enlaces a esos recursos.

Dispositivo a usar: Pagina Web.

Extensibilidad: Sistema transporte municipal.

## Caso 3

eCommerce estratégico de productos con alta demanda en hora nocturnas. Producto: Correo de la Noche.

En la decadas de los 2000's existio un popular servicio  llamado Correo de la Noche en cierto sector de la poblacion, que ofrecia servicios de licores y otros servicios que las fiestas necesitaban a la brevedad. En este casos vamos a modernizarlo con diferentes funcionalidades hipoteticas.
Creamos 2 clases de usuarios finales: ocasionales y frecuentes. Los ocasionales podrian ser creados al ser invitados por frecuentes o por un metodo de validacion de mayoria de edad, en ambos casos, tienen una limitacion por tiempo.
Los metodos de pago podrian diferir para aumentar fidelizacion por tipo de usuario, plantear alternativas para este fin. La validacion de identidad se tendria que mantener para los usuarios frecuentes.
El precio del usuario frecuente al mes era bajo, lo que permitiria su popularizacion. Se puede segmentar el usuario frecuente en edad, areas de servicio e historial de consumos.
Tenian un sistema que permitia localizar al usuario o se le solicitaba que diera direccion exacta; y se podria usar su localizacion para asignar el servicio a la licoreria o bodega oculta (diferente servicios, ejemplo, conjunto vallenato, etc) mas cercana basado en la solicitud.
Las relaciones con licoreras o bodegas ocultas debian poder generar: vinculacion, desvinculacion, geolocalizacion (real o fija), inventario disponible en tiempo casi-real, asignacion de servicio, periodicidad de pago, promociones, y calificacion del usuario final.
Se estima 2M como el universo de usuarios finales en Bogota, con 100k usuarios frecuentes al primer año, y un consumo quincenal de 75k por usuario frecuente. Los momentos de alto consumo serian jueves a domingo entre 9 pm a 4 am.

Dispositivo a usar: Pagina Web, aplicacion movil, IM, llamadas.

Extensibilidad: Servicio de medicinas frecuentes.

## Caso 4

Plataforma de evaluacion de riesgo para personas naturales, tipo Addi o SisteCredito.