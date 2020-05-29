#!/bin/bash
set -eu -o pipefail
VERSIONS=(3.5 3.6 3.7 3.8)
IMAGE_NAME="${IMAGE_NAME:-xapian-build}"
DOCKER="${DOCKER:-docker}"
mkdir -p dist
for version in "${VERSIONS[@]}"; do
    ${DOCKER} build -t "${IMAGE_NAME}:${version}" --build-arg python="python${version}" .
    pushd dist
    ${DOCKER} save "${IMAGE_NAME}:${version}" | tar -xO --wildcards '[a-f0-9]*[a-f0-9].tar'|tar -xv --wildcards '*.whl'
    popd
done
