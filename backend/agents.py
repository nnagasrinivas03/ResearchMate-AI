import json
import re
import httpx

from .config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)


# ============================================================
# JSON PARSER
# ============================================================

def parse_json_response(text: str):
    if not text:
        return {}

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to extract JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(
                text[start:end + 1]
            )
        except Exception:
            pass

    return {}


# ============================================================
# OLLAMA LLM CALL
# ============================================================

async def ask_llm(prompt: str):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,

            # Reduced from 8192
            # to reduce memory/time pressure
            "num_ctx": 4096,

            "num_predict": 1200
        }
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=OLLAMA_TIMEOUT,
        write=30.0,
        pool=30.0
    )

    try:

        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload
            )

            response.raise_for_status()

            data = response.json()

        result = data.get(
            "response",
            ""
        )

        if not result:
            print("WARNING: Ollama returned an empty response.")

        return result

    except httpx.ConnectError:

        print(
            "ERROR: Cannot connect to Ollama."
        )

        print(
            f"Check that Ollama is running at: {OLLAMA_URL}"
        )

        return ""

    except httpx.TimeoutException:

        print(
            "ERROR: Ollama request timed out."
        )

        return ""

    except httpx.HTTPStatusError as e:

        print(
            f"ERROR: Ollama HTTP error: {e}"
        )

        return ""

    except Exception as e:

        print(
            f"ERROR: Ollama error: {e}"
        )

        return ""


# ============================================================
# SOURCE TEXT
# ============================================================

def build_source_text(
    sources,
    max_sources=12,
    max_chars_per_source=3500
):

    blocks = []

    # Limit number of sources sent to LLM
    selected_sources = sources[:max_sources]

    for source in selected_sources:

        citation_id = source.get(
            "citation_id",
            "?"
        )

        title = source.get(
            "title",
            "Untitled"
        )

        source_type = source.get(
            "source_type",
            "Unknown"
        )

        abstract = source.get(
            "abstract",
            ""
        )

        content = source.get(
            "full_text",
            ""
        )

        if not content:

            content = source.get(
                "content",
                ""
            )

        text = (
            content
            or abstract
            or "No text available."
        )

        # Reduce huge source content
        text = text[:max_chars_per_source]

        blocks.append(
            f"""
SOURCE [{citation_id}]
TYPE: {source_type}
TITLE: {title}
URL: {source.get("url", "")}

TEXT:
{text}
"""
        )

    return "\n".join(blocks)


# ============================================================
# EVIDENCE AGENT
# ============================================================

async def evidence_agent(
    topic,
    sources
):

    print(
        f"Evidence Agent: processing {len(sources)} sources..."
    )

    source_text = build_source_text(
        sources,
        max_sources=12,
        max_chars_per_source=3000
    )

    prompt = f"""
You are an academic Evidence Extraction Agent.

Research topic:
{topic}

Source material:
{source_text}

Extract only claims directly supported by
the supplied source material.

Do not invent information.

Return ONLY JSON.

Format:

{{
  "evidence": [
    {{
      "claim": "specific factual claim",
      "source_ids": [1],
      "support": "supports",
      "confidence": "high"
    }}
  ]
}}

Rules:

- Use only existing citation numbers.
- support = supports, contradicts, or neutral.
- confidence = high, medium, or low.
- Maximum 10 evidence items.
- Keep claims short and specific.
"""

    result = await ask_llm(
        prompt
    )

    if not result:

        print(
            "Evidence Agent: Ollama returned no response."
        )

        return []

    parsed = parse_json_response(
        result
    )

    evidence = parsed.get(
        "evidence",
        []
    )

    if not isinstance(
        evidence,
        list
    ):
        return []

    print(
        f"Evidence Agent: {len(evidence)} evidence items."
    )

    return evidence


# ============================================================
# CONFLICT AGENT
# ============================================================

async def conflict_agent(
    topic,
    evidence,
    sources
):

    print(
        "Conflict Agent: comparing evidence..."
    )

    source_text = build_source_text(
        sources,
        max_sources=12,
        max_chars_per_source=2500
    )

    evidence_text = json.dumps(
        evidence[:10],
        indent=2
    )

    prompt = f"""
You are an academic Conflict Detection Agent.

Research topic:
{topic}

Evidence:
{evidence_text}

Source material:
{source_text}

Identify genuine disagreements between
sources about the same research question.

Do not treat different topics as conflicts.

Return ONLY JSON.

Format:

{{
  "conflicts": [
    {{
      "claim": "common research question",
      "source_a": 1,
      "source_b": 2,
      "position_a": "finding from source A",
      "position_b": "finding from source B",
      "reason": "why they disagree",
      "severity": "low"
    }}
  ]
}}

Rules:

- Maximum 5 conflicts.
- source_a and source_b must be existing citation IDs.
- severity = low, medium, or high.
- If there is no genuine conflict, return:
  {{
    "conflicts": []
  }}
"""

    result = await ask_llm(
        prompt
    )

    if not result:

        print(
            "Conflict Agent: no response."
        )

        return []

    parsed = parse_json_response(
        result
    )

    conflicts = parsed.get(
        "conflicts",
        []
    )

    if not isinstance(
        conflicts,
        list
    ):
        return []

    print(
        f"Conflict Agent: {len(conflicts)} conflicts."
    )

    return conflicts


# ============================================================
# WRITER AGENT
# ============================================================

async def writer_agent(
    topic,
    sources,
    evidence,
    conflicts
):

    print(
        "Writer Agent: generating report..."
    )

    source_text = build_source_text(
        sources,
        max_sources=12,
        max_chars_per_source=2500
    )

    evidence_text = json.dumps(
        evidence[:10],
        indent=2
    )

    conflicts_text = json.dumps(
        conflicts[:5],
        indent=2
    )

    prompt = f"""
You are the Research Writer Agent.

Write a concise academic research report.

Research topic:
{topic}

SOURCE MATERIAL:
{source_text}

EVIDENCE:
{evidence_text}

CONFLICTS:
{conflicts_text}

Requirements:

1. Use only supplied information.

2. Do not invent facts.

3. Use citations such as [1], [2].

4. Only use citation numbers that exist.

5. Explain important conflicts.

6. If there are no conflicts, say:
"No significant conflicts were identified
among the analyzed sources."

7. Use exactly these sections:

# Research Summary

## 1. Overview

## 2. Key Findings

## 3. Evidence

## 4. Conflicting Findings

## 5. Research Gaps

## 6. Conclusion

## References

8. Keep the report concise.

9. References must use only supplied sources.

10. Do not claim that a source was fully read
if only metadata or an abstract was available.
"""

    result = await ask_llm(
        prompt
    )

    if not result:

        print(
            "Writer Agent: Ollama returned no report."
        )

        return (
            "# Research Summary\n\n"
            "The research report could not be "
            "generated because the local LLM "
            "did not return a response."
        )

    print(
        "Writer Agent: report generated."
    )

    return result