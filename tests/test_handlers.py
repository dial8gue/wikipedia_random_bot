"""Tests for bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import Config
from services.wikipedia import WikipediaService
from handlers.commands import cmd_start, cmd_help, cmd_random, cmd_language
from handlers.callbacks import callback_language_selection, callback_get_more_article
from handlers.utils import create_more_button_keyboard


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
    async def test_cmd_start(self, mock_message, mock_state, config):
        """Test /start command sends welcome message."""
        mock_state.get_data = AsyncMock(return_value={"language": "ru"})
        
        await cmd_start(mock_message, config, mock_state)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Добро пожаловать" in call_args
        assert "/random" in call_args
        assert "/language" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_help(self, mock_message, mock_state, config):
        """Test /help command sends help text."""
        mock_state.get_data = AsyncMock(return_value={"language": "ru"})
        
        await cmd_help(mock_message, mock_state, config)
        
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
        
        # Create mock article object
        mock_article = MagicMock()
        mock_article.title = "Test Article"
        mock_article.extract = "This is a test article."
        mock_article.url = "https://en.wikipedia.org/wiki/Test"
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value=mock_article):
            await cmd_random(mock_message, mock_state, config, wikipedia_service)
            
            assert mock_message.answer.call_count == 1
            call_args = mock_message.answer.call_args[0][0]
            assert "Test Article" in call_args
            assert "https://en.wikipedia.org/wiki/Test" in call_args
            
            # Check that inline keyboard with "More" button is present
            keyboard = mock_message.answer.call_args[1].get("reply_markup")
            assert keyboard is not None
            assert len(keyboard.inline_keyboard) == 1
            assert len(keyboard.inline_keyboard[0]) == 1
            assert keyboard.inline_keyboard[0][0].callback_data == "get_more_article"
    
    @pytest.mark.asyncio
    async def test_cmd_random_uses_default_language(self, mock_message, mock_state, config, wikipedia_service):
        """Test /random command uses default language when not set."""
        mock_state.get_data = AsyncMock(return_value={})
        
        # Create mock article object
        mock_article = MagicMock()
        mock_article.title = "Test Article"
        mock_article.extract = "This is a test article."
        mock_article.url = "https://en.wikipedia.org/wiki/Test"
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value=mock_article) as mock_get:
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
            assert "Failed to fetch article" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_language(self, mock_message, mock_state, config):
        """Test /language command displays language options."""
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        await cmd_language(mock_message, config, mock_state)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        text = call_args[0][0]
        keyboard = call_args[1]["reply_markup"]
        
        assert "Select article language" in text
        assert keyboard is not None
    
    @pytest.mark.asyncio
    async def test_more_button_localization_ru(self):
        """Test More button text is localized correctly for Russian."""
        keyboard = create_more_button_keyboard("ru")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        button = keyboard.inline_keyboard[0][0]
        assert "Ещё" in button.text
        assert button.callback_data == "get_more_article"
    
    @pytest.mark.asyncio
    async def test_more_button_localization_en(self):
        """Test More button text is localized correctly for English."""
        keyboard = create_more_button_keyboard("en")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        button = keyboard.inline_keyboard[0][0]
        assert "More" in button.text
        assert button.callback_data == "get_more_article"


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
    
    @pytest.mark.asyncio
    async def test_callback_get_more_article_success(self, config):
        """Test More button callback sends new article."""
        # Create mock callback
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = MagicMock(spec=User)
        mock_callback.from_user.id = 12345
        mock_callback.data = "get_more_article"
        mock_callback.answer = AsyncMock()
        mock_callback.message = MagicMock()
        mock_callback.message.chat = MagicMock()
        mock_callback.message.chat.id = 12345
        mock_callback.message.answer = AsyncMock()
        mock_callback.bot = MagicMock()
        mock_callback.bot.send_chat_action = AsyncMock()
        
        # Create mock state
        mock_state = MagicMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        # Create mock Wikipedia service
        wikipedia_service = WikipediaService()
        mock_article = MagicMock()
        mock_article.title = "Another Test Article"
        mock_article.extract = "This is another test article."
        mock_article.url = "https://en.wikipedia.org/wiki/Another_Test"
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value=mock_article):
            await callback_get_more_article(mock_callback, mock_state, config, wikipedia_service)
            
            # Check callback was answered
            mock_callback.answer.assert_called_once()
            
            # Check new article was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Another Test Article" in call_args
            assert "https://en.wikipedia.org/wiki/Another_Test" in call_args
            
            # Check that inline keyboard with "More" button is present
            keyboard = mock_callback.message.answer.call_args[1].get("reply_markup")
            assert keyboard is not None
            assert len(keyboard.inline_keyboard) == 1
            assert keyboard.inline_keyboard[0][0].callback_data == "get_more_article"
    
    @pytest.mark.asyncio
    async def test_callback_get_more_article_uses_user_language(self, config):
        """Test More button callback uses user's selected language."""
        # Create mock callback
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = MagicMock(spec=User)
        mock_callback.from_user.id = 12345
        mock_callback.data = "get_more_article"
        mock_callback.answer = AsyncMock()
        mock_callback.message = MagicMock()
        mock_callback.message.chat = MagicMock()
        mock_callback.message.chat.id = 12345
        mock_callback.message.answer = AsyncMock()
        mock_callback.bot = MagicMock()
        mock_callback.bot.send_chat_action = AsyncMock()
        
        # Create mock state with Russian language
        mock_state = MagicMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"language": "ru"})
        
        # Create mock Wikipedia service
        wikipedia_service = WikipediaService()
        mock_article = MagicMock()
        mock_article.title = "Тестовая статья"
        mock_article.extract = "Это тестовая статья."
        mock_article.url = "https://ru.wikipedia.org/wiki/Test"
        
        with patch.object(wikipedia_service, 'get_random_article', 
                         return_value=mock_article) as mock_get:
            await callback_get_more_article(mock_callback, mock_state, config, wikipedia_service)
            
            # Check that Russian language was used
            mock_get.assert_called_once_with("ru")
            
            # Check that button text is in Russian
            keyboard = mock_callback.message.answer.call_args[1].get("reply_markup")
            button_text = keyboard.inline_keyboard[0][0].text
            assert "Ещё" in button_text
    
    @pytest.mark.asyncio
    async def test_callback_get_more_article_error(self, config):
        """Test More button callback handles API errors."""
        # Create mock callback
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.from_user = MagicMock(spec=User)
        mock_callback.from_user.id = 12345
        mock_callback.data = "get_more_article"
        mock_callback.answer = AsyncMock()
        mock_callback.message = MagicMock()
        mock_callback.message.chat = MagicMock()
        mock_callback.message.chat.id = 12345
        mock_callback.message.answer = AsyncMock()
        mock_callback.bot = MagicMock()
        mock_callback.bot.send_chat_action = AsyncMock()
        
        # Create mock state
        mock_state = MagicMock(spec=FSMContext)
        mock_state.get_data = AsyncMock(return_value={"language": "en"})
        
        # Create mock Wikipedia service that returns None (error)
        wikipedia_service = WikipediaService()
        
        with patch.object(wikipedia_service, 'get_random_article', return_value=None):
            await callback_get_more_article(mock_callback, mock_state, config, wikipedia_service)
            
            # Check callback was answered
            mock_callback.answer.assert_called_once()
            
            # Check error message was sent
            mock_callback.message.answer.assert_called_once()
            call_args = mock_callback.message.answer.call_args[0][0]
            assert "Failed to fetch article" in call_args or "Не удалось получить статью" in call_args
