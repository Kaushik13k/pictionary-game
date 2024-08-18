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

## Run Tests

- pytest tests/unit -s
- OR `make test`

## Get code coverage

- pytest --cov=./ tests/

## API Endpoints

- Health check: `/v1/health`
- Room operations:
  - Create Room: `/v1/create-room`
  - Join Room: `/v1/join-room`
  - Fetch Room: `/v1/fetch-rooms`
  - Fetch Players: `/v1/fetch-players`
  - Fetch Game Info: `/v1/fetch-game-info`
- Connect Socket:  `ws://localhost:8000/v1/ws`

## EVENT CALLS
`{"event": "start_game", "message":{"room_id":"STRING"}}` 
`{"event": "drawing_canvas", "message":{"sid":"STRING", "full_canvas_data":"STRING"}}`
`{"event":"selected_word", "message": {"sid":"STRING", "word_id":INT, "room_id": "STRING"}}`
`{"event": "chat_room", "message":{"sid":"STRING", "room_id":"STRING", "word":"STRING", "time_elapsed": INT}`

