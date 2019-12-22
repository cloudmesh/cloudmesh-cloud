nametag=cms
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

all: clean image

image:
	$(call banner, "Building cloudmesh/cloudmesh-${nametag}")
	docker build -t cloudmesh/cloudmesh-${nametag}:${VERSION} .
	docker tag cloudmesh/cloudmesh-${nametag}:${VERSION} \
		cloudmesh/cloudmesh-${nametag}:latest
	$(call banner, "tag cloudmesh/cloudmesh-${nametag}:${VERSION} cloudmesh/cloudmesh-${nametag}:latest")

shell:
	docker run \
		-v `pwd`:/cloudmesh \
		-v ~/.ssh:/root/.ssh \
		-v ~/.cloudmesh:/root/.cloudmesh \
		-w /cloudmesh --rm \
		-it cloudmesh/cloudmesh-${nametag}:${VERSION} /bin/bash

clean:
	-docker system prune -a
	-docker images purge
	#-docker kill $$(docker ps -q)
	#-docker rm $$(docker ps -a -q) 
	#-docker rmi $(docker images -a -q) --force
	-docker ps
	-docker image ls

push:
	docker push cloudmesh/cloudmesh-${nametag}:${VERSION}
