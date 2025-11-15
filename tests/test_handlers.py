"""Tests for bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import Config
from services.wikipedia import WikipediaService
from handlers.commands import cmd_start, cmd_help, cmd_random, cmd_language
from handlers.callbacks import callback_language_selection


class TestCommandHandlers:
    """Test cases for command handlers."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            bot_token="test_token",
            available_languages=["en", "ru", "de"]
        )
    
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
        message.bot = MagicMock()
        message.bot.send_chat_action = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_state(self):
        """Create mock FSM context."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={})
        state.update_data = AsyncMock()
        return state
    
    @pytest.mark.asyncio
    async def test_cmd_start(self, mock_message, config):
        """Test /start command sends welcome message."""
        await cmd_start(mock_message, config)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Добро пожаловать" in call_args
        assert "/random" in call_args
        assert "/language" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_help(self, mock_message):
        """Test /help command sends help text."""
        await cmd_help(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Справка" in call_args
        assert "/start" in call_args
        assert "/random" in call_args
        assert "/language" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_random_success(self, mock_message, mock_state, config, wikipedia_service):
        """Test /random command with successful article fetch."""
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value="https://en.wikipedia.org/wiki/Test"):
            await cmd_random(mock_message, mock_state, config, wikipedia_service)
            
            assert mock_message.answer.call_count == 1
            call_args = mock_message.answer.call_args[0][0]
            assert "https://en.wikipedia.org/wiki/Test" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_random_uses_default_language(self, mock_message, mock_state, config, wikipedia_service):
        """Test /random command uses default language when not set."""
        mock_state.get_data = AsyncMock(return_value={})
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value="https://en.wikipedia.org/wiki/Test") as mock_get:
            await cmd_random(mock_message, mock_state, config, wikipedia_service)
            
            # Should use first available language (en)
            mock_get.assert_called_once_with("en")
    
    @pytest.mark.asyncio
    async def test_cmd_random_api_error(self, mock_message, mock_state, config, wikipedia_service):
        """Test /random command handles API errors."""
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        with patch.object(wikipedia_service, 'get_random_article', return_value=None):
            await cmd_random(mock_message, mock_state, config, wikipedia_service)
            
            assert mock_message.answer.call_count == 1
            call_args = mock_message.answer.call_args[0][0]
            assert "Не удалось получить статью" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_language(self, mock_message, mock_state, config):
        """Test /language command displays language options."""
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        await cmd_language(mock_message, config, mock_state)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        text = call_args[0][0]
        keyboard = call_args[1]["reply_markup"]
        
        assert "Выберите язык" in text
        assert keyboard is not None


class TestCallbackHandlers:
    """Test cases for callback handlers."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            bot_token="test_token",
            available_languages=["en", "ru", "de"]
        )
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback query object."""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = MagicMock(spec=User)
        callback.from_user.id = 12345
        callback.data = "lang_ru"
        callback.answer = AsyncMock()
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        return callback
    
    @pytest.fixture
    def mock_state(self):
        """Create mock FSM context."""
        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        return state
    
    @pytest.mark.asyncio
    async def test_callback_language_selection_success(self, mock_callback, mock_state, config):
        """Test successful language selection."""
        mock_callback.data = "lang_ru"
        
        await callback_language_selection(mock_callback, mock_state, config)
        
        mock_state.update_data.assert_called_once_with(language="ru")
        mock_callback.answer.assert_called_once()
        mock_callback.message.edit_text.assert_called_once()
        
        edit_text_args = mock_callback.message.edit_text.call_args[0][0]
        assert "Язык изменен" in edit_text_args
        assert "RU" in edit_text_args
    
    @pytest.mark.asyncio
    async def test_callback_language_selection_invalid_format(self, mock_callback, mock_state, config):
        """Test handling of invalid callback data format."""
        mock_callback.data = "invalid_format"
        
        await callback_language_selection(mock_callback, mock_state, config)
        
        mock_callback.answer.assert_called_once()
        answer_args = mock_callback.answer.call_args[0][0]
        assert "Неверный формат" in answer_args
        mock_state.update_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_callback_language_selection_unsupported_language(self, mock_callback, mock_state, config):
        """Test handling of unsupported language selection."""
        mock_callback.data = "lang_fr"  # fr is not in available_languages
        
        await callback_language_selection(mock_callback, mock_state, config)
        
        mock_callback.answer.assert_called_once()
        answer_args = mock_callback.answer.call_args[0][0]
        assert "не поддерживается" in answer_args
        mock_state.update_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_callback_language_selection_different_languages(self, mock_callback, mock_state, config):
        """Test language selection for different languages."""
        for lang in ["en", "ru", "de"]:
            mock_callback.data = f"lang_{lang}"
            mock_state.update_data.reset_mock()
            
            await callback_language_selection(mock_callback, mock_state, config)
            
            mock_state.update_data.assert_called_once_with(language=lang)
