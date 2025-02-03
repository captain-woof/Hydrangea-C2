# Hydrangea-C2

## Components

### Team server

Team server (`team-server/main.py`) mediates between agents, listeners and clients.

### Client

Client (`client/main.py`) is the client to use to connect to Tasker.

### Listener

Listeners (`team-server/listeners/*.py`) are scripts that start a server, intended to receive communication from agents. They are part of team server since they are started on team server.

### Database

There's a MySQL database in `team-server/database` that needs to be setup with docker. This database stores all necessary persistent information.

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

### Starting team server

```bash
python3 -m virtualenv venv
source ./venv/bin/activate

python3 ./main.py -H 127.0.0.1 -P 6060
```

### Stopping team server

```bash
Ctrl + C # yes, just interrupt
```

### Stopping MySQL database

```bash
docker compose down -f ./database/compose.yaml -d
```

### Removing MySQL volume

```bash
sudo docker volume rm team-server_hydrangea-mysql # remove MySQL's docker volume
```

## Client guide

**Note: All client stuff is in `client/` directory. Unless otherwise stated, use this folder as your current directory when starting the client.**

### Starting client

```bash
python3 ./main.py -H 127.0.0.1 -P 6060
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

*Remember: Usernames are unique*

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