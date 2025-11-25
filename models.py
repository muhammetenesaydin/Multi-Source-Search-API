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
    readme: Optional[str] = None 

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

class ProjectIdeaRequest(BaseModel):
    title: str  # "chatbot"
    description: str  # "Ben kendimi tanıtacak bir chatbot projesi..."
    include_similar_projects: bool = True
    max_similar_projects: int = 5

class Task(BaseModel):
    task: str
    priority: str  # "high", "medium", "low"
    estimated_hours: int
    description: str

class RoadmapResponse(BaseModel):
    project_summary: str
    tech_stack: List[str]
    roadmap: List[Task]
    similar_projects_found: int
    key_insights: List[str]