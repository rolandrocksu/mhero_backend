.DEFAULT_GOAL := build

run-docker-compose-command:
	docker compose ${command}
dc: run-docker-compose-command

build-image: command=build mhero-backend
build-image: dc

manage-python:
	docker compose run --rm mhero-backend python manage.py $(command)

shell: command=shell
shell: manage-python

migrations: command=makemigrations
migrations: manage-python

migrate: command=migrate
migrate: manage-python

run: command=up mhero-backend
run: dc

bash: command=run --rm mhero-backend sh
bash: dc

build:
	make build-image
	make migrate

fixtures: command=loaddata fixtures/*/*.json */fixtures/*.json
fixtures: manage-python

lint:
	docker compose run --rm mhero-backend flake8

test:
	docker compose run --rm mhero-backend coverage run --source=. manage.py test -v 1
	docker compose run --rm mhero-backend coverage report
