"""Utility functions for handlers."""

import logging
from html import escape
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from services.wikipedia import WikipediaService
from localization import Localization


logger = logging.getLogger(__name__)


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


async def send_random_article(
    message: Message,
    language: str,
    wikipedia_service: WikipediaService,
    user_id: int
) -> None:
    """
    Fetch and send a random Wikipedia article.
    
    Args:
        message: Message object to send the article to
        language: Language code for the article
        wikipedia_service: Wikipedia service instance
        user_id: User ID for logging
    """
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
                f"<b>{title_escaped}</b>\n\n"
                f"{extract_escaped}\n\n"
                f'<a href="{article.url}">{read_more_text}</a>'
            )
            
            # Create inline keyboard with "More" button
            keyboard = create_more_button_keyboard(language)
            
            await message.answer(response_text, reply_markup=keyboard, disable_web_page_preview=False)
            logger.info(f"Successfully sent random article to user {user_id}")
        else:
            # Error occurred while fetching article
            error_text = Localization.get("error_fetch", language)
            await message.answer(error_text)
            logger.warning(f"Failed to fetch article for user {user_id}")
            
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error sending article to user {user_id}: {e}")
        error_text = Localization.get("error_general", language)
        await message.answer(error_text)
