DJANGO   := phillipjensen/payment-monitor-backend
IMG_DJANGO    := payment-monitor-backend:${GITHUB_SHA}
DJANGO_LATEST_LOCAL    := payment-monitor-backend:latest
LATEST_DJANGO := ${DJANGO}:${GITHUB_SHA}

CELERY   := phillipjensen/payment-monitor-backend-celery
IMG_CELERY    := payment-monitor-backend-celery:${GITHUB_SHA}
CELERY_LATEST_LOCAL    := payment-monitor-backend-celery:latest
LATEST_CELERY := ${CELERY}:${GITHUB_SHA}

CELERY_BEAT   := phillipjensen/payment-monitor-backend-celery-beat
IMG_CELERY_BEAT    := payment-monitor-backend-celery-beat:${GITHUB_SHA}
CELERY_BEAT_LATEST_LOCAL    := payment-monitor-backend-celery-beat:latest
LATEST_CELERY_BEAT := ${CELERY_BEAT}:${GITHUB_SHA}

NGINX   := phillipjensen/payment-monitor-nginx
IMG_NGINX    := payment-monitor-nginx:${GITHUB_SHA}
NGINX_LATEST_LOCAL    := payment-monitor-nginx:latest
LATEST_NGINX := ${CELERY_BEAT}:${GITHUB_SHA}



build-amd64:
	@docker build -t ${IMG_DJANGO} -t ${DJANGO_LATEST_LOCAL} -f ./payment-monitor-backend/dockerfiles/Django payment-monitor-backend/.
	@docker build -t ${IMG_CELERY} -t ${CELERY_LATEST_LOCAL} -f ./payment-monitor-backend/dockerfiles/Celery payment-monitor-backend/.
	@docker build -t ${IMG_CELERY_BEAT} -t ${CELERY_BEAT_LATEST_LOCAL} -f ./payment-monitor-backend/dockerfiles/Beat payment-monitor-backend/.
	@docker build -t ${IMG_NGINX} -t ${NGINX_LATEST_LOCAL} -f ./payment-monitor-backend/dockerfiles/Nginx .
	@docker tag ${IMG_DJANGO} ${LATEST_DJANGO}
	@docker tag ${IMG_CELERY} ${LATEST_CELERY}
	@docker tag ${IMG_CELERY_BEAT} ${LATEST_CELERY_BEAT}
	@docker tag ${IMG_NGINX} ${NGINX_BEAT}

	@docker tag ${DJANGO_LATEST_LOCAL} ${DJANGO}:latest
	@docker tag ${CELERY_LATEST_LOCAL} ${CELERY}:latest
	@docker tag ${CELERY_BEAT_LATEST_LOCAL} ${CELERY_BEAT}:latest
	@docker tag ${NGINX_LATEST_LOCAL} ${NGINX}:latest

push-amd64:
	@docker push ${LATEST_DJANGO}
	@docker push ${LATEST_CELERY}
	@docker push ${LATEST_CELERY_BEAT}
	@docker push ${LATEST_NGINX}
	@docker push ${DJANGO}:latest
	@docker push ${CELERY}:latest
	@docker push ${CELERY_BEAT}:latest
	@docker push ${NGINX}:latest


login:
	@docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}
	
