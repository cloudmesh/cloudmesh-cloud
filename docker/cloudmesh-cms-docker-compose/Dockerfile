FROM ubuntu:19.04

RUN set -x \
        && apt-get -y update \
        && apt-get -y upgrade \
        && apt-get -y --no-install-recommends install build-essential \
                                                      git \
                                                      curl \
                                                      wget \
                                                      sudo \
        && apt-get -y install python3 \
                              python3-pip \
        && rm -rf /var/lib/apt/lists/* \
        && update-alternatives --install /usr/bin/python python /usr/bin/python3 1 \
        && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 \
        && pip install cloudmesh-installer

RUN mkdir cm
WORKDIR cm

RUN cloudmesh-installer git clone cloud
RUN cloudmesh-installer install cloud -e

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
