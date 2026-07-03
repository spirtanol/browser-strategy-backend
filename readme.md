# Real-Time Browser Strategy Game Server (Core & Web Backend)

This is a technical proof-of-concept (PoC) focused on building a asynchronous backend architecture. The main goal is to demonstrate scalable real-time state synchronization using Python and Redis, rather than delivering a complete frontend game.

Built with **Python**, **FastAPI**, **Redis (Pub/Sub + Cache)**, and **WebSockets**.

## Architectural Overview

The project uses a **decoupled architecture** where a single codebase can be launched in two distinct modes depending on environment variables:

1. **Web Mode (API & WebSockets):** Handles user HTTP requests (auth, registration), manages persistent WebSocket connections, validates incoming player commands, and forwards them to the Core.
2. **Core Mode (Game Loop / Ticks):** Runs the main game loop, processes entity states, executes queued actions, and broadcasts world updates.

## Core Features & Mechanics

* **Stateful Real-Time Synchronization:** Active objects (e.g., ships, platforms) are "awakened" by the Core when requested by players. The Core streams their real-time state changes via Redis Pub/Sub back to the Web instance, which broadcasts them to connected clients.
* **Persistent Offline World:** Entity coordinates are calculated based on delta-time increments, allowing ships movements and long-term actions to process seamlessly even when players are offline.
* **Centralized State & Security:** 
  * Handshake and session safety are enforced via custom JWT blacklisting using Redis TTL.
  * Structural commands are thoroughly validated by the Web layer before being pushed to the Core's execution queue.

## Tech Stack

* **Language:** Python 3.13+ (Asyncio)
* **Framework:** FastAPI
* **Real-time Networking:** WebSockets
* **Message Broker & Cache:** Redis (Pub/Sub, Key-Value)
* **Database / ORM:** MariaDB / SQLAlchemy (In progress)

## Getting Started

### Prerequisites
* Docker and Docker Compose
* Make (optional, for development shortcuts)

---

### Quick Start (Production / Demo Mode)
If you just want to launch the fully automated architecture and test the real-time synchronization, use the release configuration. The core engine will automatically wait for the database, run Alembic migrations, apply seed data, and spin up both Web and Core layers.

1. **Prepare Environment Variables:**
   ```bash
   cp .env.example .env

```

2. **Launch the Stack:**
```bash
docker compose up --build

```



---

### Local Development Workflow
For active development, code refactoring, or running migrations manually, use the dedicated development environment which includes hot-reload, volume mounting, and exposed ports for database/Redis GUI clients.

A `Makefile` is provided to simplify daily routines:

* **Start Development Environment:**
  ```bash
  make up

```

* **Stop and Remove All Containers:**
```bash
make down

```


* **Stop Only Application Containers (Core & Web):**
```bash
make stop

```


* **Force Restart Application Containers (Apply Code Changes if needed):**
```bash
make restart

```


* **Apply Database Migrations:**
```bash
make migrate

```


* **Seed Database with Test Content:**
```bash
make seed

```


* **Enter Interactive Database CLI:**
```bash
make db

```


* **Enter Core Container Bash Shell:**
```bash
make shell

```

---

### API Verification & Testing

#### 1. Obtain an Access Token

To interact with the WebSockets, authenticate via the seeded player account to receive a JWT token:

```bash
curl --request POST \
  --url http://localhost:4000/api/auth/login \
  --header 'content-type: application/json' \
  --data '{
    "email": "player@test.com",
    "password": "12qwaszx"
  }'

```

#### 2. Connect to Real-Time Monitor

1. Open the local `monitor.html` file in your browser.
2. Paste the `access_token` obtained from the step above.
3. Establish a WebSocket connection to observe real-time state updates and entity movements driven by the Core loop.

