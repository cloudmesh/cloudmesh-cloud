package=cloud
UNAME=$(shell uname)
VERSION=`head -1 ../../VERSION`

define banner
	@echo
	@echo "###################################"
	@echo $(1)
	@echo "###################################"
endef

######################################################################
# DOCKER
######################################################################

USERNAME=`cms config value cloudmesh.data.mongo.MONGO_USERNAME`
PASSWORD=`cms config value cloudmesh.data.mongo.MONGO_PASSWORD`

mongo:
	docker run -d \
	    -p 127.0.0.1:27017:27017 \
	    --name cloudmesh-mongo \
	    -e MONGO_INITDB_ROOT_USERNAME=$(USERNAME) \
	    -e MONGO_INITDB_ROOT_PASSWORD=$(PASSWORD) \
	    mongo

all: clean image

image:
	$(call banner, "Building cloudmesh/cloudmesh-${package}")
	docker build -t cloudmesh/cloudmesh-${package}:${VERSION} .
	docker tag cloudmesh/cloudmesh-${package}:${VERSION} \
		cloudmesh/cloudmesh-${package}:latest
	$(call banner, "tag cloudmesh/cloudmesh-${package}:${VERSION} cloudmesh/cloudmesh-${package}:latest")

shell:
	docker run -v `pwd`:/cloudmesh -w /cloudmesh --rm \
	-it cloudmesh/cloudmesh-${package}:${VERSION} /bin/bash

clean:
	-docker ps
	-docker image ls
	-docker kill $$(docker ps -q --force)
	-docker rm $$(docker ps -a -q)
	-docker rmi $$(docker images -q)

push:
	docker push cloudmesh/cloudmesh-${package}:${VERSION}
