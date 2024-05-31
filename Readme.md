# Pictionary Game

This project is a Pictionary game implemented with Python and Docker. It's designed for anyone who wants to play Pictionary online with their friends.

## Installation

1. Install Docker from [here](https://www.docker.com/products/docker-desktop/)
2. Install Python from [here](https://www.python.org/downloads/)

## Running the App

1. Clone the repository and navigate to the project directory.
2. If not running in a container, create a Python virtual environment using the following command: `python3 -m pipenv shell`
3. Run the app using Docker Compose: `docker-compose up` or use command `make up`
4. To shut down the app and remove all images, use: `docker-compose down --rmi all` or use command `make down`
5. OR just do `make all`

## API Endpoints

- Health check: `/v1/health`
- Room operations:
  - Create Room: `/v1/create-room`
  - Join Room: `/v1/join-room`
  - Fetch Room: `/v1/fetch-rooms`

## Socket Events

- Start game: `start_game`
- End game: `end_game`
- Start turn: `start_turn`
- End turn: `end_turn`
- Start round: `start_round`
- End round: `end_round`
