.PHONY: up down all test

up:
	docker-compose up

down:
	docker-compose down --rmi all

all: down up

test:
	docker build -t pictionary-app-test -f dockerfile.test .
	docker run pictionary-app-test