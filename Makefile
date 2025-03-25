#!make
include .env
.DEFAULT_GOAL=up
MAKEFLAGS += --no-print-directory

# Constants
TAIL_LOGS = 50
PYLINT_FAIL_UNDER = 8

up:
	$s docker compose up --force-recreate -d

down:
	$s docker compose down

down-up: down up

up-build: down build up

build:
	$s docker compose build

complete-build: build down-up

logs:
	$s docker logs --tail ${TAIL_LOGS} -f ${PROJECT_NAME}_data_events

bash:
	$s docker exec -it ${PROJECT_NAME}_data_events bash

sh:
	$s docker exec -it ${PROJECT_NAME}_data_events bash

shell:
	$s docker exec -it ${PROJECT_NAME}_data_events ipython


ruff:
	$s docker exec ${PROJECT_NAME}_data_events ruff check .

pylint:
	$s docker exec ${PROJECT_NAME}_data_events pylint --fail-under=${PYLINT_FAIL_UNDER} ./

linters: ruff pylint

black:
	$s docker exec ${PROJECT_NAME}_data_events black .

isort:
	$s docker exec ${PROJECT_NAME}_data_events isort .

code-style: isort black

test:
	$s docker exec ${PROJECT_NAME}_data_events python -m unittest discover test

wait-up:
	$s sleep 60
