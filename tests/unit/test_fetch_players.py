import pytest
from unittest.mock import patch, MagicMock
from services.fetch_players import FetchPlayers
import json


@pytest.mark.asyncio
@patch("services.fetch_players.redis_init")
async def test_handle_room(mock_redis):
    mock_redis.execute_command.return_value = '{"members": ["player1", "player2"]}'
    mock_room_data = MagicMock()
    fetch_players_instance = FetchPlayers(mock_room_data)
    fetch_players_instance.room_data.room_id = "123"

    response = await fetch_players_instance.handle_room()

    result = json.loads(response.body)

    assert result["status"] == "Success"
    assert result["response"]["members"] == ["player1", "player2"]
    assert result["message"] == "Players fetched successfully"


@pytest.mark.asyncio
@patch("services.fetch_players.redis_init")
async def test_handle_room_no_players(mock_redis):
    mock_room_data = MagicMock()
    mock_room_data.room_id = "123"
    mock_redis.execute_command.return_value = None
    fetch_players_instance = FetchPlayers(mock_room_data)

    fetch_players_instance.room_id = "wrong_room_id"

    result = await fetch_players_instance.handle_room()
    result = json.loads(result.body)

    assert result["response"] == "Failed to fetch players. Check the room id provided."
    assert result["status"] == "Failed"
