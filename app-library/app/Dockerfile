
FROM python:3.12-alpine AS app-base

ENV APP_DIR=/usr/src/backend
ENV PROJECT_NAME=app
WORKDIR ${APP_DIR}
ARG UID
RUN adduser --disabled-password -u ${UID} -s /bin/ash app && \
	chown app:app ${APP_DIR}

COPY --chown=app app ./
COPY --chown=app alembic ./
COPY --chown=app requirements.txt ./
COPY bin/entrypoint.sh ${PROJECT_NAME}/entrypoint.sh
COPY bin/wait-for-it.sh ${PROJECT_NAME}/wait-for-it.sh

## install sudoers and enable sudo without password prompt

RUN chmod +x app/entrypoint.sh ${PROJECT_NAME}/wait-for-it.sh && \
	apk add sudo && \
	sed -e 's/^# \(%wheel.*NOPASSWD*\)/\1/g' -i /etc/sudoers && \
	addgroup app wheel

## install postgresql and mysql connectors

RUN ls -ltr && \
	apk add -u gcc musl-dev postgresql-client \
				mariadb-client mariadb-dev mariadb-connector-c-dev \
				libffi-dev curl 

ENV PATH="${PATH}:/home/app/.local/bin"

## install nginx

RUN apk update && \
	apk add nginx --no-cache && \
	adduser -D -g 'www' www && \
	mkdir -p /www && \
	chown -R www:www /var/lib/nginx && \
	chown -R www:www /www && \
	mkdir -p /run/nginx/

# mkdir -p /var/log/uwsgi/ && chown app:app /var/log/uwsgi/


COPY --chown=www docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=www docker/nginx/index.html /www/index.html
# COPY --chown=app docker/wsgi /etc/wsgi

## install rsyslog

WORKDIR /etc/apk/keys 
##RUN echo 'http://alpine.adiscon.com/3.7/stable' >> /etc/apk/repositories
##RUN wget http://alpine.adiscon.com/rsyslog@lists.adiscon.com-5a55e598.rsa.pub && \
RUN	apk update && \
	apk add rsyslog g++

## install openrc

RUN apk add util-linux openrc
VOLUME /sys/fs/cgroup
RUN rc-update add rsyslog default && \
	mkdir -p /run/openrc && \
	touch /run/openrc/softlevel && \
	chown :app /etc/rc.conf  && \
	chmod 0674 /etc/rc.conf

## install python pandas and additional packages

WORKDIR ${APP_DIR}/${PROJECT_NAME}
RUN for x in $(echo "main community testing"); \
	do echo "https://dl-cdn.alpinelinux.org/alpine/edge/${x}" >> /etc/apk/repositories; \
	done && \
	apk update && \
	apk add py3-pandas && \
	pip3 install --upgrade pip 

# pip3 install poetry
	

## install nodejs and npm

RUN apk update && apk add nodejs npm
#WORKDIR ${APP_DIR}
##RUN npm install

USER app
WORKDIR ${APP_DIR}
# RUN mkdir -p media/{xls,pdf,uploads}	
ENV PYTHONPATH="/usr/lib/python3.12/site-packages/"


## target: develop

FROM app-base AS dev
USER root
RUN pip install -r requirements.txt
USER app

EXPOSE 8001
ENTRYPOINT ["./entrypoint.sh"]
CMD ["deploy"]


## target: production

FROM app-base AS prod
USER root
RUN pip install -r requirements.txt
USER app

EXPOSE 8001
ENTRYPOINT ["./entrypoint.sh"]
CMD ["deploy"]
