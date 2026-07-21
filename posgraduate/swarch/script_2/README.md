## LEER SOLUCION

* Instalar Python. Version probada fue Python 3.9.11 en Windows 11 H2. Dentro de los requirimientos de ejecucion de este Python esta la instalacion de boto3. Revisar la instalacion en su sistema operativo.
  
* Instalar el AWS CLI y configurarlo de manera adecuada con el AWS Academy [Ejemplo de Configuracion en el AWS Academy](./Requisites2.png).
  
* Cuando use comandos de CLI algunas veces la respuesta es larga por tanto se pagina, para avanzar se realiza con espacio y cuando llega al final aparece algo como (END) y para salir, se presiona q

* Revisar los links que estan en el PDF de [solucion o notas del profesor](./student-guide.pdf)

* Hubo una actualizacion en la creacion del ECS, asi que puse la nota en el PDF y aqui esta la [imagen mas grande](./ECS_Cluster.png)

* Puede que tenga alguna confusion entre un ARN y un ID en el ejercicio 7.1, aqui pongo un ejemplo de unos de los casos, por favor revisarlo [aqui](./Task71.png)

* Encontre algunas paginas con la solucion al laboratorio, sin embargo, la parte de los scripts no aparece. Recordar mantener los nombres iguales.
 
    https://www.youtube.com/watch?v=l3-4ARgddJQ

    https://jayeshrajput.hashnode.dev/mastering-aws-building-microservices-and-cicd-pipelines-for-scalable-applications

* La salida de todos los scripts esta [aqui](./Salida.txt)

* La manera de ejecutar cada script es la misma, ejemplo

python script2phase2.py LabMicroservices 

* La union de todos los scripts fue asi:
  
python script2phase2.py LabMicroservices >Salida.txt

python script2phase3.py LabMicroservices >>Salida.txt

python script2phase4.py LabMicroservices >>Salida.txt

python script2phase5.py LabMicroservices >>Salida.txt

python script2phase6.py LabMicroservices >>Salida.txt

python script2phase7.py LabMicroservices >>Salida.txt

python script2phase8.py LabMicroservices >>Salida.txt

python script2phase9.py LabMicroservices >>Salida.txt

* Para el envio de las credenciales al profesor se hara por un formulario de Microsoft Forms. Un ejemplo de como funcionara estara en: https://forms.office.com/Pages/ResponsePage.aspx?id=MRalrP4ADUmRqxY--HJg7u7OXjM2wjRAkB_m26FrUqpURjQ5SEU4VlZXTE0yRlgwRFM5WUJUNlgzUi4u