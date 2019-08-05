FROM python:3

MAINTAINER Gregor von Laszewski <laszewski@gmail.com>

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y --no-install-recommends install build-essential
RUN apt-get -y --no-install-recommends install git
RUN apt-get -y --no-install-recommends install curl
RUN apt-get -y --no-install-recommends install wget
RUN apt-get -y --no-install-recommends install sudo

RUN pip install cloudmesh-installer

RUN mkdir cm
WORKDIR cm

RUN ls
RUN echo
RUN cloudmesh-installer git clone cloud
RUN cloudmesh-installer install cloud -e

