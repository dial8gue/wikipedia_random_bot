"""Wikipedia API service for fetching random articles."""

import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class WikipediaArticle:
    """Data class for Wikipedia article information."""
    title: str
    extract: str
    url: str


class WikipediaService:
    """Service for interacting with Wikipedia API."""
    
    BASE_URL = "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"
    TIMEOUT_SECONDS = 10
    USER_AGENT = "WikipediaTelegramBot/1.0 (https://github.com/yourproject; contact@example.com)"
    MAX_RETRIES = 2
    
    def __init__(self):
        """Initialize the service with a persistent session."""
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT_SECONDS)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": self.USER_AGENT}
            )
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_random_article(self, language: str) -> Optional[WikipediaArticle]:
        """
        Fetch a random Wikipedia article with preview for the specified language.
        
        Args:
            language: Two-letter language code (e.g., 'en', 'ru', 'de')
            
        Returns:
            WikipediaArticle object with title, extract, and URL, or None if an error occurred
        """
        url = self.BASE_URL.format(language=language)
        
        # Retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                session = await self._get_session()
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract article information
                        title = data.get("title", "")
                        extract = data.get("extract", "")
                        article_url = data.get("content_urls", {}).get("desktop", {}).get("page")
                        
                        if article_url and title:
                            article = WikipediaArticle(
                                title=title,
                                extract=extract,
                                url=article_url
                            )
                            logger.info(f"Successfully fetched random article for language '{language}': {title}")
                            return article
                        else:
                            logger.error(f"Article data incomplete in response for language '{language}'")
                            return None
                    else:
                        logger.error(f"Wikipedia API returned status {response.status} for language '{language}'")
                        if attempt < self.MAX_RETRIES - 1:
                            await asyncio.sleep(0.5)
                            continue
                        return None
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout while fetching article for language '{language}' (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(0.5)
                    continue
                logger.error(f"All retry attempts exhausted for language '{language}'")
                return None
            except aiohttp.ClientError as e:
                logger.warning(f"HTTP error while fetching article for language '{language}' (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(0.5)
                    continue
                return None
            except Exception as e:
                logger.error(f"Unexpected error while fetching article for language '{language}': {e}")
                return None
        
        return None
