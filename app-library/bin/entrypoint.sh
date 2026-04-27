#!/bin/sh

#CONFIG_FILE="main.settings.development"

arg=$1
APP_DIR=/usr/src/backend
APP_PORT=8000
cd ${APP_DIR}

if [ $arg = "start" ]; then
    uvicorn app.main:app --reload --host 0.0.0.0 --port ${APP_PORT}

elif  [ $arg = "migrate" ]; then
    alembic upgrade head

elif  [ $arg = "load_dev_data" ]; then
    echo "load_dev_data command"

elif  [ $arg = "setup" ]; then
    alembic upgrade head && \
        uvicorn app.main:app --reload --host 0.0.0.0 --port ${APP_PORT}

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
    alembic upgrade head
    # run gunicorn on the background
    gunicorn app.main:app --bind 0.0.0.0:${APP_PORT} \
            --worker-class uvicorn.workers.UvicornWorker \
            --workers 2 \
            --access-logfile /var/log/gunicorn/access.log \
            --error-logfile /var/log/gunicorn/error.log &

    # start nginx
    sudo openrc
    sleep 2 && \
        sudo rc-service nginx start && \
        tail -f /var/log/nginx/* /var/log/gunicorn/*

elif [ $arg == "debug" ]; then
    exec /bin/sh
else
    exec "$@"
fi