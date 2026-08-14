## LEER SOLUCION

Esta actividad es *individual* para hacer la solucion puede mirar entornos de desarrollo locales puede usar:

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

https://www.geekfun.club/blog/setup-dynamodb-local

https://floci.io/#products

Un entorno de desarollo (en el lab pasado usados Cloud9) sirve para hacer codificacion, pruebas, etc. En ese caso, se puede hacer el diseño, pruebas iniciales de carga de datos y pruebas de test (de performance o el QA que desees indagar, justifique en el documento la decision) para probar como puedas cargar los datos y las tabla(s) que desees probar. No he probado ninguna de las opciones anteriores, asi que por favor, indagar y hacer las pruebas correspondientes.

Cuando crean que el entorno funciona adecuadamente, que la manera de carga de informacion y que la manera de probar fue la adecuada, pueden ejecutar la carga de la informacion en AWS y hacer la prueba. Es su responsabilidad hacer las verificaciones de costos, el sandbox account tiene un limite de U$20, por favor, tener en cuenta para sus pruebas y tomar decisiones con respecto al RCU/WCU o Scaling On Demand. Justifique en el documento la decision. Recordar que el profesor tiene que poder ingresar y hacer las verificaciones, asi que evite que se bloquee su cuenta por uso excesivo de los U$20.

Para la generacion de datos ficticia pueden usar GenAI, y pueden basarse en datos publicos por ejemplo, https://datosabiertos-transmilenio.hub.arcgis.com/

Existen opciones para hacer el test, en la Guia de Actividades de Unisabana e-Learning mencione JMeter, Gatling, pero tambien puede usar otros por ejemplo, k6. En el documento de entrega, mencionar justificar su  seleccion de herramientas, ademas de explicar brevemente el script. NO NECESITO EL SCRIPT O LA MANERA DE PROBARLO, quisiera que pudiera mencionar como lo realizo.

El script definitivo se publicara el viernes 14 de Agosto y los formularios de Forms Office con las fechas se haran desde el miercoles 19 de Agosto, y se ejecutaran a las 5 pm todos los dias hasta la fecha de cortes, 23 de Agosto. La idea es que traiga preguntas a la clase del martes o miercoles sobre esta actividad.

*El modelamiento (UML, APIs Design) si aplica para los 3 casos de uso, en la actividad del modelamiento en AWS Dynamodb (lo que monta en la cuenta de Sandbox) seleccione uno de ellos y apliquelo*