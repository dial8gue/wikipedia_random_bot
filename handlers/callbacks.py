"""Callback query handlers for the Wikipedia Telegram bot."""

import logging
from html import escape
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import Config
from localization import Localization
from services.wikipedia import WikipediaService


logger = logging.getLogger(__name__)
router = Router()


def create_more_button_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Create inline keyboard with "More" button.
    
    Args:
        language: Language code for button text localization
        
    Returns:
        InlineKeyboardMarkup with "More" button
    """
    button_text = Localization.get("more_button", language)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data="get_more_article")]
    ])
    return keyboard


async def callback_language_selection(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config
) -> None:
    """
    Handle language selection from inline keyboard buttons.
    
    Saves the selected language to user state and sends confirmation.
    
    Requirements: 2.3, 2.4
    """
    # Extract language code from callback data (format: "lang_XX")
    if not callback.data or not callback.data.startswith("lang_"):
        await callback.answer("❌ Неверный формат данных")
        logger.warning(f"Invalid callback data: {callback.data}")
        return
    
    selected_language = callback.data.replace("lang_", "")
    
    # Validate that the selected language is in available languages
    if selected_language not in config.available_languages:
        await callback.answer("❌ Язык не поддерживается")
        logger.warning(
            f"User {callback.from_user.id} tried to select unsupported language: {selected_language}"
        )
        return
    
    # Save selected language to user state
    await state.update_data(language=selected_language)
    
    # Verify the state was updated
    user_data = await state.get_data()
    logger.info(f"User {callback.from_user.id} state after update: {user_data}")
    
    # Send confirmation message in the selected language
    confirmation_text = Localization.get(
        "language_changed",
        selected_language,
        lang=selected_language.upper()
    )
    
    logger.info(f"Confirmation text: {confirmation_text}")
    
    # Answer callback query to remove loading state
    await callback.answer(confirmation_text)
    
    # Edit the original message to show confirmation
    await callback.message.edit_text(confirmation_text)
    
    logger.info(
        f"User {callback.from_user.id} changed language to '{selected_language}'"
    )


async def callback_get_more_article(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
    wikipedia_service: WikipediaService
) -> None:
    """
    Handle "More" button callback - send another random article.
    
    Requirements: 6.2, 6.4
    """
    # Get user's selected language from state
    user_data = await state.get_data()
    language = user_data.get("language", config.available_languages[0])
    
    logger.info(f"User {callback.from_user.id} requested more article in language '{language}'")
    
    # Answer callback query to remove loading indicator
    await callback.answer()
    
    # Show typing indicator
    await callback.bot.send_chat_action(callback.message.chat.id, "typing")
    
    try:
        # Fetch random article from Wikipedia API
        article = await wikipedia_service.get_random_article(language)
        
        if article:
            # Get localized "Read more" text
            read_more_text = Localization.get("read_more", language)
            
            # Escape HTML special characters in title and extract
            title_escaped = escape(article.title)
            extract_escaped = escape(article.extract)
            
            # Format response with title, extract, and URL
            response_text = (
                f"🎲 <b>{title_escaped}</b>\n\n"
                f"{extract_escaped}\n\n"
                f'<a href="{article.url}">{read_more_text}</a>'
            )
            
            # Create inline keyboard with "More" button
            keyboard = create_more_button_keyboard(language)
            
            # Send new article with "More" button
            await callback.message.answer(response_text, reply_markup=keyboard, disable_web_page_preview=False)
            logger.info(f"Successfully sent more article to user {callback.from_user.id}")
        else:
            # Error occurred while fetching article
            error_text = Localization.get("error_fetch", language)
            await callback.message.answer(error_text)
            logger.warning(f"Failed to fetch more article for user {callback.from_user.id}")
            
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in callback_get_more_article for user {callback.from_user.id}: {e}")
        error_text = Localization.get("error_general", language)
        await callback.message.answer(error_text)


def setup_handlers(router: Router, config: Config, wikipedia_service: WikipediaService) -> None:
    """
    Register all callback query handlers with the router.
    
    Args:
        router: Aiogram router instance
        config: Bot configuration
        wikipedia_service: Wikipedia service instance
    """
    # Create wrapper function with injected dependencies
    async def language_selection_handler(callback: CallbackQuery, state: FSMContext):
        await callback_language_selection(callback, state, config)
    
    async def more_article_handler(callback: CallbackQuery, state: FSMContext):
        await callback_get_more_article(callback, state, config, wikipedia_service)
    
    # Register callback handler for language selection
    router.callback_query.register(
        language_selection_handler,
        lambda c: c.data and c.data.startswith("lang_")
    )
    
    # Register callback handler for "More" button
    router.callback_query.register(
        more_article_handler,
        lambda c: c.data == "get_more_article"
    )
    
    logger.info("Callback handlers registered successfully")
