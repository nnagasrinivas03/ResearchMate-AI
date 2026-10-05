from datetime import datetime

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.responses import (
    FileResponse
)

from fastapi.staticfiles import (
    StaticFiles
)

from .research_graph import (
    ResearchGraph
)

from .database import (
    init_database,
    save_research,
    get_recent_research
)

from .config import (
    FRONTEND_DIR
)


app = FastAPI(
    title="ResearchMate AI",
    version="2.0"
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(FRONTEND_DIR)
    ),
    name="static"
)


@app.on_event("startup")
async def startup():

    init_database()


@app.get("/")
async def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/health")
async def health():

    return {
        "status": "online",
        "system": "ResearchMate AI",
        "version": "2.0"
    }


@app.get("/api/history")
async def history():

    return {
        "history":
            get_recent_research()
    }


@app.websocket(
    "/ws/research"
)
async def research_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        request = (
            await websocket.receive_json()
        )

        topic = (
            request
            .get("topic", "")
            .strip()
        )

        if not topic:

            await websocket.send_json({

                "type": "error",

                "message":
                    "Research topic is required."
            })

            return

        async def send_event(event):

            await websocket.send_json({

                "type":
                    "agent_event",

                "timestamp":
                    datetime.now().strftime(
                        "%H:%M:%S"
                    ),

                **event
            })

        await websocket.send_json({

            "type":
                "started",

            "message":
                f"Research started: {topic}"
        })

        graph = ResearchGraph(
            send_event
        )

        result = await graph.run(
            topic
        )

        sources = result.get(
            "sources",
            []
        )

        evidence = result.get(
            "evidence",
            []
        )

        conflicts = result.get(
            "conflicts",
            []
        )

        report = result.get(
            "report",
            ""
        )

        research_id = save_research(
            topic,
            report,
            sources,
            evidence,
            conflicts
        )

        await websocket.send_json({

            "type":
                "result",

            "result": {

                "research_id":
                    research_id,

                "report":
                    report,

                "sources":
                    sources,

                "evidence":
                    evidence,

                "conflicts":
                    conflicts
            }
        })

        await websocket.send_json({

            "type":
                "completed",

            "message":
                "Research workflow completed successfully."
        })

    except WebSocketDisconnect:

        print(
            "Research client disconnected."
        )

    except Exception as error:

        print(
            f"Research error: {error}"
        )

        try:

            await websocket.send_json({

                "type":
                    "error",

                "message":
                    str(error)
            })

        except Exception:

            pass