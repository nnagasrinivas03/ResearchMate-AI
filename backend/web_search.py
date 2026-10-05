import httpx

from .config import (
    WEB_SEARCH_API_KEY,
    MAX_WEB_RESULTS
)


TAVILY_URL = "https://api.tavily.com/search"


async def web_search(
    topic: str,
    max_results: int = MAX_WEB_RESULTS
):

    if not WEB_SEARCH_API_KEY:

        return [

            {
                "source_type": "Web",
                "title":
                    "Web Search Not Configured",
                "url": "",
                "content":
                    "Tavily API key is not configured."
            }

        ]

    payload = {

        "api_key":
            WEB_SEARCH_API_KEY,

        "query":
            topic,

        "search_depth":
            "advanced",

        "max_results":
            max_results,

        "include_answer":
            False,

        "include_raw_content":
            False
    }

    async with httpx.AsyncClient(
        timeout=40
    ) as client:

        response = await client.post(
            TAVILY_URL,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

    results = []

    for item in data.get(
        "results",
        []
    ):

        results.append({

            "source_type":
                "Web",

            "title":
                item.get(
                    "title",
                    ""
                ),

            "url":
                item.get(
                    "url",
                    ""
                ),

            "content":
                item.get(
                    "content",
                    ""
                )
        })

    return results