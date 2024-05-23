# Movies rating Pipeline de données en temps réel avec Apache nifi, postgress, Debezium et kafka 
## Contexte
### 1. Vue globale :
Ce projet consiste à la création d’un pipeline de données complet en utilisant divers services AWS et des technologies telles que NiFi, Debezium, Kafka, Postgres, ainsi que des outils de visualisation de données. Le pipeline vise à récupérer les évaluations des utilisateurs sur des films à partir d'une API et à les stocker dans une base de données Postgres à l'aide de NiFi. Ensuite, les données seront transmises à S3 via un consommateur Kafka développé en Python. Un connecteur Debezium sera également utilisé avec la base de données créée sur Postgres pour détecter les changements et les transférer vers un topic Kafka. Enfin, les données seront traitées avec Athena puis visualisées à l'aide de Power BI.

### 2. Architecture:
![data-pipeline (17)](https://github.com/Dan2195178/BigData-projet2/assets/123899056/b60af1cf-aec8-45bc-96c0-3dbf2b4627fa)

### 3. Raison du choix de Streaming:
Pour ce projet, ce sont les raisons pour lesquelles que nous avons choisi le streaming :
#### Analyse en temps réel : 
Le streaming nous permet de regarder les données au moment où elles arrivent, ce qui est très important pour voir comment notre système fonctionne en ce moment et pour prédire ce qui va se passer dans le futur.
#### Traitement continu : 
Avec le streaming, on traite les données dès qu'elles arrivent, ce qui veut dire qu'on voit toujours la situation actuelle des données. 
#### Réactivité accrue : 
Le streaming nous permet de réagir vite quand il y a des événements ou des changements dans les données. Ça nous aide à prendre des décisions rapidement. 

### 4. Technologies Utilisées:
#### Service Web: Amazon EC2 avec NGINX et FastAPI
#### Ubuntu avec Docker: configuration de l’environnement de déploiement des composant de la pipeline
#### Capture de données : Debezium, Crawler
#### Traitement des données : Apache NiFi, Python
#### Streaming d'événements : Kafka
#### Stockage de données : PostgreSQL, Amazon S3
#### Analyse des données : Amazon Athena, Amazon Glue
#### Visualisation des données : Power BI 

## Déploiement du projet
Les étapes pour mettre en œuvre le projet :
### 1-Créer une VM Ubuntu avec AWS EC2 pour lancer une API (FastAPI) à partir des données stockées sur S3 :

- ***Démarrez une instance EC2 sur AWS***
```
  Description
Canonical, Ubuntu, 22.04 LTS, amd64 jammy image build on 2024-04-11
t2 Family, xLarge
1 volume(s) - 25 GiB
```
- ***Configurer les autorisations nécessaires pour accéder au compartiment S3 contenant les données (movies.csv et ratings.csv)***

- ***Établir la connexion vers Ubuntu via la ligne du commande, et clonez ce dossier dans le terminal, exécuter:***
```Bash
git clone https://github.com/Dan2195178/BigData-projet2.git
```
- ***Installez les outils necessaires***

Acceder au dossier et executer les commandes comme root:
```bash
sudo apt-get update
sudo apt install python3-pip
```
```python
pip3 install -r requirements.txt

```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/1535c165-a993-4808-9804-a90a3fb61874)

 ```
  REQUIREMENTS
uvicorn
boto3
toml
fastapi
requests
```
- ***Installez et configurer nginx***
```bash
sudo apt install nginx
cd /etc/nginx/sites-enabled/
sudo nano fastapi_nginx
 ```
 ```
 CONFIGURATON 
server {
        listen 80;
        server_name <server-public-ip>;
        location / {
                proxy_pass http://127.0.0.1:8000;
        }
}

 ```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/f9616934-5b7d-4992-ae0c-62e74b627ae1)

Redémarrer le service nginx
 ```bash
service nginx restart
 ```
- ***Configurez un serveur web Fastapi, sur l'instance EC2***

Servir du fichier `api.py` pour la création de l'application FastAPI pour interagir avec la source des données S3 bucket (rating.csv) et configurer les endpoints des données.

Création et configuration d'un fichier `config.toml` pour fournir la clé d’accès du bucket
```
[s3]
keyid="access key"
keysecret="secret access key"
 ```
Maintenant on peut exécuter l'application FastAPI:
 ```python
python3 -m uvicorn api:app
 ```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/9e8c6e0d-4d2e-447b-afd0-ff21b5395a26)

On ouvre l'adresse IP de l'instance EC2 on a l'interface suivante :

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/fa7cd864-858a-419e-afe6-5e174003c843)

Nous ajoutons `/docs` pour accéder au swagger :

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/90503609-7846-4b6f-b193-3762ac50f8d8)

