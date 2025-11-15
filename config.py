import os
import sys
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for loading and validating environment variables."""
    
    def __init__(self, bot_token: str, available_languages: List[str]):
        self.bot_token = bot_token
        self.available_languages = available_languages
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.
        
        Returns:
            Config: Configuration instance
            
        Raises:
            SystemExit: If BOT_TOKEN is missing or invalid
        """
        # Validate and load BOT_TOKEN (required)
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.critical("BOT_TOKEN is missing in environment variables. Cannot start bot.")
            sys.exit(1)
        
        bot_token = bot_token.strip()
        if not bot_token:
            logger.critical("BOT_TOKEN is empty. Cannot start bot.")
            sys.exit(1)
        
        # Load and parse AVAILABLE_LANGUAGES (optional, defaults to ["en"])
        languages_str = os.getenv("AVAILABLE_LANGUAGES", "en")
        available_languages = cls._parse_languages(languages_str)
        
        if not available_languages:
            logger.warning("No valid languages found in AVAILABLE_LANGUAGES. Using default: ['en']")
            available_languages = ["en"]
        
        logger.info(f"Configuration loaded successfully. Available languages: {available_languages}")
        
        return cls(bot_token=bot_token, available_languages=available_languages)
    
    @staticmethod
    def _parse_languages(languages_str: str) -> List[str]:
        """
        Parse comma-separated language codes from string.
        
        Args:
            languages_str: Comma-separated language codes (e.g., "ru,en,de")
            
        Returns:
            List of valid language codes
        """
        if not languages_str:
            return []
        
        # Split by comma and clean up whitespace
        languages = [lang.strip().lower() for lang in languages_str.split(",")]
        
        # Filter out empty strings and validate format (2-letter codes)
        valid_languages = []
        for lang in languages:
            if lang and len(lang) == 2 and lang.isalpha():
                valid_languages.append(lang)
            elif lang:
                logger.warning(f"Invalid language code '{lang}' - must be 2 letters. Skipping.")
        
        return valid_languages
