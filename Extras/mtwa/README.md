# MTWA
# Codigo Adaptado de Multi Layer Application de Ben Piper (https://github.com/benpiper/mtwa-docker)
# que a su vez es la version dockerizada de Brantley Richbourg (https://github.com/brichbourg/Multi-Tier-App-Demo)

Las imagenes docker estan disponibles en:

fmorenod81/mtwa:web
fmorenod81/mtwa:app

apt install python3-mysql

La primera es la version para la capa Web, mientras que la segunda cubre la capa Aplicaciones.
Para lanzar ambos contenedores es importante enviarles las siguientes variables de entorno:
APPSERVER: La IP/DNS del Balanceador/Instancia de la capa de Aplicaciones.
DBSERVER_W: La IP/DNS/Endpoint de la Base de Datos MySQL.
DBSERVER_RO: La IP/DNS/Endpoint de la replica de la Base de Datos MySQL.
SETCOOKIE: Si es YES o esta definida, se crea una cookie para el Sticky Session y permite acceder al mismo servidor consecutivamente.

Las modificaciones al codigo de Ben Piper fueron:
- Eliminar la llamada a una archivo PHP inexistente.
- Adicionar imagenes en el encabezado.
- Agregar fecha y hora de los contenedores.
- Modificaciones de variables independientes para base de datos.
- Adicion del archivo SQL con el esquema para MySQL/Aurora que se tiene que ejecutar. Datos de BD (instancia DB/usuario/clave-appdemo/appdemo/appdemo1)



https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/mysql-install-cli.html
sudo dnf install mariadb105 -y
mysql --version
mysql -h terraform-20261031024252267100000001.cyfiyy9tw3jn.us-east-1.rds.amazonaws.com -P 3306 -u appdemo -p

curl -o global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
mysql -h terraform-20261031024252267100000001.cyfiyy9tw3jn.us-east-1.rds.amazonaws.com -P 3306 -u appdemo -p --ssl-mode=VERIFY_IDENTITY --ssl-ca=./global-bundle.pem

appdemo1

Para OCI 8
sudo yum install git -y
git clone https://github.com/fmorenod81/AWS_SAA_C03
cd /AWS_SAA_C03/Extras/mtwa
sudo dnf install -y dnf-utils zip unzip
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf remove -y runc
sudo dnf install -y docker-ce --nobest
sudo systemctl enable docker.service
sudo systemctl start docker.service
sudo echo "opc  ALL=(ALL)  NOPASSWD: /usr/bin/docker" >> /etc/sudoers
sudo echo "alias docker=\"sudo /usr/bin/docker\"" >> /home/opc/.bash_profile

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)


sudo docker run -d -p 80:80 -p 443:443 -h web1 fmorenod81/mtwaoci:web 
sudo docker run -d -p 8080:8080 -p 8443:8443 -h web1 fmorenod81/mtwaoci:app
apt install nano --force-yes
nano /var/www/html/appdemo/appsitefunctions.py