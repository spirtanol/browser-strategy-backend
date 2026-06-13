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
