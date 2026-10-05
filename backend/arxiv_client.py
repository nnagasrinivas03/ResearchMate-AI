import httpx
import feedparser
from urllib.parse import quote

ARXIV_URL = "https://export.arxiv.org/api/query"


async def search_arxiv(topic: str, max_results: int = 6):

    query = quote(topic)

    url = (
        f"{ARXIV_URL}"
        f"?search_query=all:{query}"
        f"&start=0"
        f"&max_results={max_results}"
        f"&sortBy=relevance"
    )

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.get(url)

        response.raise_for_status()

        feed = feedparser.parse(response.text)

    papers = []

    for entry in feed.entries:

        authors = [
            author.name
            for author in entry.get("authors", [])
        ]

        pdf_url = ""

        for link in entry.get("links", []):

            if link.get("type") == "application/pdf":

                pdf_url = link.get("href", "")
                break

        papers.append({

            "source_type": "arXiv",

            "title": entry.get(
                "title",
                ""
            ).strip(),

            "authors": authors,

            "abstract": entry.get(
                "summary",
                ""
            ).strip(),

            "published": entry.get(
                "published",
                ""
            ),

            "year": (
                entry.get("published", "")[:4]
                if entry.get("published")
                else None
            ),

            "url": entry.get(
                "link",
                ""
            ),

            "pdf_url": pdf_url,

            "paper_id": entry.get(
                "id",
                ""
            )
        })

    return papers