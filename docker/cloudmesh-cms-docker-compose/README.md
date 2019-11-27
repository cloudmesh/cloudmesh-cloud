
1. Download the source code: https://github.com/cloudmesh/cloudmesh-cloud/tree/master/docker/cloudmesh-cms-docker-compose

    It contains three files:
    * Dockerfile
    * docker-compose.yml
    * mongo-init.js

2. Place all the above three files in a separate empty folder.
3. Modify the above files by replacing the placeholder with your own username and password for MongoDB.
4. Go to this folder in a terminal
5. Run docker-compose up
    It is expected that the two containers will be started up.
6. Login the CMS container
    1. Run `docker ps` to check the container ID of the CMS container
    2. Run `docker exec -it <container-ID> bash`
