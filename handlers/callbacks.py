"""Callback query handlers for the Wikipedia Telegram bot."""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import Config


logger = logging.getLogger(__name__)
router = Router()


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
    
    # Send confirmation message
    confirmation_text = (
        f"✅ Язык изменен на {selected_language.upper()}\n\n"
        f"Теперь используйте /random для получения случайных статей на этом языке."
    )
    
    # Answer callback query to remove loading state
    await callback.answer(f"Выбран язык: {selected_language.upper()}")
    
    # Edit the original message to show confirmation
    await callback.message.edit_text(confirmation_text)
    
    logger.info(
        f"User {callback.from_user.id} changed language to '{selected_language}'"
    )


def setup_handlers(router: Router, config: Config) -> None:
    """
    Register all callback query handlers with the router.
    
    Args:
        router: Aiogram router instance
        config: Bot configuration
    """
    # Create wrapper function with injected dependencies
    async def language_selection_handler(callback: CallbackQuery, state: FSMContext):
        await callback_language_selection(callback, state, config)
    
    # Register callback handler for language selection
    router.callback_query.register(
        language_selection_handler,
        lambda c: c.data and c.data.startswith("lang_")
    )
    
    logger.info("Callback handlers registered successfully")
