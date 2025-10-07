"""
arXiv connector for searching academic papers.
"""
import aiohttp
import logging
from typing import List
from urllib.parse import urlencode
from models import Paper
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivConnector:
    """Connector for arXiv API to search academic papers."""
    
    def __init__(self):
        """Initialize arXiv connector."""
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search_papers(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on arXiv.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        params = {
            "search_query": query,
            "start": 0,
            "max_results": min(max_results, 100),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        url = f"{self.base_url}?{urlencode(params)}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_response(content)
                    else:
                        logger.error(f"arXiv API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching arXiv papers: {str(e)}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Paper]:
        """
        Parse arXiv API XML response.
        
        Args:
            xml_content: XML response from arXiv API
            
        Returns:
            List of Paper objects
        """
        try:
            root = ET.fromstring(xml_content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
            
            papers = []
            for entry in root.findall('atom:entry', namespace):
                # Extract paper ID from the ID element
                id_element = entry.find('atom:id', namespace)
                paper_id = id_element.text.split('/abs/')[-1] if id_element is not None and id_element.text else ""
                
                # Extract title
                title_element = entry.find('atom:title', namespace)
                title = title_element.text if title_element is not None and title_element.text else ""
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', namespace):
                    name_element = author.find('atom:name', namespace)
                    if name_element is not None and name_element.text:
                        authors.append(name_element.text)
                
                # Extract abstract
                summary_element = entry.find('atom:summary', namespace)
                abstract = summary_element.text if summary_element is not None and summary_element.text else ""
                
                # Extract publication date
                published_element = entry.find('atom:published', namespace)
                published = published_element.text if published_element is not None and published_element.text else ""
                
                # Extract URL
                url = id_element.text if id_element is not None and id_element.text else ""
                
                paper = Paper(
                    id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    published=published,
                    url=url,
                    source="arxiv"
                )
                papers.append(paper)
            
            return papers
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {str(e)}")
            return []