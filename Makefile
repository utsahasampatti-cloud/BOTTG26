.PHONY: colima up down logs ps build rebuild

# Colima must be running before docker compose.
# If "qemu-img not found": brew install qemu (Colima 0.10 + qemu VM backend)
colima:
	colima start

build:
	docker compose build

# Full image rebuild (no cache) + recreate containers — use after Dockerfile/requirements changes
rebuild:
	docker compose build --no-cache
	docker compose up -d --force-recreate

up: build
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f telegram-bot

ps:
	docker compose ps
