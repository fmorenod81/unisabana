## LEER SOLUCION

* Instalar Python. Version probada fue Python 3.9.11 en Windows 11 H2. Dentro de los requirimientos de ejecucion de este Python esta la instalacion de boto3 y para la fase 10 hay un [README especial](./README_PHASE10.md). Revisar la instalacion en su sistema operativo.
  
* Instalar el AWS CLI y configurarlo de manera adecuada con el AWS Academy [Ejemplo de Configuracion en el AWS Academy](./Requisites2.png).
  
* Cuando use comandos de CLI algunas veces la respuesta es larga por tanto se pagina, para avanzar se realiza con espacio y cuando llega al final aparece algo como (END) y para salir, se presiona q

* Revisar los links que estan en el PDF de [solucion o notas del profesor](./student-guide.pdf)

* Hubo una actualizacion en la creacion del ECS, asi que puse la nota en el PDF y aqui esta la [imagen mas grande](./ECS_Cluster.png)

* Puede que tenga alguna confusion entre un ARN y un ID en el ejercicio 7.1, aqui pongo un ejemplo de unos de los casos, por favor revisarlo [aqui](./Task71.png)

* Encontre algunas paginas con la solucion al laboratorio, sin embargo, la parte de los scripts no aparece. Recordar mantener los nombres iguales.
 
    https://www.youtube.com/watch?v=l3-4ARgddJQ

    https://jayeshrajput.hashnode.dev/mastering-aws-building-microservices-and-cicd-pipelines-for-scalable-applications

* Un ejemplo de la salida de todos los scripts esta [aqui](./franciscomodi.log)

* La ejecucion de la fase 10 es para tomar los pantallazos de ejecucion; y al finalizar se subiran los resultados a la pagina web estatica.

* La manera de ejecutar cada script es la misma, ejemplo

python script2phase2.py franciscomodi 

* La union de todos los scripts fue asi:
  
python script2phase2.py franciscomodi >franciscomodi

python script2phase3.py franciscomodi >>franciscomodi.log

python script2phase4.py franciscomodi >>franciscomodi.log

python script2phase5.py franciscomodi >>franciscomodi.log

python script2phase6.py franciscomodi >>franciscomodi.log

python script2phase7.py franciscomodi >>franciscomodi.log

python script2phase8.py franciscomodi >>franciscomodi.log

python script2phase9.py franciscomodi >>franciscomodi.log

python script2phase10.py franciscomodi >>franciscomodi.log

* Para el envio de las credenciales al profesor se hara por un formulario de Microsoft Forms. 

Los Formularios permiten el llenado de informacion a las 6 AM y cierran accesos a las 5 PM COT.

* Formulario Sabado 25-Julio: https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpURjQ5SEU4VlZXTE0yRlgwRFM5WUJUNlgzUi4u

* Formulario Domingo 26-Julio: https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpURDQ5VkxLWDhKN1g3WUdCMFNJNEo0NFFGRC4u

* Formulario Sabado 1-Agosto: https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUQUhaRjZETjdQSzdKTkg2MDhGNk8wNk9XMC4u

* Formulario Domingo 2-Agosto: https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUMlpMMDhEUlg2TzNFUzdKQVE1VFZLMjRWSi4u

* Formulario Viernes 4-Agosto (Cierra 8pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUQ1ZIN0ZGMkxRSDM5T0FXRlQ4WFNMRUxDWi4u

* Formulario Viernes 5-Agosto (Cierra 8pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUODJISDBQRTlDWVVNNE5XWlA0RlZWVzRTVi4u

* Formulario Viernes 6-Agosto (Cierra 8pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUOVpYQ1BERE1aTlBCRzZFQjVZRFVDQjRWQS4u

* Formulario Viernes 7-Agosto (Cierra 5pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUMkxLR1ZBRjRUWTE0UFlMMkw4S1VSWkFTWi4u

* Formulario Sabado 8-Agosto (Cierra 5pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUMlJHOUNSNTlXVzZBNVNGMTZWUE9GRU4wNi4u

* Formulario Domingo 9-Agosto (Cierra 5pm): https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpUNlM3Q1pWTU1MOUIxUU5KQ0NSQ1gxVUhEQi4u


* La ruta donde quedara el registro de la ultima ejecucion estara disponible en:  http://testfmorenodpublichtml.s3-website-us-east-1.amazonaws.com/<nombre_de_usuario>/ el mismo que fue incluido en el formulario, por ejemplo, http://testfmorenodpublichtml.s3-website-us-east-1.amazonaws.com/franciscomodi/

* Voy a intentar que el script sea inteligente, pero sinceramente espero que tenga estudiantes a nivel de MSc que lo revisen localmente antes de enviarlo.