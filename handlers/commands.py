"""Command handlers for the Wikipedia Telegram bot."""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from services.wikipedia import WikipediaService
from states import UserState
from config import Config
from localization import Localization


logger = logging.getLogger(__name__)
router = Router()


async def cmd_start(message: Message, config: Config, state: FSMContext) -> None:
    """
    Handle /start command - send welcome message with instructions.
    
    Requirements: 4.1
    """
    # Get user's selected language
    user_data = await state.get_data()
    language = user_data.get("language", config.available_languages[0])
    
    logger.info(f"User {message.from_user.id} started the bot. State: {user_data}, Language: {language}")
    
    welcome_text = Localization.get(
        "welcome",
        language,
        languages=", ".join(config.available_languages)
    )
    await message.answer(welcome_text)
    logger.info(f"User {message.from_user.id} started the bot")


async def cmd_help(message: Message, state: FSMContext, config: Config) -> None:
    """
    Handle /help command - send list of available commands.
    
    Requirements: 4.2
    """
    # Get user's selected language
    user_data = await state.get_data()
    language = user_data.get("language", config.available_languages[0])
    
    help_text = Localization.get("help", language)
    await message.answer(help_text)
    logger.info(f"User {message.from_user.id} requested help")


async def cmd_random(
    message: Message,
    state: FSMContext,
    config: Config,
    wikipedia_service: WikipediaService
) -> None:
    """
    Handle /random command - send random Wikipedia article link.
    
    Requirements: 4.3, 1.1, 1.2, 1.3, 1.4
    """
    # Get user's selected language from state, or use first available language as default
    user_data = await state.get_data()
    language = user_data.get("language", config.available_languages[0])
    
    logger.info(f"User {message.from_user.id} requested random article in language '{language}'")
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Fetch random article from Wikipedia API
        article = await wikipedia_service.get_random_article(language)
        
        if article:
            # Get localized "Read more" text
            read_more_text = Localization.get("read_more", language)
            
            # Format response with title, extract, and URL
            response_text = (
                f"🎲 <b>{article.title}</b>\n\n"
                f"{article.extract}\n\n"
                f"🔗 <a href='{article.url}'>{read_more_text}</a>"
            )
            await message.answer(response_text, disable_web_page_preview=False)
            logger.info(f"Successfully sent random article to user {message.from_user.id}")
        else:
            # Error occurred while fetching article
            error_text = Localization.get("error_fetch", language)
            await message.answer(error_text)
            logger.warning(f"Failed to fetch article for user {message.from_user.id}")
            
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in cmd_random for user {message.from_user.id}: {e}")
        error_text = Localization.get("error_general", language)
        await message.answer(error_text)


async def cmd_language(message: Message, config: Config, state: FSMContext) -> None:
    """
    Handle /language command - display available languages with inline buttons.
    
    Requirements: 4.4, 2.2
    """
    # Get current language
    user_data = await state.get_data()
    current_language = user_data.get("language", config.available_languages[0])
    
    # Create inline keyboard with language options
    keyboard_buttons = []
    for lang in config.available_languages:
        # Add checkmark for currently selected language
        button_text = f"{'✅ ' if lang == current_language else ''}{lang.upper()}"
        callback_data = f"lang_{lang}"
        keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = Localization.get(
        "language_selection",
        current_language,
        current=current_language.upper()
    )
    
    await message.answer(text, reply_markup=keyboard)
    logger.info(f"User {message.from_user.id} opened language selection")


def setup_handlers(router: Router, config: Config, wikipedia_service: WikipediaService) -> None:
    """
    Register all command handlers with the router.
    
    Args:
        router: Aiogram router instance
        config: Bot configuration
        wikipedia_service: Wikipedia service instance
    """
    # Create wrapper functions with injected dependencies
    async def start_handler(message: Message, state: FSMContext):
        await cmd_start(message, config, state)
    
    async def help_handler(message: Message, state: FSMContext):
        await cmd_help(message, state, config)
    
    async def random_handler(message: Message, state: FSMContext):
        await cmd_random(message, state, config, wikipedia_service)
    
    async def language_handler(message: Message, state: FSMContext):
        await cmd_language(message, config, state)
    
    # Register handlers
    router.message.register(start_handler, Command(commands=["start"]))
    router.message.register(help_handler, Command(commands=["help"]))
    router.message.register(random_handler, Command(commands=["random"]))
    router.message.register(language_handler, Command(commands=["language"]))
    
    logger.info("Command handlers registered successfully")
