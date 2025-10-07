"""
FastAPI application for the multi-source search engine.
"""
from fastapi import FastAPI, Query
from typing import List, Optional
import asyncio
import os
import logging

from models import SearchResult
from connectors.github import GitHubConnector
from connectors.arxiv import ArxivConnector
from connectors.semantic_scholar import SemanticScholarConnector
from connectors.web_search import WebSearchConnector
from aggregator import ResultAggregator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Source Search Engine API",
    description="Search for repositories and academic papers across multiple sources",
    version="1.0.0"
)

# Initialize connectors
github_connector = GitHubConnector()
arxiv_connector = ArxivConnector()
semantic_scholar_connector = SemanticScholarConnector()
web_search_connector = WebSearchConnector()
aggregator = ResultAggregator()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Multi-Source Search Engine API"}

@app.get("/search", response_model=SearchResult)
async def search(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results to return", ge=1, le=100)
):
    """
    Search for repositories and academic papers.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-100)
        
    Returns:
        SearchResult object containing repositories and papers
    """
    logger.info(f"Search request: query='{query}', max_results={max_results}")
    
    # Run all searches concurrently
    tasks = [
        github_connector.search_repositories(query, max_results),
        arxiv_connector.search_papers(query, max_results),
        semantic_scholar_connector.search_papers(query, max_results),
        web_search_connector.search_articles(query, max_results)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle potential exceptions
    repositories = results[0] if not isinstance(results[0], Exception) else []
    arxiv_papers = results[1] if not isinstance(results[1], Exception) else []
    semantic_scholar_papers = results[2] if not isinstance(results[2], Exception) else []
    web_papers = results[3] if not isinstance(results[3], Exception) else []
    
    # Ensure all are lists before combining
    repositories = repositories if isinstance(repositories, list) else []
    arxiv_papers = arxiv_papers if isinstance(arxiv_papers, list) else []
    semantic_scholar_papers = semantic_scholar_papers if isinstance(semantic_scholar_papers, list) else []
    web_papers = web_papers if isinstance(web_papers, list) else []
    
    # Combine papers from all sources
    all_papers = arxiv_papers + semantic_scholar_papers + web_papers
    
    # Aggregate results
    aggregated_results = aggregator.aggregate_results(repositories, all_papers, max_results)
    
    logger.info(f"Search completed: {len(aggregated_results.repositories)} repositories, {len(aggregated_results.papers)} papers")
    
    return aggregated_results

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)