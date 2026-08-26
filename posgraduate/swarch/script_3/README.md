## LEER LECCIONES APRENDIDAS

![Mandatory](../../../img/ppt.png)[*LEA LAS LECCIONES APRENDIDAS*](./m13_Solutions.pdf)


Esta actividad es *individual* para hacer la solucion puede mirar entornos de desarrollo locales puede usar:

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

https://www.geekfun.club/blog/setup-dynamodb-local

https://floci.io/#products

Un entorno de desarollo (en el lab pasado usados Cloud9) sirve para hacer codificacion, pruebas, etc. En ese caso, se puede hacer el diseño, pruebas iniciales de carga de datos y pruebas de test (de performance o el QA que desees indagar, justifique en el documento la decision) para probar como puedas cargar los datos y las tabla(s) que desees probar. No he probado ninguna de las opciones anteriores, asi que por favor, indagar y hacer las pruebas correspondientes.

Cuando crean que el entorno funciona adecuadamente, que la manera de carga de informacion y que la manera de probar fue la adecuada, pueden ejecutar la carga de la informacion en AWS y hacer la prueba. Es su responsabilidad hacer las verificaciones de costos, el sandbox account tiene un limite de U$20, por favor, tener en cuenta para sus pruebas y tomar decisiones con respecto al RCU/WCU o Scaling On Demand. Justifique en el documento la decision. Recordar que el profesor tiene que poder ingresar y hacer las verificaciones, asi que evite que se bloquee su cuenta por uso excesivo de los U$20.

Para la generacion de datos ficticia pueden usar GenAI, y pueden basarse en datos publicos por ejemplo, https://datosabiertos-transmilenio.hub.arcgis.com/

Existen opciones para hacer el test, en la Guia de Actividades de Unisabana e-Learning mencione JMeter, Gatling, pero tambien puede usar otros por ejemplo, k6. En el documento de entrega, mencionar justificar su  seleccion de herramientas, ademas de explicar brevemente el script. NO NECESITO EL SCRIPT O LA MANERA DE PROBARLO, quisiera que pudiera mencionar como lo realizo.

El script definitivo se publicara el viernes 25 de Agosto y los formularios de Forms Office con las fechas se haran desde el miercoles 26 de Agosto, y se ejecutaran a las 7 pm (ver excepciones en listado al final) todos los dias hasta la fecha de cortes, 2 de Septiembre. La idea es que traiga preguntas a la clase del martes o miercoles sobre esta actividad.

----
## IMPORTANTE

Mi sugerencia es que inicie con el caso de uso y luego el diseño del API, porque quiero que piensen en el flujo: en quien va a consumir (actor), a donde va a consumir (dispositivos o canales), dentro de su arquitectura va a ver componentes intermedios que sean consumidores (cache). Si cree que es mas facil describir concretamente la arquitectura o un diagrama con ello, no hay problema. Algunos grupos, presentaron el filtro de Bloom en la arquitectura, quizas eso le puede dar ideas del flujo.
Para la prueba Ud. puede seleccionar lectura, escritura y mencionar que actor lo hace; y que almacena (datos) y como lo almacena (uso de indices).
Es un ejercicio de inteligencia, no de metodo. Uds puede gastarse mucho en hacer la medicion, pero valorare mas como piensa el caso y como lo diseña. Para ello, lo calificare en Contenido (Verifique los saltos en la Guia de Actividades, ejemplo en ese item de 2.2 a 1.3). Pude usar la AI para darle ideas, pero el contexto y lo que se vive/vé en la calle o se imagine (pensar fuera de la casa), es lo que le da el valor al arquitecto.

----
*El modelamiento (UML, APIs Design) si aplica para los 3 casos de uso, en la actividad del modelamiento en AWS Dynamodb (lo que monta en la cuenta de Sandbox) seleccione uno de ellos y apliquelo*


Como se usa el script

python script3phase1.py --profile <NOMBRE_DEL_PROFILE> <NOMBRE_TABLA_DYNAMODB>

Reemplazar los valores adecuadamente.

**El script no hace comprobaciones, unicamente es la evidencia que Ud. monto el mismo diseño que presenta en el documento y cuantos registros cargo**


Los Formularios permiten el llenado de informacion a las 6 AM y cierran accesos a las 7 PM COT. Ejecutare a las 7 PM COT.

* Formulario Lunes 24-Agosto: https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUOTA5WUpFOVdMMkxJOURCMTY3ME5NRzZUTi4u