En exécutant `GET/rating`, nous obtenons le schéma de données de l'API :

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/cf2638d6-18dc-43dc-92c0-f8574af67be1)

> L'application doit rester en exécution tout au long du projet
### **2. Installer NiFi, Debezium, Kafka, PostgreSQL à l'aide d'un Docker Compose :**

- ***Lancer fichier docker-compose.yml pour démarrer les conteneurs NiFi, Kafka et PostgreSQL avec les configurations spécifiées***

on se placant toujours dans le dossier de projet, executons les commandes tant que root:
 ```bash
apt install docker-compose
  ```
```bash
docker-compose up -d
```
```bash
docker ps
```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/7f4af7d4-131a-4fe4-8d39-4e14280acecf)

### **3. Configurer la base de données :**
Pour accéder au conteneur de la base de données postgres, executer:
```bash
docker exec -it postgres /bin/bash
```
Se connecter à la base de données Postgres:
```sql
psql -U postgres
```
Créer une database:
```sql
CREATE DATABASE stream_db;
```
Se connecter à stream_db :
```sql
 \c stream_db;
```
Créer les tables :

*La table movies pour les donnees en batch*
``` SQL
CREATE TABLE movies (
	movieId SERIAL PRIMARY KEY,
	title VARCHAR(45) NOT NULL,
        genres VARCHAR(45) NOT NULL
);
```
*La table ratings pour les donnees en streaming*

```sql
CREATE TABLE ratings (
	user_id INT,
	movieId INT NOT NULL,
	rating FLOAT NOT NULL,
        timestamp INT NOT NULL,
	event_time TIMESTAMP DEFAULT NOW()
);
```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/b5646d6d-a253-42ce-b784-19a7f1bd6ab8)
Lister tous les tables de stream_db pour vérifier s'ils sont bien créées :
```sql
 \dt
```
Sortir de conteneur postgres :
```sql
exit
exit
```
### **4. Utiliser l'interface NiFi pour récupérer les données et les mettre dans une base de données PostgreSQL :**
Accéder au conteneur de NiFi, exécuter:
```bash
docker exec -it nifi /bin/bash
```
Les commandes pour ajouter le jdbc de Postgres à NiFi:
```bash
mkdir custom-jars
cd custom-jars
wget https://jdbc.postgresql.org/download/postgresql-42.5.4.jar
```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/d89bfd23-382f-4194-bc64-2626c810a1d0)

- ***Accédez à l'interface NiFi via le navigateur web en ajoutant le port `:8081/nifi` à l'adresse ip***
- Configurez les deux flux de données pour récupérer les données
  -  Récupérer le fichier "movies.csv" (batch) à partir du bucket et les charger dans la table "movies"
 ![nifi1](https://github.com/Khadijaessa/BigData-projet2/assets/123899056/b56a3e7b-42b3-4fbe-9c55-fe013e569d3b)
  -  Récupérer les données de ratings (streaming) à partir de l’API et les charger dans la table "ratings"
![data-pipeline (10)](https://github.com/Khadijaessa/BigData-projet2/assets/123899056/7aa11542-9d03-48bb-8e45-1783a586c46f)
> La Template du pipeline NiFi est présente dans le dossier de projet sous le nom `flux_nifi.XML`, il suffit de l’importer et ajouter les clés d’accès du bucket dans les processeurs `listS3` et `fetchS3Object`.
### **5. Créer un connecteur Debezium pour détecter les changements sur la base de données PostgreSQL :**
- ***Configurez et démarrez un connecteur Debezium pour surveiller les changements sur la base de données stream_db qui publie les modifications dans un topic Kafka***

Sur la ligne de commande , nous exécutons le connecteur Debezium:
```bash
curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '
{
 "name": "test-connector",
 "config": {
   "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
   "database.hostname": "postgres",
   "database.port": "5432",
   "database.user": "postgres",
   "database.password": "postgres",
   "database.dbname" : "stream_db",
   "database.server.name": "dbserver1",
   "topic.prefix": "dbserver1",
   "plugin.name": "pgoutput",
   "time.precision.mode" : "connect",
  "transforms": "tsConverter",
  "transforms.tsConverter.type": "org.apache.kafka.connect.transforms.TimestampConverter$Value",
  "transforms.tsConverter.field": "time",
  "transforms.tsConverter.format": "dd-mm-yyyy hh:mm:ss",
  "transforms.tsConverter.target.type": "string"
 }
}'

```
Vérifier que le connecteur est actif:
```bash
curl -i http://localhost:8083/connectors/test-connector/status
```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/c401e5ff-7ed0-4276-ad0e-85e20c4dc7e9)

Accéder au conteneur Kafka et lister les sujets créés 
```bash
docker exec -it kafka /bin/bash
```
```bash
kafka-topics.sh --bootstrap-server=localhost:9092 --list
```
![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/63d43c91-a46b-4903-b5c9-2a4e576d3491)

On doit avoir deux topics créés automatiquement, sous les noms "dbserver1.public.movies" et "dbserver1.public.ratings".

### **6. Utiliser Apache Kafka pour faire le traitement de flux de données en temps réel et les charger sur s3 en exécutant les scripts Python qui consomme les topics spécifiés du Kafka :**
- ***Créer le bucket dans AWS S3 où sont stockés les flux de données***

- ***Créer deux fichiers en Python et les exécuter pour consommer les topics publiées dans Kafka, suivéillant par le Debezium du changement des deux tables du stream_db , et stockez-les dans le bucket S3***
  
Avant on aura besoin des outils pour que l'exécution des consommateurs soit réussie:
```python
pip install kafka-python
pip install s3fs
```

Exécutons un par un maintenant les deux consommateurs `consumer_movies.py` et `consumer_ratings.py` sur deux lignes de commande différentes.

Notez que dans le NiFi, le pipeline pour la table ratings soit déja démarré et FastAPI en python aussi devrait être en cours d'exécution. 

```puthon
python3 consumer_ratings.py
```

S'assurer que la table movies ne soit pas vide pour avoir des réactions lorsque les commandes suivants est en cours d'exécution.

```python
python3 consumer_movies.py
```

Une fois les deux scripts exécutés, nous devrions recevoir des messages indiquant que le stockage a réussi.
> Les données sur les films seront chargées dans le bucket par lots, puisqu'il s'agit d'une table de base, qui contient les données sur les films dont nous voulons suivre leurs tendances, par contre les données de ratings seront stockées ligne par ligne comme ils sont générés via l'API, debezium est connecté aux deux tables donc il détecte les insertions de films s'il y en a, et les avis des utilisateurs.
## Configuration de l'environnement de traitement (plus de details sur cette partie dans le fichier word)
### **1. Configuration de AWS Glue et AWS Athena:**
- ***Configuration de AWS Glue et AWS Athena***

Aller vers AWS Glue après crawlras et créer crawler

Ajouter les deux dossiers créés dans le bucket comme source de données :

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/3a53310a-3f8b-4d6c-acac-a85031108810)

