NAME=cloudmesh-mongo

image:
	docker build . -t $(NAME)

start:
	docker run --rm -d -p 27017:27017/tcp --name $(NAME) $(NAME):latest

stop:
	docker container ls -q --filter name=$(NAME) | xargs docker stop

shell:
	docker exec -it $(NAME) bash

mongo:
	docker exec -it $(NAME) mongo
