"""
FastAPI application for the multi-source search engine.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
load_dotenv()  
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from models import SearchResult, ProjectIdeaRequest, RoadmapResponse
from connectors.github import GitHubConnector
from connectors.arxiv import ArxivConnector
from connectors.semantic_scholar import SemanticScholarConnector
from connectors.web_search import WebSearchConnector
from aggregator import ResultAggregator, AIProjectPlanner


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Source Search & AI Project Planner API",
    description="Search repositories/papers and turn ideas into roadmaps",
    version="2.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # sadece test için
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- connectors ----------
github_connector = GitHubConnector()
arxiv_connector = ArxivConnector()
semantic_scholar_connector = SemanticScholarConnector()
web_search_connector = WebSearchConnector()
aggregator = ResultAggregator()
planner = AIProjectPlanner()

# ---------- root ----------
@app.get("/")
async def root():
    return {"message": "Multi-Source Search & AI Project Planner API"}

# ---------- search ----------
@app.get("/search", response_model=SearchResult)
async def search(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=100)
):
    logger.info(f"Search: query='{query}', max_results={max_results}")
    tasks = [
        github_connector.search_repositories(query, max_results),
        arxiv_connector.search_papers(query, max_results),
        semantic_scholar_connector.search_papers(query, max_results),
        web_search_connector.search_articles(query, max_results)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    repositories = results[0] if not isinstance(results[0], Exception) else []
    papers = (
        (results[1] if not isinstance(results[1], Exception) else []) +
        (results[2] if not isinstance(results[2], Exception) else []) +
        (results[3] if not isinstance(results[3], Exception) else [])
    )
    aggregated = await aggregator.aggregate_results(repositories, papers, max_results)
    logger.info(f"Search finished: {len(aggregated.repositories)} repos, {len(aggregated.papers)} papers")
    return aggregated

# ---------- plan ----------
@app.post("/plan/create", response_model=RoadmapResponse)
async def create_project_plan(request: ProjectIdeaRequest):
    """Proje fikrinden roadmap oluştur"""
    try:
        repos = await github_connector.search_repositories(
            query=f"{request.title} {request.description}",
            max_results=request.max_similar_projects
        )
        repos_with_readme = await aggregator._attach_readmes(repos)

        similar_projects = [
            {
                "name": r.name,
                "description": r.description or "",
                "readme_snippet": (r.readme or "")[:1000],
                "stars": r.stars,
                "language": r.language or "Unknown",
            }
            for r in repos_with_readme
        ]
        plan_result = await planner.create_project_plan(
            title=request.title,
            description=request.description,
            similar_projects=similar_projects
        )

        return RoadmapResponse(
            project_summary=plan_result["project_summary"],
            tech_stack=plan_result["tech_stack"],
            roadmap=plan_result["roadmap"],
            similar_projects_found=len(similar_projects),
            key_insights=plan_result["key_insights"]
        )
    except Exception as e:
        logger.exception("Planlama hatası")
        raise HTTPException(status_code=500, detail=f"Planlama hatası: {str(e)}")

@app.get("/plan/example")
async def plan_example():
    return {
        "example": {
            "title": "chatbot",
            "description": "Ben kendimi tanıtacak bir chatbot projesi yapmak istiyorum",
            "max_similar_projects": 5
        },
        "usage": "POST /plan/create with JSON body"
    }

# ---------- plan from search ----------
@app.post("/plan/from-search", response_model=RoadmapResponse)
async def plan_from_search(request: ProjectIdeaRequest):
    """Kullanıcıdan sadece başlık ve açıklama alıp GitHub’da arama yapar ve roadmap oluşturur."""
    try:
        # 1. GitHub’da benzer projeleri ara
        repos = await github_connector.search_repositories(
            query=f"{request.title} {request.description}",
            max_results=request.max_similar_projects
        )

        # 2. README’leri çek
        repos_with_readme = await aggregator._attach_readmes(repos)

        # 3. Gemini’ye gönderilecek formata dönüştür
        similar_projects = [
            {
                "name": r.name,
                "description": r.description or "",
                "readme_snippet": (r.readme or "")[:2000],
                "stars": r.stars,
                "language": r.language or "Unknown",
            }
            for r in repos_with_readme
        ]

        # 4. Gemini’den plan oluştur
        plan_result = await planner.create_project_plan(
            title=request.title,
            description=request.description,
            similar_projects=similar_projects
        )

        return RoadmapResponse(
            project_summary=plan_result["project_summary"],
            tech_stack=plan_result["tech_stack"],
            roadmap=plan_result["roadmap"],
            similar_projects_found=len(similar_projects),
            key_insights=plan_result["key_insights"]
        )

    except Exception as e:
        logger.exception("Planlama hatası")
        raise HTTPException(status_code=500, detail=f"Planlama hatası: {str(e)}")

# ---------- run ----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)