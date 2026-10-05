import re
import fitz
import httpx

from bs4 import BeautifulSoup

from .config import SOURCE_READ_TIMEOUT


MAX_TEXT_LENGTH = 12000


def clean_text(text: str) -> str:

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


async def read_web_page(url: str):

    if not url:

        return ""

    try:

        headers = {
            "User-Agent":
                "ResearchMateAI/1.0"
        }

        async with httpx.AsyncClient(
            timeout=SOURCE_READ_TIMEOUT,
            follow_redirects=True,
            headers=headers
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside"
            ]
        ):

            element.decompose()

        text = soup.get_text(
            separator=" "
        )

        return clean_text(text)[
            :MAX_TEXT_LENGTH
        ]

    except Exception:

        return ""


async def read_pdf(url: str):

    if not url:

        return ""

    try:

        async with httpx.AsyncClient(
            timeout=SOURCE_READ_TIMEOUT,
            follow_redirects=True
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

        document = fitz.open(
            stream=response.content,
            filetype="pdf"
        )

        pages = []

        for page in document:

            pages.append(
                page.get_text()
            )

            if sum(
                len(p)
                for p in pages
            ) >= MAX_TEXT_LENGTH:

                break

        text = clean_text(
            " ".join(pages)
        )

        return text[:MAX_TEXT_LENGTH]

    except Exception:

        return ""


async def enrich_source(source):

    source = dict(source)

    existing = (
        source.get("content")
        or source.get("full_text")
        or ""
    )

    if existing:

        source["full_text"] = (
            existing[:MAX_TEXT_LENGTH]
        )

        return source

    pdf_url = source.get(
        "pdf_url",
        ""
    )

    url = source.get(
        "url",
        ""
    )

    text = ""

    if pdf_url:

        text = await read_pdf(
            pdf_url
        )

    if not text and url:

        if ".pdf" in url.lower():

            text = await read_pdf(
                url
            )

        else:

            text = await read_web_page(
                url
            )

    if not text:

        text = (
            source.get(
                "abstract",
                ""
            )
            or source.get(
                "content",
                ""
            )
        )

    source["full_text"] = (
        text[:MAX_TEXT_LENGTH]
    )

    source["read_status"] = (
        "full"
        if text
        else "metadata_only"
    )

    return source