"""
Main module for Wikipedia Telegram Bot.

This module initializes the bot, registers handlers, and starts polling.
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config
from services.wikipedia import WikipediaService
from handlers.commands import setup_handlers as setup_command_handlers
from handlers.callbacks import setup_handlers as setup_callback_handlers
from states import storage


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main function to initialize and run the bot.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 5.4
    """
    logger.info("Starting Wikipedia Telegram Bot...")
    
    # Load configuration from environment variables
    try:
        config = Config.from_env()
        logger.info("Configuration loaded successfully")
    except SystemExit:
        logger.critical("Failed to load configuration. Exiting.")
        return
    
    # Initialize Bot with default properties
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize Dispatcher with memory storage for FSM
    dp = Dispatcher(storage=storage)
    
    # Initialize Wikipedia service
    wikipedia_service = WikipediaService()
    
    # Register all handlers
    logger.info("Registering handlers...")
    setup_command_handlers(dp, config, wikipedia_service)
    setup_callback_handlers(dp, config)
    logger.info("All handlers registered successfully")
    
    # Start polling with graceful shutdown
    try:
        logger.info("Bot started. Polling for updates...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        # Graceful shutdown
        logger.info("Shutting down bot...")
        await bot.session.close()
        await storage.close()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)
