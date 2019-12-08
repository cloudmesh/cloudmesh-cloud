FROM ubuntu:19.04

MAINTAINER Gregor von Laszewski <laszewski@gmail.com>

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y --no-install-recommends install build-essential
RUN apt-get -y --no-install-recommends install git
RUN apt-get -y --no-install-recommends install curl
RUN apt-get -y --no-install-recommends install wget
RUN apt-get -y --no-install-recommends install sudo
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN apt-get -y --no-install-recommends install mongodb


RUN pip install cloudmesh-installer

RUN mkdir cm
WORKDIR cm

RUN ls
RUN echo
RUN cloudmesh-installer git clone cloud
RUN cloudmesh-installer install cloud -e

# RUN cms help

# RUN cms config set cloudmesh.data.mongo.MONGO_AUTOINSTALL=True

# RUN openssl rand -base64 32 > /root/.cloudmesh/tmp.txt
# RUN cms config set cloudmesh.data.mongo.MONGO_PASSWORD=$(cat /root/.cloudmesh/tmp.txt)
# RUN rm /root/.cloudmesh/tmp.txt

# RUN cms help


# RUN cms admin mongo install --nosudo

# ENV PATH="/root/local/mongo/bin:${PATH}"

# RUN cms admin mongo create

#RUN /bin/bash -c "source ~/.bashrc"

## RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
## USER docker

# Add script to start mongodb at startup

# COPY docker-entrypoint.sh /usr/local/bin/
# RUN chmod 755 /usr/local/bin/docker-entrypoint.sh
# RUN ln -s usr/local/bin/docker-entrypoint.sh / # backwards compat
# ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["bash"]
