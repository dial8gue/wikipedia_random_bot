"""Handlers package for the Wikipedia Telegram bot."""

from handlers.commands import setup_handlers as setup_command_handlers
from handlers.callbacks import setup_handlers as setup_callback_handlers

__all__ = [
    "setup_command_handlers",
    "setup_callback_handlers",
]
