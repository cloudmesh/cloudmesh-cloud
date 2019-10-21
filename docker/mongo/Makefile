build:
	docker build . -t cloudmesh-mongo

start:
	docker run --rm -d -p 27017:27017/tcp --name cloudmesh-mongo cloudmesh-mongo:latest

stop:
	docker container ls -q --filter name=cloudmesh-mongo | xargs docker stop
