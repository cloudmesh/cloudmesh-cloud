package=cloud
UNAME=$(shell uname)
VERSION=`head -1 ../VERSION`

define banner
	@echo
	@echo "###################################"
	@echo $(1)
	@echo "###################################"
endef

######################################################################
# DOCKER
######################################################################

image:
	$(call banner, "Building cloudmesh/cloudmesh-${package}")
	docker build -t cloudmesh/cloudmesh-${package}:${VERSION} .
	docker tag cloudmesh/cloudmesh-${package}:${VERSION} \
    			cloudmesh/cloudmesh-${package}:latest
	$(call banner, "tag cloudmesh/cloudmesh-${package}:${VERSION} cloudmesh/cloudmesh-${package}:latest")

image-push:
	docker push cloudmesh/cloudmesh-${package}

shell:
	docker run -v `pwd`:/cloudmesh -w /cloudmesh --rm \
	-it cloudmesh/cloudmesh-${package}:${VERSION} /bin/bash

docker-clean:
	-docker kill $$(docker ps -q)
	-docker rm $$(docker ps -a -q)
	-docker rmi $$(docker images -q)

docker-push:
	docker push cloudmesh/cloudmesh-${package}:${VERSION}
