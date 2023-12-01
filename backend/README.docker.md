# SAASR PROJECT BACKEND

Install docker non-root: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04

If you did not install docker as non-root, you will need to prepend '' to each command, there will be problems connecting docker image from vscode.

# rebuild and push image to docker (assume dockerhub username is dockerhubusername)

## cd to the directory this README.md is.Then:

docker build -t saasrbackend .
docker tag saasrbackend:latest dockerhubusername/saasrbackend:latest
docker login -u dockerhubusername
docker push dockerhubusername/saasrbackend:latest

# remove existing swarm / network

docker stack rm exs
docker swarm leave --force

# create new swarm

docker swarm init

# deploy our app

docker stack deploy exs -c backend.yml

# see service logs

docker service ls
docker service logs -f --raw exs_backend_api

# apply database migrations

docker exec $(docker ps -q -f name=exs_backend_api) alembic upgrade head

# populate initial data

docker exec $(docker ps -q -f name=exs_backend_api) python ./app/initial_data.py

# run tests

docker exec $(docker ps -q -f name=exs_backend_api) pytest -x

# visit online API documentation

http://127.0.0.1:8888/api/docs

# get interactive shell example

docker exec -ti $(docker ps -q -f name=exs_backend_api) bash

# create database migrations if necessary.

docker exec $(docker ps -q -f name=exs_backend_api) alembic revision --autogenerate -m "message"

# docker cleanup.

// remove network, prune all containers
docker container prune

// prune all images
docker image prune

// prune unused everything
docker system prune -a

// remove all containers
docker rm -f $(docker ps -a -q)

# remove selected volumes: may erase data!

// find all volumes:
docker volume ls
// delete unvanted volumes:
docker volume rm <volume_name>

# remove all docker data. Notice: will erase database data!

docker volume rm $(docker volume ls -q)

# query examples

docker service ps exs_backend_api
docker ps -q -f name=exs_backend_api
docker image ls
docker service ls

# log view examples

docker service logs -f exs_backend_api --raw
docker service ps exs_backend_api
docker inspect $(docker ps -q -f name=exs_backend_api)

# get system architecture

docker info|grep Architecture
