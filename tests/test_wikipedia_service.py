"""Tests for Wikipedia service."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import ClientError
from services.wikipedia import WikipediaService


class TestWikipediaService:
    """Test cases for WikipediaService class."""
    
    @pytest.fixture
    def service(self):
        """Create WikipediaService instance for testing."""
        return WikipediaService()
    
    @pytest.mark.asyncio
    async def test_get_random_article_success(self, service):
        """Test successful retrieval of random article."""
        mock_response_data = {
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Test_Article"
                }
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("en")
            
            assert result == "https://en.wikipedia.org/wiki/Test_Article"
    
    @pytest.mark.asyncio
    async def test_get_random_article_http_error(self, service):
        """Test handling of HTTP error responses."""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("en")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_random_article_missing_url_in_response(self, service):
        """Test handling of response without article URL."""
        mock_response_data = {
            "content_urls": {}
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("en")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_random_article_timeout(self, service):
        """Test handling of timeout errors."""
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError())
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("en")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_random_article_client_error(self, service):
        """Test handling of aiohttp ClientError."""
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session.get = MagicMock(side_effect=ClientError())
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("en")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_random_article_different_languages(self, service):
        """Test that correct URL is constructed for different languages."""
        mock_response_data = {
            "content_urls": {
                "desktop": {
                    "page": "https://ru.wikipedia.org/wiki/Test"
                }
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_get = MagicMock(return_value=mock_response)
        mock_session.get = mock_get
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await service.get_random_article("ru")
            
            # Verify the correct URL was called
            called_url = mock_get.call_args[0][0]
            assert "ru.wikipedia.org" in called_url
            assert result == "https://ru.wikipedia.org/wiki/Test"
