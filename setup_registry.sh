#!/bin/bash
# setup_registry.sh

REGISTRY_PORT=5000
REGISTRY_NAME="local-registry"

# Check if registry is already running
if docker ps -a --format '{{.Names}}' | grep -q "^${REGISTRY_NAME}$"; then
    echo "Registry container ${REGISTRY_NAME} already exists. Restarting..."
    docker start ${REGISTRY_NAME} || docker restart ${REGISTRY_NAME}
else
    echo "Starting new private registry on port ${REGISTRY_PORT}..."
    docker run -d \
      -p ${REGISTRY_PORT}:5000 \
      --restart=always \
      --name ${REGISTRY_NAME} \
      registry:2
fi

echo "Registry is running on localhost:${REGISTRY_PORT}"
echo "To use this registry from other nodes, use $(hostname -I | awk '{print $1}'):${REGISTRY_PORT}"
