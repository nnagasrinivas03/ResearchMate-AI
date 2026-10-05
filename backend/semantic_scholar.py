import asyncio
import httpx

from .config import (
    SEMANTIC_SCHOLAR_API_KEY,
    MAX_SEMANTIC_RESULTS,
)

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


async def search_semantic_scholar(
    topic: str,
    limit: int = MAX_SEMANTIC_RESULTS
):
    headers = {}

    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    params = {
        "query": topic,
        "limit": limit,
        "fields": (
            "title,abstract,authors,year,url,"
            "citationCount,openAccessPdf"
        )
    }

    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True
        ) as client:

            response = await client.get(
                BASE_URL,
                params=params,
                headers=headers
            )

            # Rate limit
            if response.status_code == 429:
                print("Semantic Scholar rate limit reached.")
                print("Continuing without Semantic Scholar results.")
                return []

            response.raise_for_status()

            data = response.json()

    except httpx.HTTPStatusError as e:
        print(f"Semantic Scholar HTTP error: {e}")
        return []

    except Exception as e:
        print(f"Semantic Scholar error: {e}")
        return []

    papers = []

    for paper in data.get("data", []):
        authors = [
            author.get("name", "")
            for author in paper.get("authors", [])
        ]

        open_pdf = paper.get("openAccessPdf") or {}

        papers.append({
            "source_type": "Semantic Scholar",
            "title": paper.get("title", ""),
            "authors": authors,
            "abstract": paper.get("abstract") or "",
            "year": paper.get("year"),
            "url": paper.get("url", ""),
            "citation_count": paper.get("citationCount", 0),
            "pdf_url": open_pdf.get("url", "")
        })

    return papers