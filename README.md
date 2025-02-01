# Hydrangea-C2

## Components

### Tasker

Tasker (`tasker/main.py`) is part of team-server, and its job is to mediate between listeners and clients. Clients can task agents via Tasker.

### Client

Client (`client/main.py`) is the client to use to connect to Tasker.

### Listener

Listeners (`listeners/*.py`) are scripts that start a server, intended to receive communication from agents. They are part of team server since they are started on team server.

## Team server guide

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

### Stopping

```bash
docker compose down # stops MySQL container
```

### Removing

```bash
sudo docker volume rm team-server_hydrangea-mysql # remove MySQL's docker volume
```

## Client guide

### Starting client

```bash
python3 ./client/main.py -H 127.0.0.1 -P 6060
```

At any point, invoke `help` command to see available commands. These commands are also listed below.

### Administration commands

Enter the `admin` context with below command first:

```
USER@Tasker (xx.xx.xx.xx:xx) > context admin
```

**Create new user**

```
USER@Tasker (xx.xx.xx.xx:xx) > Admin > newuser USERNAME PASSWORD ROLE
```

**Edit existing user's username**

```
USER@Tasker (xx.xx.xx.xx:xx) > Admin > editusername USERNAME NEW_USERNAME
```

**Edit existing user's password**

```
USER@Tasker (xx.xx.xx.xx:xx) > Admin > editpassword USERNAME NEW_PASSWORD
```

**Edit existing user's role**

```
USER@Tasker (xx.xx.xx.xx:xx) > Admin > editrole USERNAME NEW_ROLE
```

**Delete existing user**

```
USER@Tasker (xx.xx.xx.xx:xx) > Admin > deluser USERNAME
```

### Listener commands

### Agent commands