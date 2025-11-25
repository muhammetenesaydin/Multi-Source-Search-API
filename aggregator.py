"""
Aggregator for combining and ranking search results from multiple sources.
"""
import os 
import json
import logging
from typing import List,Dict,Any
from datetime import datetime
import google.generativeai as genai
from models import SearchResult, Repository, Paper
from connectors.github import GitHubConnector

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResultAggregator:
    """Aggregator for combining and ranking search results."""

    def __init__(self):
        self.github = GitHubConnector()

    async def _attach_readmes(self, repos: List[Repository]) -> List[Repository]:
        """Fetch README for each repository asynchronously."""
        for repo in repos:
            try:
                readme = await self.github.get_repository_readme(repo.owner, repo.name)
                repo.readme = readme
                logger.info(f"README yüklendi → {repo.full_name}")
            except Exception as e:
                logger.warning(f"README alınamadı: {repo.full_name} → {e}")
                repo.readme = None
        return repos

    async def aggregate_results(
        self,
        repositories: List[Repository],
        papers: List[Paper],
        max_results: int = 10
    ) -> SearchResult:
        """
        Aggregate and rank search results.
        """

        # Repository'leri yıldız sayısına göre sırala
        sorted_repos = sorted(repositories, key=lambda r: r.stars, reverse=True)

        # README'leri ekle (ASYNC!)
        sorted_repos = await self._attach_readmes(sorted_repos)

        # Paper'lar aynı şekilde kalıyor (şimdilik bir ranking yok)
        return SearchResult(
            repositories=sorted_repos[:max_results],
            papers=papers[:max_results]
        )

    def _calculate_repository_score(self, repo: Repository) -> float:
        """(Opsiyonel) Repo skoru hesaplama."""
        score = float(repo.stars)
        try:
            updated = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            days = (datetime.now(updated.tzinfo) - updated).days
            if days < 30:
                score *= 1.5
            elif days < 365:
                score *= 1.1
        except:
            pass
        return score

    def _calculate_paper_score(self, paper: Paper) -> float:
        """Paper skoru (şimdilik sabit)."""
        return 1.0



class AIProjectPlanner:
    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY bulunamadı")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    async def create_project_plan(self, title: str, description: str, similar_projects: List[Dict]) -> Dict[str, Any]:
        """AI ile proje planı oluştur"""
        
        prompt = f"""Kullanıcı şu projeyi yapmak istiyor:

Proje Başlığı: {title}
Kullanıcı Açıklaması: {description}

Bulunan benzer projeler:
{json.dumps(similar_projects[:3], indent=2, ensure_ascii=False)}

Bu bilgilere dayanarak detaylı bir proje planı oluştur. JSON formatında yanıt ver:

{{
  "project_summary": "Proje hakkında kısa analiz",
  "tech_stack": ["Python", "Flask"],
  "roadmap": [
    {{
      "task": "Görev adı",
      "priority": "high",
      "estimated_hours": 8,
      "description": "Detaylı açıklama"
    }}
  ],
  "key_insights": ["İpucu 1", "İpucu 2"]
}}"""

        try:
            response = await self.model.generate_content_async(prompt)
            
            # JSON'ı temizle
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
            
        except Exception as e:
            print(f"AI planlama hatası: {e}")
            # Basit yedek plan
            return {
                "project_summary": f"{title} için temel plan",
                "tech_stack": ["Python"],
                "roadmap": [
                    {
                        "task": "Proje yapısını oluştur",
                        "priority": "high",
                        "estimated_hours": 16,
                        "description": "Temel dosya yapısı"
                    }
                ],
                "key_insights": ["Basit başla", "Kademeli geliştir"]
            }