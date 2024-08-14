import logging
import asyncio
from typing import Dict
from fastapi import HTTPException

from services.end_turn import end_turn
from services.connection_manager import ConnectionManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimerStrategy:
    """Strategy pattern for different timer behaviors."""

    async def run(self, game_id: int, duration: int, manager: ConnectionManager):
        """Run the timer for the given duration."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class SimpleTimerStrategy(TimerStrategy):
    """Simple strategy that just counts down."""

    async def run(self, game_id: int, duration: int, manager: ConnectionManager):
        for second in range(1, duration + 1):
            if TimerManager.instance().is_stopped(game_id):
                logger.info(f"Timer for Game {game_id} stopped at {second} seconds.")
                return
            await asyncio.sleep(1)
        logger.info(f"Timer for Game {game_id} completed.")
        await manager.broadcast(
            {"event": "time_up", "value": f"Time's up."},
        )
        try:
            TimerManager.instance().stop_timer(game_id)
            await end_turn(game_id, manager, is_time_up=True)
        except Exception as e:
            logger.error(e)


class TimerManager:
    """Singleton class to manage all timers."""

    _instance = None

    def __init__(self):
        if TimerManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.timers: Dict[int, asyncio.Task] = {}
        self.stop_signals: Dict[int, bool] = {}
        TimerManager._instance = self

    @staticmethod
    def instance():
        if TimerManager._instance is None:
            TimerManager()
        return TimerManager._instance

    @staticmethod
    def create_timer(
        strategy: TimerStrategy, game_id: int, duration: int, manager: ConnectionManager
    ):
        return asyncio.create_task(strategy.run(game_id, duration, manager))

    def start_timer(self, game_id: int, duration: int, manager: ConnectionManager):
        if game_id in self.timers:
            raise HTTPException(
                status_code=400, detail=f"Timer for Game {game_id} is already running"
            )

        strategy = SimpleTimerStrategy()
        self.timers[game_id] = self.create_timer(strategy, game_id, duration, manager)
        self.stop_signals[game_id] = False

    def stop_timer(self, game_id: int):
        if game_id not in self.timers:
            raise HTTPException(
                status_code=400, detail=f"No active timer to stop for Game {game_id}"
            )

        self.stop_signals[game_id] = True
        asyncio.create_task(self.wait_for_timer(game_id))

    def is_stopped(self, game_id: int) -> bool:
        return self.stop_signals.get(game_id, False)

    async def wait_for_timer(self, game_id: int):
        await self.timers[game_id]
        del self.timers[game_id]
        del self.stop_signals[game_id]