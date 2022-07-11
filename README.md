# Payments monitor backend

A brief description of what this project does and who it's for


## Installation

#### pre-requisites
The payments monitor backend is running as a Docker Swarm Cluster. This means that you must have a docker swarm running on your machine before you can start the backend.

To do so you must install docker and docker-compose.

Once both are installed you must initiate the swarm cluster by running `docker swarm init`

### Build

To build all services: `docker-compose -f docker-compose-dev.yml build`

### Dev deploy

To deploy and start all services locally: 
`docker stack deploy -c docker-compose-dev.yml payments`

If running on Windows you should add:
`127.0.0.1 api.localhost`
to `C:\Windows\System32\drivers\etc\hosts`
otherwise there is problem with routing in command line to api.localhost.

`/monitor-backend` folder is mounted inside Django and Celery containers, 
so there is no need of rebuilding containers after code change during development, besides the
exception to updating pip requirements.

Normal restart (if not related to background tasks). 
Django will pickup code changes without rebuilding:
* For django: `docker service update --force payments_django`

Full restart (for example when requirements changes or change in background tasks):
* Remove stack: `docker stack rm payments`
* Run stack again: `docker stack deploy -c docker-compose-dev.yml payments`


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




### How to start the backend

``