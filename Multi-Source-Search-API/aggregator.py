"""
Aggregator for combining and ranking search results from multiple sources.
"""
import logging
from typing import List
from datetime import datetime
from models import SearchResult, Repository, Paper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultAggregator:
    """Aggregator for combining and ranking search results."""
    
    def aggregate_results(self, repositories: List[Repository], papers: List[Paper], max_results: int = 10) -> SearchResult:
        """
        Aggregate and rank search results.
        
        Args:
            repositories: List of Repository objects
            papers: List of Paper objects
            max_results: Maximum number of results to return
            
        Returns:
            SearchResult object with ranked results
        """
        # For now, we'll just return the results as-is
        # In a more advanced implementation, we could implement ranking algorithms
        # based on relevance, recency, popularity, etc.
        
        # Sort repositories by stars (descending)
        sorted_repos = sorted(repositories, key=lambda r: r.stars, reverse=True)
        
        # For papers, we don't have a clear ranking metric, so we'll keep them as-is
        # In a real implementation, we might use citation count, publication date, etc.
        
        return SearchResult(
            repositories=sorted_repos[:max_results],
            papers=papers[:max_results]
        )
    
    def _calculate_repository_score(self, repo: Repository) -> float:
        """
        Calculate a relevance score for a repository.
        
        Args:
            repo: Repository object
            
        Returns:
            Score as float
        """
        # Simple scoring based on stars and recency
        # This is a basic implementation - a real system would be more sophisticated
        score = float(repo.stars)
        
        # Boost score for recently updated repositories
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days
            if days_since_update < 30:  # Boost for updates in last month
                score *= 1.5
            elif days_since_update < 365:  # Small boost for updates in last year
                score *= 1.1
        except Exception:
            # If we can't parse the date, just use the star count
            pass
        
        return score
    
    def _calculate_paper_score(self, paper: Paper) -> float:
        """
        Calculate a relevance score for a paper.
        
        Args:
            paper: Paper object
            
        Returns:
            Score as float
        """
        # For papers, we don't have clear metrics without more data
        # In a real implementation, we might consider citation count, publication venue, etc.
        return 1.0