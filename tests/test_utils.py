"""Tests for handler utility functions."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat

from handlers.utils import create_more_button_keyboard, send_random_article
from services.wikipedia import WikipediaService


class TestHandlerUtils:
    """Test cases for handler utility functions."""
    
    @pytest.fixture
    def wikipedia_service(self):
        """Create mock Wikipedia service."""
        return WikipediaService()
    
    @pytest.fixture
    def mock_message(self):
        """Create mock message object."""
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.chat = MagicMock(spec=Chat)
        message.chat.id = 12345
        message.answer = AsyncMock()
        return message
    
    def test_create_more_button_keyboard_ru(self):
        """Test creating More button keyboard with Russian localization."""
        keyboard = create_more_button_keyboard("ru")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        button = keyboard.inline_keyboard[0][0]
        assert "Ещё" in button.text
        assert button.callback_data == "get_more_article"
    
    def test_create_more_button_keyboard_en(self):
        """Test creating More button keyboard with English localization."""
        keyboard = create_more_button_keyboard("en")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        button = keyboard.inline_keyboard[0][0]
        assert "More" in button.text
        assert button.callback_data == "get_more_article"
    
    @pytest.mark.asyncio
    async def test_send_random_article_success(self, mock_message, wikipedia_service):
        """Test sending random article successfully."""
        # Create mock article
        mock_article = MagicMock()
        mock_article.title = "Test Article"
        mock_article.extract = "This is a test article."
        mock_article.url = "https://en.wikipedia.org/wiki/Test"
        
        with patch.object(wikipedia_service, 'get_random_article', return_value=mock_article):
            await send_random_article(mock_message, "en", wikipedia_service, 12345)
            
            # Check that message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Test Article" in call_args
            assert "https://en.wikipedia.org/wiki/Test" in call_args
            
            # Check that keyboard is present
            keyboard = mock_message.answer.call_args[1].get("reply_markup")
            assert keyboard is not None
    
    @pytest.mark.asyncio
    async def test_send_random_article_error(self, mock_message, wikipedia_service):
        """Test sending random article when API returns None."""
        with patch.object(wikipedia_service, 'get_random_article', return_value=None):
            await send_random_article(mock_message, "en", wikipedia_service, 12345)
            
            # Check that error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "Failed to fetch article" in call_args
    
    @pytest.mark.asyncio
    async def test_send_random_article_exception(self, mock_message, wikipedia_service):
        """Test sending random article when exception occurs."""
        with patch.object(wikipedia_service, 'get_random_article', side_effect=Exception("Test error")):
            await send_random_article(mock_message, "en", wikipedia_service, 12345)
            
            # Check that error message was sent
            mock_message.answer.assert_called_once()
            call_args = mock_message.answer.call_args[0][0]
            assert "error occurred" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_send_random_article_localization(self, mock_message, wikipedia_service):
        """Test that send_random_article uses correct localization."""
        # Create mock article
        mock_article = MagicMock()
        mock_article.title = "Тестовая статья"
        mock_article.extract = "Это тестовая статья."
        mock_article.url = "https://ru.wikipedia.org/wiki/Test"
        
        with patch.object(wikipedia_service, 'get_random_article', return_value=mock_article):
            await send_random_article(mock_message, "ru", wikipedia_service, 12345)
            
            # Check that Russian localization is used
            keyboard = mock_message.answer.call_args[1].get("reply_markup")
            button_text = keyboard.inline_keyboard[0][0].text
            assert "Ещё" in button_text
