docker-tutorial-1
=================

Run a simple Python web service in a Docker container, manually connected to a MongoDB container — then simplify the whole thing with Docker Compose.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running. No VM, no Vagrant, no extra tooling needed.

---

## Part 1: Running Containers Manually

This section walks through the core concepts: building an image, creating a user-defined network, and connecting two containers together — all by hand.

### Step 1 — Start the MongoDB container

```bash
docker network create myapp-net
docker run --name mongo --network myapp-net -d mongo
```

The `docker network create` command creates a private bridge network called `myapp-net`.  Any containers attached to this network can reach each other by **container name** as a hostname — no need to hard-code IP addresses or use the deprecated `--link` flag.

Verify the container is running:

```bash
docker ps
```

```
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS         PORTS       NAMES
a3f9c21e7b12   mongo   "docker-entrypoint.s…"   3 seconds ago   Up 2 seconds   27017/tcp   mongo
```

### Step 2 — Build the web service image

From the root of this repository, build the image from the `myapp` directory:

```bash
docker build -t webservice ./myapp
```

This uses the `Dockerfile` in `myapp/` to create a local image tagged `webservice`.

### Step 3 — Run the web service container

```bash
docker run --name webservice \
  --network myapp-net \
  -p 8000:8000 \
  -v "$(pwd)/myapp:/usr/src/app" \
  -e MONGO_HOST=mongo \
  -d webservice
```

Breaking this down:

| Flag | Purpose |
|---|---|
| `--network myapp-net` | Attach to the same network as mongo so the two containers can communicate |
| `-p 8000:8000` | Publish container port 8000 to your host |
| `-v $(pwd)/myapp:/usr/src/app` | Mount local source code into the container for live editing |
| `-e MONGO_HOST=mongo` | Tell the app where to find MongoDB — `mongo` resolves to the mongo container on the shared network |

### Step 4 — Try the app

- Visit **<http://localhost:8000/>** to add a random color to the database on each page load.
- Visit **<http://localhost:8000/hello>** (or click the link on the home page) to see all stored colors rendered as colored blocks.

---

## Inspecting the Running MongoDB Container

One of the most useful Docker skills is being able to look inside a running container.  Here's how to find where mongo is living on the network and then connect to its shell — **without installing mongo tools on your host machine**.

### Inspect the container's network settings

```bash
docker inspect mongo
```

Scroll down to the `NetworkSettings` section.  You are looking for the container's IP address on your `myapp-net` network:

```json
"Networks": {
    "myapp-net": {
        "Gateway": "172.18.0.1",
        "IPAddress": "172.18.0.2",
        ...
    }
}
```

You can also extract just the IP with a format string:

```bash
docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo
```

### Open a mongo shell on the running container

The modern mongo image ships with `mongosh` (the MongoDB Shell).  The cleanest way to open it is with `docker exec`, which runs a command inside an *already-running* container:

```bash
docker exec -it mongo mongosh
```

You're now inside the mongo shell.  Explore the data the web app is writing:

```
> use slsdb
switched to db slsdb

> show collections
colors

> db.colors.find()
[
  { _id: ObjectId('...'), color: '#7DE6B6' },
  { _id: ObjectId('...'), color: '#1C3160' },
  ...
]
```

Type `exit` to leave the shell.

### Teardown

When you're done with Part 1, stop and remove everything before moving on to Part 2:

```bash
docker stop webservice mongo
docker rm webservice mongo
docker network rm myapp-net
```

---

## Part 2: Docker Compose

You just did everything manually to understand what's happening under the hood.  Now let's see how **Docker Compose** collapses all of those commands into a single declarative file.

Open `docker-compose.yml` in the project root:

```yaml
services:
  mongo:
    image: mongo
    volumes:
      - mongo-data:/data/db

  webservice:
    build: ./myapp
    ports:
      - "8000:8000"
    environment:
      - MONGO_HOST=mongo
    volumes:
      - ./myapp:/usr/src/app
    depends_on:
      - mongo

volumes:
  mongo-data:
```

Notice how this maps directly to what we did by hand:

| Manual command | Compose equivalent |
|---|---|
| `docker network create myapp-net` | Compose creates a default network automatically |
| `docker run ... mongo` | The `mongo` service definition |
| `docker build -t webservice ./myapp` | `build: ./myapp` under the `webservice` service |
| `docker run ... -e MONGO_HOST=mongo ...` | `environment: - MONGO_HOST=mongo` |
| `docker run ... -p 8000:8000 ...` | `ports: - "8000:8000"` |
| `docker run ... -v $(pwd)/myapp:/usr/src/app ...` | `volumes: - ./myapp:/usr/src/app` |

The `depends_on` key tells Compose to start `mongo` before `webservice`.  The named volume `mongo-data` persists database data across container restarts.

### Start everything with one command

From the project root:

```bash
docker compose up
```

Add `-d` to run in detached (background) mode:

```bash
docker compose up -d
```

Visit **<http://localhost:8000/>** — same app, same behavior, much less typing.

### Useful Compose commands

```bash
# View running services
docker compose ps

# Stream logs from all services
docker compose logs -f

# Open a mongo shell (just like before, but using the compose service name)
docker compose exec mongo mongosh

# Stop and remove containers (data volume is preserved)
docker compose down

# Stop and remove containers AND the data volume
docker compose down -v
```

### Rebuilding after code changes

Because the source code is volume-mounted, edits to `webservice.py` take effect immediately (the Bottle reloader picks them up).  If you change `requirements.txt` or the `Dockerfile` itself, rebuild the image first:

```bash
docker compose up --build
```

---

That's the full picture: manual container wiring to understand the fundamentals, then Compose to make it repeatable and shareable. Have fun developing with Docker!
