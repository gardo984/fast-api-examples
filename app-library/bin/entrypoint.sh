#!/bin/sh

#CONFIG_FILE="main.settings.development"

arg=$1
APP_DIR=/usr/src/backend
DEFAULT_PORT=8001
cd ${APP_DIR}

if [ $arg = "start" ]; then
    uvicorn app.main:app --reload --host 0.0.0.0 --port ${DEFAULT_PORT}

elif  [ $arg = "migrate" ]; then
    alembic upgrade head

elif  [ $arg = "load_dev_data" ]; then
    echo "load_dev_data command"

elif  [ $arg = "setup" ]; then
    alembic upgrade head && \
        uvicorn app.main:app --reload --host 0.0.0.0 --port ${DEFAULT_PORT}

elif [ $arg = "unit_tests" ]; then
    echo "unit-tests command"

elif  [ $arg = "deploy" ]; then
    # for test purposes
    alembic upgrade head && \
        uvicorn app.main:app

elif [ $arg = "nginx" ]; then
    # the following sentence is for a bug that happen in k8s
    echo 'rc_provide="loopback net"' >> /etc/rc.conf
    
    # process migrations and app setup
    alembic upgrade head && uvicorn app.main:app

    # start uwsgi in the background and nginx
    #uwsgi --ini /etc/wsgi/uwsgi.ini &
    sudo openrc
    sleep 2 && \
        sudo rc-service nginx start && \
        tail -f /var/log/nginx/*

elif [ $arg == "debug" ]; then
    exec /bin/sh
else
    exec "$@"
fi