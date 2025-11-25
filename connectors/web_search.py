"""
Web search connector using SERPAPI or DuckDuckGo as fallback.
"""
import os
import aiohttp
import logging
from typing import List, Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from models import Paper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchConnector:
    """Connector for web search using SERPAPI or DuckDuckGo as fallback."""
    
    def __init__(self):
        """Initialize web search connector with API key from environment."""
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
    
    async def search_articles(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for articles using SERPAPI or DuckDuckGo as fallback.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        if self.serpapi_key:
            return await self._search_with_serpapi(query, max_results)
        else:
            logger.info("SERPAPI_KEY not set. Using DuckDuckGo as fallback.")
            return await self._search_with_duckduckgo(query, max_results)
    
    async def _search_with_serpapi(self, query: str, max_results: int) -> List[Paper]:
        """Search using SERPAPI."""
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "num": min(max_results, 100)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_serpapi_response(data)
                    else:
                        logger.error(f"SERPAPI error: {response.status}")
                        # Fallback to DuckDuckGo
                        return await self._search_with_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"Error with SERPAPI: {str(e)}")
            # Fallback to DuckDuckGo
            return await self._search_with_duckduckgo(query, max_results)
    
    async def _search_with_duckduckgo(self, query: str, max_results: int) -> List[Paper]:
        """Search using DuckDuckGo as fallback."""
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        data = {
            "q": query,
            "kl": "us-en"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_duckduckgo_response(content, max_results)
                    else:
                        logger.error(f"DuckDuckGo search error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching with DuckDuckGo: {str(e)}")
            return []
    
    def _parse_serpapi_response(self, data: dict) -> List[Paper]:
        """Parse SERPAPI response."""
        papers = []
        try:
            for result in data.get("organic_results", []):
                title = result.get("title", "")
                url = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Only include results that look like academic papers or technical articles
                if "paper" in title.lower() or "research" in title.lower() or "study" in title.lower():
                    paper = Paper(
                        id=url,
                        title=title,
                        authors=[],  # SERPAPI doesn't provide authors in organic results
                        abstract=snippet,
                        published="",  # Not available in this format
                        url=url,
                        source="web"
                    )
                    papers.append(paper)
        except Exception as e:
            logger.error(f"Error parsing SERPAPI response: {str(e)}")
        
        return papers
    
    def _parse_duckduckgo_response(self, html_content: str, max_results: int) -> List[Paper]:
        """Parse DuckDuckGo HTML response."""
        papers = []
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            results = soup.find_all('div', class_='result')
            
            for result in results[:max_results]:
                title_elem = result.find('a', class_='result__a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                snippet_elem = result.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # Only include results that look like academic papers or technical articles
                if "paper" in title.lower() or "research" in title.lower() or "study" in title.lower() or "article" in title.lower():
                    paper = Paper(
                        id=url,
                        title=title,
                        authors=[],  # Not available in DuckDuckGo results
                        abstract=snippet,
                        published="",  # Not available in this format
                        url=url,
                        source="web"
                    )
                    papers.append(paper)
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo response: {str(e)}")
        
        return papers