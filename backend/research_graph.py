import asyncio
from urllib.parse import urlparse

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .models import ResearchState

from .arxiv_client import (
    search_arxiv
)

from .semantic_scholar import (
    search_semantic_scholar
)

from .web_search import (
    web_search
)

from .source_reader import (
    enrich_source
)

from .agents import (
    evidence_agent,
    conflict_agent,
    writer_agent
)

from .conflict_detector import (
    validate_conflicts
)


class ResearchGraph:

    def __init__(
        self,
        event_callback
    ):

        self.event_callback = (
            event_callback
        )

        graph = StateGraph(
            ResearchState
        )

        graph.add_node(
            "retrieve",
            self.retrieve_node
        )

        graph.add_node(
            "read_sources",
            self.read_sources_node
        )

        graph.add_node(
            "evidence",
            self.evidence_node
        )

        graph.add_node(
            "conflict",
            self.conflict_node
        )

        graph.add_node(
            "writer",
            self.writer_node
        )

        graph.add_edge(
            START,
            "retrieve"
        )

        graph.add_edge(
            "retrieve",
            "read_sources"
        )

        graph.add_edge(
            "read_sources",
            "evidence"
        )

        graph.add_edge(
            "evidence",
            "conflict"
        )

        graph.add_edge(
            "conflict",
            "writer"
        )

        graph.add_edge(
            "writer",
            END
        )

        self.graph = graph.compile()

    async def emit(
        self,
        agent,
        status,
        message
    ):

        await self.event_callback({

            "agent":
                agent,

            "status":
                status,

            "message":
                message
        })

    async def retrieve_node(
        self,
        state
    ):

        topic = state["topic"]

        await self.emit(
            "Research Coordinator",
            "running",
            "Launching research agents..."
        )

        async def run_web():

            await self.emit(
                "Web Researcher",
                "running",
                "Searching live web sources..."
            )

            try:

                results = await web_search(
                    topic
                )

                await self.emit(
                    "Web Researcher",
                    "completed",
                    f"{len(results)} web sources found."
                )

                return results

            except Exception as error:

                await self.emit(
                    "Web Researcher",
                    "error",
                    str(error)
                )

                return []

        async def run_arxiv():

            await self.emit(
                "arXiv Agent",
                "running",
                "Searching academic papers..."
            )

            try:

                results = await search_arxiv(
                    topic
                )

                await self.emit(
                    "arXiv Agent",
                    "completed",
                    f"{len(results)} arXiv papers found."
                )

                return results

            except Exception as error:

                await self.emit(
                    "arXiv Agent",
                    "error",
                    str(error)
                )

                return []

        async def run_semantic():

            await self.emit(
                "Semantic Scholar",
                "running",
                "Searching research literature..."
            )

            try:

                results = (
                    await search_semantic_scholar(
                        topic
                    )
                )

                await self.emit(
                    "Semantic Scholar",
                    "completed",
                    f"{len(results)} papers found."
                )

                return results

            except Exception as error:

                await self.emit(
                    "Semantic Scholar",
                    "error",
                    str(error)
                )

                return []

        (
            web_results,
            arxiv_results,
            semantic_results
        ) = await asyncio.gather(
            run_web(),
            run_arxiv(),
            run_semantic()
        )

        sources = (
            web_results
            + arxiv_results
            + semantic_results
        )

        # Remove duplicate URLs/titles
        unique = []

        seen = set()

        for source in sources:

            key = (
                source.get("url")
                or source.get("title", "")
            ).lower().strip()

            if key and key not in seen:

                seen.add(key)

                unique.append(source)

        # Deterministic citation numbering
        for index, source in enumerate(
            unique,
            start=1
        ):

            source["citation_id"] = index

        await self.emit(
            "Research Coordinator",
            "completed",
            f"{len(unique)} unique sources collected."
        )

        return {
            "web_sources": web_results,
            "arxiv_sources": arxiv_results,
            "semantic_sources": semantic_results,
            "sources": unique
        }

    async def read_sources_node(
        self,
        state
    ):

        sources = state.get(
            "sources",
            []
        )

        await self.emit(
            "Source Reader",
            "running",
            f"Reading {len(sources)} sources..."
        )

        async def read_one(source):

            try:

                return await enrich_source(
                    source
                )

            except Exception:

                return source

        enriched = await asyncio.gather(
            *[
                read_one(source)
                for source in sources
            ]
        )

        full_count = sum(
            1
            for source in enriched
            if source.get(
                "read_status"
            ) == "full"
        )

        await self.emit(
            "Source Reader",
            "completed",
            f"{full_count} sources successfully read."
        )

        return {
            "sources": enriched
        }

    async def evidence_node(
        self,
        state
    ):

        await self.emit(
            "Evidence Agent",
            "running",
            "Extracting evidence from sources..."
        )

        evidence = await evidence_agent(
            state["topic"],
            state.get("sources", [])
        )

        await self.emit(
            "Evidence Agent",
            "completed",
            f"{len(evidence)} evidence items extracted."
        )

        return {
            "evidence": evidence
        }

    async def conflict_node(
        self,
        state
    ):

        await self.emit(
            "Conflict Agent",
            "running",
            "Comparing findings for contradictions..."
        )

        conflicts = await conflict_agent(
            state["topic"],
            state.get("evidence", []),
            state.get("sources", [])
        )

        conflicts = validate_conflicts(
            conflicts,
            state.get("sources", [])
        )

        await self.emit(
            "Conflict Agent",
            "completed",
            f"{len(conflicts)} conflicts detected."
        )

        return {
            "conflicts": conflicts
        }

    async def writer_node(
        self,
        state
    ):

        await self.emit(
            "Writer Agent",
            "running",
            "Generating citation-grounded report..."
        )

        report = await writer_agent(
            state["topic"],
            state.get("sources", []),
            state.get("evidence", []),
            state.get("conflicts", [])
        )

        await self.emit(
            "Writer Agent",
            "completed",
            "Research report generated."
        )

        return {
            "report": report
        }

    async def run(
        self,
        topic
    ):

        return await self.graph.ainvoke(
            {
                "topic": topic
            }
        )