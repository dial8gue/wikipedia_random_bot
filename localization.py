"""Localization module for bot messages."""

from typing import Dict


class Localization:
    """Handles bot message localization."""
    
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        "ru": {
            "welcome": (
                "👋 Добро пожаловать в Wikipedia Random Article Bot!\n\n"
                "Я помогу вам открывать случайные статьи из Википедии на разных языках.\n\n"
                "Доступные команды:\n"
                "/random - Получить случайную статью\n"
                "/language - Выбрать язык статей\n"
                "/help - Показать справку\n\n"
                "Доступные языки: {languages}"
            ),
            "help": (
                "📚 Справка по командам:\n\n"
                "/start - Приветственное сообщение\n"
                "/random - Получить случайную статью из Википедии\n"
                "/language - Выбрать язык для статей\n"
                "/help - Показать эту справку\n\n"
                "Выберите язык с помощью /language, затем используйте /random для получения случайных статей!"
            ),
            "language_selection": "🌍 Выберите язык для статей:\n\nТекущий язык: {current}",
            "language_changed": "✅ Язык изменен на: {lang}",
            "read_more": "Читать полностью",
            "more_button": "🎲 Ещё",
            "error_fetch": (
                "❌ Не удалось получить статью, попробуйте позже.\n\n"
                "Возможные причины:\n"
                "- Проблемы с подключением к Wikipedia\n"
                "- Выбранный язык временно недоступен"
            ),
            "error_general": "❌ Произошла ошибка. Попробуйте позже."
        },
        "en": {
            "welcome": (
                "👋 Welcome to Wikipedia Random Article Bot!\n\n"
                "I will help you discover random Wikipedia articles in different languages.\n\n"
                "Available commands:\n"
                "/random - Get a random article\n"
                "/language - Select article language\n"
                "/help - Show help\n\n"
                "Available languages: {languages}"
            ),
            "help": (
                "📚 Command reference:\n\n"
                "/start - Welcome message\n"
                "/random - Get a random Wikipedia article\n"
                "/language - Select article language\n"
                "/help - Show this help\n\n"
                "Choose a language using /language, then use /random to get random articles!"
            ),
            "language_selection": "🌍 Select article language:\n\nCurrent language: {current}",
            "language_changed": "✅ Language changed to: {lang}",
            "read_more": "Read full article",
            "more_button": "🎲 More",
            "error_fetch": (
                "❌ Failed to fetch article, please try again later.\n\n"
                "Possible reasons:\n"
                "- Connection issues with Wikipedia\n"
                "- Selected language temporarily unavailable"
            ),
            "error_general": "❌ An error occurred. Please try again later."
        }
    }
    
    @classmethod
    def get(cls, key: str, language: str = "en", **kwargs) -> str:
        """
        Get localized message.
        
        Args:
            key: Message key
            language: Language code (e.g., 'ru', 'en')
            **kwargs: Format parameters for the message
            
        Returns:
            Localized message string
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Default to English if language not supported
        lang = language if language in cls.TRANSLATIONS else "en"
        
        logger.info(f"Localization.get: key='{key}', language='{language}', resolved_lang='{lang}'")
        
        # Get message template
        message = cls.TRANSLATIONS[lang].get(key, cls.TRANSLATIONS["en"].get(key, ""))
        
        # Format with provided parameters
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                logger.error(f"Format error in localization: {e}")
        
        return message
