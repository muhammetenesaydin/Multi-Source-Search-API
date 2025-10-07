"""
Data models for the multi-source search engine.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Repository(BaseModel):
    """Model for GitHub repository."""
    id: int
    name: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    stars: int
    forks: int
    language: Optional[str] = None
    updated_at: str
    owner: str

class Paper(BaseModel):
    """Model for academic paper."""
    id: str
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    published: Optional[str] = None
    url: str
    source: str  # arxiv, semantic_scholar, etc.

class SearchResult(BaseModel):
    """Model for search result."""
    repositories: List[Repository]
    papers: List[Paper]