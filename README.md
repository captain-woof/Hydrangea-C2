# Hydrangea-C2

## Components

### Tasker

Tasker (`tasker.py`) is part of team-server, and its job is to mediate between listeners and clients. Clients can task agents via Tasker.

### Listener

Listeners (`listeners/*.py`) are scripts that start a server, intended to receive communication from agents.

## Team server

**Note: All team server stuff is in `team-server/` directory. Unless otherwise stated, use this folder as your current directory when starting the team server.**

### Environment variables

Create a `.env` file (use `.env.example` as a template) for usage.

### Starting MySQL database

Once done, start the database:

```bash
docker compose up -f ./database/compose.yaml -d # starts MySQL in a docker and performs database setup
```

This starts a local (`127.0.0.1:3306`) MySQL database, with your chosen username and password in `.env`. Use this if you need to manually interact with the database.

### Starting Tasker

```bash
fastapi run --host 127.0.0.1 --port 6060 ./tasker/main.py
```

### Starting client

```bash
python3 ./client/main.py -H 127.0.0.1 -P 6060
```

### Stopping

```bash
docker compose down # stops MySQL container
```

### Removing

```bash
sudo docker volume rm team-server_hydrangea-mysql # remove MySQL's docker volume
```