softarch2_20262.md

- [Presentaciones](#presentaciones)
- [Asignaciones](#asignaciones)
  - [Tacticas, Patrones Arquitectonicos y Estilos Arquitectonicos](#tacticas-patrones-arquitectonicos-y-estilos-arquitectonicos)
    - [Plataformas asignadas](#plataformas-asignadas)
  - [Sistemas Distribuidos](#sistemas-distribuidos)
    - [Diseño de base de datos no-relacionales](#diseño-de-base-de-datos-no-relacionales)
  - [Liderazgo en Arquitectura](#liderazgo-en-arquitectura)
    - [Ideas en industrias sugeridas](#ideas-en-industrias-sugeridas)
- [Links Interesantes](#links-interesantes)

# Presentaciones

<details>
  <summary><b>Presentaciones del Curso</b></summary>
  <br>

![Mandatory](../../img/ppt.png)[Modulo 0: Introduccion al Curso](./m0_Intro_To_Course.pdf)

![Mandatory](../../img/ppt.png)[Modulo 1: Estilos y Patrones Arquitectonicos](./m1_Tactics_Arch_Patterns_Arch_Styles.pdf)

![Mandatory](../../img/ppt.png)[Modulo 2: Microservicios](./m2_Microservices.pdf)

![Mandatory](../../img/ppt.png)[Modulo 3: Sistemas Distribuidos](./m3_Distributed_Systems.pdf)

![Mandatory](../../img/ppt.png)[Modulo 4: Liderazgo en Arquitectura](./m4_Leadership_in_Architecture.pdf)

</details>

# Asignaciones

Seleccion de su problema asignado depende de la cantidad de estudiantes y del valor seleccionado al azar, puede darse por ultimo digito de su documento de identificacion par o impar, o de otra manera, pero la condicion es que la cantidad de estudiantes asignados a los problemas sean similares.

## Tacticas, Patrones Arquitectonicos y Estilos Arquitectonicos

2026 - Semestre 2 Cohorte 1, se aplicara Caso 1 y Caso 3.

2026 - Semestre 2 Cohorte 2, se aplicara Caso 2 y Caso 4.

<details>
  <summary><b>Casos de estudio de Google</b></summary>
  <br>

  ![Mandatory](../../img/google.png) [EHR Healthcare](https://services.google.com/fh/files/blogs/master_case_study_ehr_healthcare.pdf)

  ![Mandatory](../../img/google.png) [Helicopter Racing League](https://services.google.com/fh/files/blogs/master_case_study_helicopter_racing_league.pdf)

  ![Mandatory](../../img/google.png) [Mountkirk Games](https://services.google.com/fh/files/blogs/master_case_study_mountkirk_games.pdf)

  ![Mandatory](../../img/google.png) [TerramEarth](https://services.google.com/fh/files/blogs/master_case_study_terramearth.pdf)

</details>

### Plataformas asignadas

<details>
  <summary><b>Caso 1: Tiquetes Aereos para la Fabrica de Software</b></summary>
  <br>

Reserva de tiquetes aéreos en una fábrica de software: ventas, conformación de equipos remotos y eventos técnicos.

El rol del entrevistado sera el Director de compras (Procurement).

Una empresa de outsorcing de personal tenia un alianza con una agencia de viajes que realizaba la gestion de tiquetes, alojamiento y transporte; sin embargo, para minizar costos y a que existen mas operadoras que permiten hacer alianzas directas, las directivas solicitan la creacion de un portal de autoservicio para que los empleados que necesitan hacer viajes puedan hacer la gestion directa.

El organigrama de la compañia estan clasificada en A, B y C (ascedente); y dentro de ella, estan en niveles de 1 a 5 (ascedente). Segun esta clasificacion esta las aprobaciones de viajes. Existen areas que tendrian un rol diferente como son: Finanzas y Auditoria.

Los viajes de creacion de equipos (team building) pueden durar 1 semana, y pueden ser cobrados al cliente posteriormente. Los eventos tecnicos tienen una duracion de 1 a 3 dias, y el resto suelen ser de 3 a 4 dias.

Son 60k empleados, con un estimado de empleados al año que realizan viajes 700, con un estimado de 5k viajes al año 2024. Crecimiento del 15% anual.
Las personas suelen movilizarse usando transporte privado en las ciudades durante el viaje y suelen usar Uber/Cabify/InDrive. Se puede permitir subir la categoria dependiendo de la aprobacion.

Se espera que la transaccion sea sincronica (<800ms, el P95) sin embargo, se podria optimizar  costo con las mismas condiciones de fecha y hora, pero con condiciones diferentes (i.e. Ejecutando una consulta posterior pero con categoria turista en vez de Primera Clase).

Las operadores estan por pais y por categoria (transporte aereo y terrestre) y ofrecen un API que puede variar, en los metodos la exposicion de la oferta, como para la reserva. Existen campos obligatorios para cada  servicio, sin embargo, no estan estandarizados, ejemplo: Nombre completo, ó Nombres y Apellidos.

Dispositivo a usar: Pagina Web, movil con funcionalidad reducida.

Extensibilidad: Sistema propio tipo PinBus, tiquetes baratos, aerolineas.

</details>

<details>
  <summary><b>Caso 2: Sistema de recaudo para transporte masivo para Bogotá (Transmilenio/SITP).</b></summary>
  <br>

El rol del entrevistado sera el CTO de la compañia de Recaudo.

En Bogota, existe un sistema de transporte que usa una tarjeta para realizar la validacion al ingresar al sistema de transporte. Se desea que se diseñe la plataforma de recaudo (recarga en dispositivos y validacion en barreras) para generar un minimo de fraude (evasion) al usar las tarjetas y que la experiencia al usuario sea excelente (Contractualmente -hipotetico- un malfuncionamiento obligacion abrir barreras sin validacion de manera ilimitada, y evaluado cada 10 minutos).
Existen diferentes actores: Ciudadano, Subsidiado, Funcionario Operador Bus, Funcionario SITP, Servicio Emergencia (Policia TM, Cruz Roja), sistema aliado (Movilred, Efecty, PagaTodo), banco aliado, Operador de Movilidad (Empresa Transporte).
Existen diferentes tarjetas: Anonima, Personalizada, Funcionario Operador Bus, Funcionario SITP, Servicio Emergencia.

Se estima que una transaccion de validacion debe ser menor a 800ms (P95). Las estaciones y buses deberan tener contigencia. El sistema debera tener DRP en una region/lugar en un pais diferente al principal. El año 2025 fueron 3.3M transacciones al dia.

Las estaciones deberan tener disponibles en las horas de operacion (Estaciones 4 am - 10 pm, buses 4:30 am - 11 pm). Contractualmente -hipotetico- 99.9% de disponibilidad, sin embargo puede existir demoras en el registro en las comunicaciones posteriores (un bus que pierde comunicacion durante la noche o mantenimiento).

Funcionalidad a mostrar: Validacion -o no- de tarjetas en Listas negras (tarjetas bloqueadas - robo o fraude), Listas blancas (funcionarios o servicio de emergencia), usuarios ciudadanos (Anonimos y Personlizadas).

La volumetria y parametros (cantidad de estaciones, buses por operador) son de dominio publico. Incluso algunos valores estan en el caso de Sistemas Distribuidos aqui. Anexar los enlaces a esos recursos.

Dispositivos a usar: Dispositivos de validacion en estacion, buses, Recursos Nube, Consumidor funcionario Ente Gestor.

Extensibilidad: Sistema transporte municipal.

</details>


<details>
  <summary><b>Caso 3: eCommerce estrategico de productos con alta demanda en hora nocturnas</b></summary>
  <br>

eCommerce estratégico de productos con alta demanda en hora nocturnas. Producto: Correo de la Noche.

El rol del entrevistado sera el CEO de la compañia (Startup).

En la decadas de los 2000's existio un popular servicio  llamado Correo de la Noche en cierto sector de la poblacion, que ofrecia servicios de licores y otros servicios que las fiestas necesitaban a la brevedad. En este casos vamos a modernizarlo con diferentes funcionalidades hipoteticas.
Creamos 2 clases de usuarios finales: ocasionales y frecuentes. Los ocasionales podrian ser creados al ser invitados por frecuentes o por un metodo de validacion de mayoria de edad, en ambos casos, tienen una limitacion por tiempo.
Los metodos de pago podrian diferir para aumentar fidelizacion por tipo de usuario, plantear alternativas para este fin. La validacion de identidad se tendria que mantener para los usuarios frecuentes.
El precio del usuario frecuente al mes era bajo, lo que permitiria su popularizacion. Se puede segmentar el usuario frecuente en edad, areas de servicio e historial de consumos.
Tenian un sistema que permitia localizar al usuario o se le solicitaba que diera direccion exacta; y se podria usar su localizacion para asignar el servicio a la licoreria o bodega oculta (diferente servicios, ejemplo, conjunto vallenato, etc) mas cercana basado en la solicitud.
Las relaciones con licoreras o bodegas ocultas debian poder generar: vinculacion, desvinculacion, geolocalizacion (real o fija), inventario disponible en tiempo casi-real, asignacion de servicio, periodicidad de pago, promociones, y calificacion del usuario final.

Se estima 2M como el universo de usuarios finales en Bogota, con 100k usuarios frecuentes al primer año, y un consumo quincenal de 75k por usuario frecuente. Los momentos de alto consumo serian jueves a domingo entre 9 pm a 4 am.

Se estima que una transaccion con informacion completa debera ejecutarse menos a 3 segundos (P90). Se puede establecer un DRP flexible, a excepciones de redudancia de datos (compras recientes < 2 dias).

Dispositivo a usar: Pagina Web, aplicacion movil, IM, llamadas.

Extensibilidad: Servicio de medicinas frecuentes.

</details>

<details>
  <summary><b>Caso 4: Plataforma de evaluacion de riesgo para personas naturales, tipo Addi o SisteCredito.</b></summary>
  <br>

TBD
</details>

## Sistemas Distribuidos

2026 - Semestre 2 Cohorte 1, se aplicara Caso A

2026 - Semestre 2 Cohorte 2, se aplicara Caso B

### Diseño de base de datos no-relacionales

<details>
  <summary><b>Caso A: Sistema de Validacion de Tarjetas en Transporte Masivo</b></summary>
  <br>

Ademas de la informacion visto en el caso anterior, vemos que el sistema de validacion de tarjetas tiene los siguientes valores:

* Transacciones por hora: ~30,000

* Transacciones por minuto: ~500

* Transacciones por segundo (TPS): ~8-10 (en promedio constante durante esa hora).

* Tarjetas perdidas o robadas anuales: 150,000 (aprox.)

* Cantidad de Funcionarios (TM, Recaudo, Policia TM): 35,000

Estos valores son obtenidos por GenAI, sin embargo, si puede encontrar la fuente mas fiable por favor referenciarla.

</details>

<details>
  <summary><b>Caso B: Juegos online - Intercambio de productos o features</b></summary>
  <br>

TBD
</details>

## Liderazgo en Arquitectura

La idea inicial es que realice el Architectural Kata y el ADR de la empresa o en la industria donde labora, recuerde que no puede entregar informacion sensible o algo que identifique univocamente su empresa. En caso contrario, aquie puede encontrar un listado de ideas para la Kata y el ADR por industria:

2026 - Semestre 2 Cohorte 1, se aplicara Industrias i y iii

2026 - Semestre 2 Cohorte 2, se aplicara Industrias ii y iv

### Ideas en industrias sugeridas

<details>
  <summary><b>Industrias i: Salud</b></summary>
  <br>

- Sistema de solicitud de Citas medicas y diagnosticas

- Entrega de resultados diagnosticos

- Localizacion de medicos y/o especialistas

</details>

<details>
  <summary><b>Industrias ii: Financieras</b></summary>
  <br>

- Medios de pago alternativos: Economia circular.

- Inversion en Trading y Broker para inversores persona natural y de bajo monto.

</details>

<details>
  <summary><b>Industrias iii: Servicios</b></summary>
  <br>

- Mantenimiento de vehiculos particulares: lavado, revisiones, mantenimiento, SOAT, etc.

- Solicitud de Reparacion Locativas.

</details>


<details>
  <summary><b>Industrias iv: Gobierno</b></summary>
  <br>

- Impuestos finca raiz: prevision, ahorro.

- Impuestos persona natural.

</details>

# Links Interesantes

[Techworld with Milan - Modular Monolith](https://newsletter.techworld-with-milan.com/p/what-is-a-modular-monolith)

[Databricks - MapReduce](https://www.databricks.com/glossary/mapreduce)

[Choosing the Right DynamoDB Partition Key, AWS Database Blog](https://aws.amazon.com/blogs/database/choosing-the-right-dynamodb-partition-key/)

