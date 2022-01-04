#!/bin/bash
set -eux

SCRIPT_DIR=$(dirname $(readlink -f $0))
CONTAINER_NAME=localhost/centos8-builder

pushd ${SCRIPT_DIR}/../
  name=${PWD##*/}
  pushd ..
  tar -czf /tmp/directord.tar.gz --exclude .tox "${name}"
  mv /tmp/directord.tar.gz ${SCRIPT_DIR}/container-build/
  popd
popd

export RELEASE_VERSION=$(awk -F'"' '/version/ {print $2}' ${SCRIPT_DIR}/../directord/meta.py)

buildah bud -t ${CONTAINER_NAME} ${SCRIPT_DIR}/container-build
podman run -it -v ${SCRIPT_DIR}:/home/builder/rpm:z --env RELEASE_VERSION="${RELEASE_VERSION}" ${CONTAINER_NAME}:latest
