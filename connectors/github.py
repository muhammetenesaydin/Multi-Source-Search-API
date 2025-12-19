"""
GitHub connector for searching repositories.
"""
import os
import aiohttp
import logging
from typing import List, Dict, Optional
from cachetools import TTLCache
from models import Repository
import base64
import requests
from os import getenv


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize cache with 1 hour TTL
cache = TTLCache(maxsize=100, ttl=3600)


GITHUB_TOKEN = getenv("GITHUB_TOKEN")

def get_readme(full_name: str):
    """
    full_name: 'owner/repo'
    """
    owner, repo = full_name.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        return None

    data = resp.json()
    content = data.get("content")

    if not content:
        return None

    # Base64 decode → UTF-8
    return base64.b64decode(content).decode("utf-8")

class GitHubConnector:
    """Connector for GitHub API to search repositories."""
    
    def __init__(self):
        """Initialize GitHub connector with API token from environment."""
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Multi-Source-Search-Engine"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        else:
            logger.warning("GITHUB_TOKEN not set. Rate limits may apply.")
    
    async def search_repositories(self, query: str, max_results: int = 10) -> List[Repository]:
        """
        Search for repositories on GitHub.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Repository objects
        """
        # Check cache first
        cache_key = f"github:{query}:{max_results}"
        if cache_key in cache:
            logger.info("Returning cached GitHub results")
            return cache[cache_key]
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(max_results, 100)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        repositories = []
                        for item in data.get("items", [])[:max_results]:
                            repo = Repository(
                                id=item["id"],
                                name=item["name"],
                                full_name=item["full_name"],
                                html_url=item["html_url"],
                                description=item.get("description", ""),
                                stars=item["stargazers_count"],
                                forks=item["forks_count"],
                                language=item.get("language"),
                                updated_at=item["updated_at"],
                                owner=item["owner"]["login"]
                            )
                            repositories.append(repo)
                        
                        # Cache results
                        cache[cache_key] = repositories
                        return repositories
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching GitHub repositories: {str(e)}")
            return []
    
    async def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Get the README content of a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string or None if not found
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # The content is base64 encoded
                        import base64
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        return content
                    else:
                        logger.error(f"Error fetching README: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting repository README: {str(e)}")
            return None