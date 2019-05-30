#!/usr/bin/env bash

DIR=$(cd `dirname $0` && pwd)

if [[ -z "${ANIME_SERVICE_CLIENT_NAME}" ]]
then
    echo "Please set the ANIME_SERVICE_CLIENT_NAME env variable"
    exit 1
else
    kubectl apply -f ${DIR}/manifest/pvc.yml
    envsubst '${ANIME_SERVICE_CLIENT_NAME}' < ${DIR}/manifest/deployment.yml > deployment_injected.yml
    kubectl apply -f deployment_injected.yml
    rm deployment_injected.yml

    kubectl apply -f ${DIR}/manifest/service.yml
fi