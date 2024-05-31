.PHONY: up down all

up:
	docker-compose up

down:
	docker-compose down --rmi all

all: down up