# Payments monitor backend

A brief description of what this project does and who it's for


## Installation

#### pre-requisites
The payments monitor backend is running as a Docker Swarm Cluster. This means that you must have a docker swarm running on your machine before you can start the backend.

To do so you must install docker and docker-compose.

Once both are installed you must initiate the swarm cluster by running `docker swarm init`

### Build

To build all services: `docker-compose -f docker-compose-dev.yml build`

### Configuration

There are two config files:

For development, you can use values provided in .template files (copy them accordingly).

`.envs/.db` - Postgres db config (self explanatory)
`.envs/.django` - Django config 

DJANGO_SECRET=generateme - used for DB encryption
JWT_SIGNING_KEY=generateme - used for frontend authentication and key signing. It must match
variable set in frontend (look for frontend Readme file).
Django implementation of JSON Web Tokens standard

### Dev deploy

To deploy and start all services locally: 
`docker stack deploy -c docker-compose-dev.yml payments`

To check if service are running use:
`docker stack ps --no-trunc payments`

To follow logs of the service
`docker service logs payments_django -f`

If running on Windows you should add:
`127.0.0.1 api.localhost`
to `C:\Windows\System32\drivers\etc\hosts`
otherwise there is problem with routing in command line to api.localhost.

`/monitor-backend` folder is mounted inside Django and Celery containers, 
so there is no need of rebuilding containers after code change during development, besides the
exception to updating pip requirements.

Normal restart (if not related to background tasks). 
Django will pick up code changes without rebuilding:
* For django: `docker service update --force payments_django`

Full restart (for example when requirements changes or change in background tasks):
* Remove stack: `docker stack rm payments`
* Run stack again: `docker stack deploy -c docker-compose-dev.yml payments`

Deleting the database (restoring to default state)
* Remove stack: `docker stack rm payments` (wait a bit for containers to be stopped)
* Delete postgres volume (wipes all data): `docker volume rm payments_db_data`
* Run stack again: `docker stack deploy -c docker-compose-dev.yml payments`

### Optional - Django admin

* Create superuser
* Exec into container django:
* Find container id: `docker ps -q -f name=payments_django` 
* Go inside container: `docker exec -it container_id /bin/sh`
* Django management script: `python manage.py createsuperuser`
* Alternatively, you can set it manually in the database of your user:
Table: api_users, Column: is_superuser
* 


### Docker tricks

* You can use https://dockstation.io/ to manage containers a bit easier.

Services:
* traefik - internal load balancer. In production: it will renew SSL certificates.
* django - backend itself. Django is using postgres for Database.
* redis - message broker for the background tasks. It is used only for Celery background task communication.
* celery - background worker itself completing background task.
* celery_beat - background task supervisor.  
* postgres

## Celery - background service

Task are defined inside Django and Django has integration with Celery. 
Celery-beat will pick up the task automatically and put it into one of the workers.