Création d’un rôle IAM:

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/e6eb169e-0a95-4d6c-8a10-06e1b0893f1d)

Créer et exécuter le Crawler:

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/c0ff68d6-f9d6-4389-8cf4-0cb9b4afad8c)

- ***Requêter les données avec Athena***

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/8a37d6f7-d337-4760-ba14-9f607bbd3a66)

### **2. La visualisation des données:**
- ***Installer le pilote ODBC***
- ***Créer une nouvelle clé d’accès sur AWS IAM et choisir third-party service***
- ***Installer le pilote ODBC***
- ***Entrer dans le power BI et ajouter le ODBC de Athena***
  
  Power BI nous demandera de saisir les informations d'identification (la clé d’accès créer pour Athéna), après la connexion, on peut voir les deux tables de bucket.
  
  ![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/cf68cf73-b135-4a3d-b57b-0410704524a4)

    > Et là on peut commencer notre visualisation, il suffit de rafraîchir la table `bucket_kafka_stream`, pour vois les rapports en temps réel (voir la video pour plus de details).

Voici deux exemples de rapports pouvant être réalisés avec ce type de données:

![image](https://github.com/Dan2195178/BigData-projet2/assets/123899056/18e8c2cd-130a-4385-9a7d-1bad0cd87bb9)

![image](https://github.com/Dan2195178/BigData-projet2/assets/89165325/7a468f85-9b6c-4018-aa4a-6d3a9a0ab6be)


## Conclusion :
La mise en place de ce pipeline de données en temps réel pour évaluer les évaluations sur des films a été une expérience enrichissante. À travers l'utilisation de divers outils comme Apache NiFi, PostgreSQL, Debezium et Kafka, nous avons pu créer un flux de données robuste et efficace, de la capture initiale des évaluations à leur stockage, analyse et visualisation.

Apache NiFi nous a fourni une plateforme flexible et intuitive pour la collecte des données, permettant une intégration simple avec différentes sources (S3, API) et une manipulation simple des flux de données vers Postgres database (base de données principale). Debezium permet la capture des modifications de données en temps réel, et les publier dans un topic Kafka, ce dernier a été cruciale pour assurer la scalabilité et la résilience de notre système, permettant le streaming efficace des données entre les différents composants du pipeline. 
Ces technologies offrent une base solide pour la construction de systèmes de traitement de données distribuées robustes, avec un potentiel significatif pour répondre aux besoins croissants en matière d'analyse de données en temps réel dans divers domaines d'application, y compris celui de l'évaluation des films.






