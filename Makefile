DC_DEV = docker compose -f docker-compose.dev.yml

.PHONY: up down stop restart shell migrate seed db dump restore

FILE ?= dump.sql

up:
	$(DC_DEV) up

down:
	$(DC_DEV) down

stop:
	$(DC_DEV) down core web

restart:
	$(DC_DEV) up --force-recreate core web

shell:
	$(DC_DEV) run --rm -it core bash

migrate:
	$(DC_DEV) run --rm core poetry run alembic upgrade head

seed:
	$(DC_DEV) run --rm core poetry run python -m app.seed

db:
	$(DC_DEV) exec -it db sh -c 'mysql -u"$$MYSQL_USER" -p"$$MYSQL_PASSWORD" "$$MYSQL_DATABASE"'

dump:
	$(DC_DEV) exec db sh -c 'mysqldump -u"$$MYSQL_USER" -p"$$MYSQL_PASSWORD" "$$MYSQL_DATABASE"' > $(FILE)

restore:
	$(DC_DEV) exec db sh -c 'mysqldump -u"$$MYSQL_USER" -p"$$MYSQL_PASSWORD" "$$MYSQL_DATABASE"' < $(FILE)