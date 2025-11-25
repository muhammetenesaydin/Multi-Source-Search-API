"""
Semantic Scholar connector for searching academic papers.
"""
import os
import aiohttp
import logging
from typing import List, Optional
from models import Paper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticScholarConnector:
    """Connector for Semantic Scholar API to search academic papers."""
    
    def __init__(self):
        """Initialize Semantic Scholar connector with API key from environment."""
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
        else:
            logger.warning("SEMANTIC_SCHOLAR_KEY not set. Using free tier with rate limits.")
    
    async def search_papers(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on Semantic Scholar.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "paperId,title,authors,abstract,year,url,externalIds"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_semantic_scholar_response(data)
                    elif response.status == 429:
                        logger.warning("Rate limit exceeded for Semantic Scholar API")
                        return []
                    else:
                        logger.error(f"Semantic Scholar API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar papers: {str(e)}")
            return []
    
    def _parse_semantic_scholar_response(self, data: dict) -> List[Paper]:
        """
        Parse Semantic Scholar API response.
        
        Args:
            data: JSON response from Semantic Scholar API
            
        Returns:
            List of Paper objects
        """
        papers = []
        try:
            for item in data.get("data", []):
                # Extract authors
                authors = []
                for author in item.get("authors", []):
                    authors.append(author.get("name", ""))
                
                # Extract paper ID
                paper_id = item.get("paperId", "")
                
                # Extract title
                title = item.get("title", "")
                
                # Extract abstract
                abstract = item.get("abstract", "")
                
                # Extract publication year
                year = item.get("year", "")
                published = str(year) if year else ""
                
                # Extract URL
                url = item.get("url", "")
                if not url and item.get("externalIds", {}).get("ArXiv"):
                    arxiv_id = item["externalIds"]["ArXiv"]
                    url = f"https://arxiv.org/abs/{arxiv_id}"
                
                paper = Paper(
                    id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    published=published,
                    url=url,
                    source="semantic_scholar"
                )
                papers.append(paper)
        except Exception as e:
            logger.error(f"Error parsing Semantic Scholar response: {str(e)}")
        
        return papers