"""
FSM states for managing user state in the Wikipedia Telegram bot.
"""

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


class UserState(StatesGroup):
    """State group for storing user-specific data."""
    language = State()


# Initialize memory storage for FSM
storage = MemoryStorage()
