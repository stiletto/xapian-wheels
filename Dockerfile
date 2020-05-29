FROM docker.io/ubuntu:18.04 AS builder
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends --yes python3-sphinx git build-essential curl wget ca-certificates gpg gpg-agent software-properties-common zlib1g-dev
RUN add-apt-repository --yes ppa:deadsnakes/ppa
ARG python=python3.5
RUN apt-get update && apt-get install --no-install-recommends --yes python3-pip ${python} ${python}-dev
RUN ${python} -m pip install -U pip wheel setuptools
WORKDIR /root/xapian-wheels/
COPY xapian /root/xapian-wheels/xapian
COPY setup.py /root/xapian-wheels/
RUN ${python} setup.py bdist_wheel

FROM scratch
COPY --from=builder /root/xapian-wheels/dist/*.whl /

