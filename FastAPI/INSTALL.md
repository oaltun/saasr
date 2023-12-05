# SAASR BACKEND DOCKER BASED INSTALLATION

This installation is for development purposes.

## Installation using docker

### Install docker

Install docker. If possible enable non-root docker execution. Otherwise you will need to prepend 'sudo' to each docker command.

### Set environment variables

Copy .env.example to .env, and enter values for those variables.

### Start docker-compose network

Following command will build the docker image and start the docker compose network. `sudo` is not needed if you installed docker non-root.

```bash
sudo docker compose up
```

The python files are NOT embedded to the image. Instead, when you edit the files, they are automatically synched.

### Get an interactive shell to the container

```bash
sudo docker exec -it fastapi /bin/bash
```

This will give you a nice bash shell that you can run following commands:

Apply database migrations:

```bash
python -m alembic upgrade head
```

Populate initial data:

```bash
python ./app/initial_data.py
```

Run tests:

```bash
pytest -x
```

### Visit online API documentation

http://127.0.0.1:8888/api/docs

## Development notes

### Create database migrations if necessary

```bash
sudo docker exec -it fastapi /bin/bash
alembic revision --autogenerate -m "message"
```
