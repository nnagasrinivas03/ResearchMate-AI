const topicInput =
    document.getElementById("topicInput");

const startButton =
    document.getElementById("startButton");

const activity =
    document.getElementById("activity");

const report =
    document.getElementById("report");

const sources =
    document.getElementById("sources");

const conflicts =
    document.getElementById("conflicts");

const sourceCount =
    document.getElementById("sourceCount");

const evidenceCount =
    document.getElementById("evidenceCount");

const conflictCount =
    document.getElementById("conflictCount");

const connectionStatus =
    document.getElementById(
        "connectionStatus"
    );

const copyButton =
    document.getElementById(
        "copyButton"
    );


let socket = null;


function connectSocket() {

    const protocol =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const wsUrl =
        `${protocol}//${window.location.host}/ws/research`;

    socket = new WebSocket(wsUrl);


    socket.onopen = () => {

        connectionStatus.textContent =
            "● ONLINE";

        connectionStatus.className =
            "status online";
    };


    socket.onclose = () => {

        connectionStatus.textContent =
            "● OFFLINE";

        connectionStatus.className =
            "status offline";
    };


    socket.onerror = () => {

        connectionStatus.textContent =
            "● ERROR";

        connectionStatus.className =
            "status offline";
    };


    socket.onmessage = (event) => {

        const data =
            JSON.parse(event.data);

        handleMessage(data);
    };
}


function resetDashboard() {

    activity.innerHTML = "";

    sources.innerHTML =
        '<div class="empty">Waiting for sources...</div>';

    conflicts.innerHTML =
        '<div class="empty">Checking conflicts...</div>';

    report.innerHTML =
        '<div class="empty">Generating report...</div>';

    sourceCount.textContent = "0";

    evidenceCount.textContent = "0";

    conflictCount.textContent = "0";


    document
        .querySelectorAll(".agent-card")
        .forEach(card => {

            card.classList.remove(
                "running",
                "completed",
                "error"
            );

            card.querySelector(
                ".agent-status"
            ).textContent =
                "WAITING";
        });
}


function updateAgent(
    agent,
    status
) {

    const card =
        document.querySelector(
            `.agent-card[data-agent="${agent}"]`
        );

    if (!card) return;


    card.classList.remove(
        "running",
        "completed",
        "error"
    );


    if (
        status === "running" ||
        status === "completed" ||
        status === "error"
    ) {

        card.classList.add(
            status
        );
    }


    const statusElement =
        card.querySelector(
            ".agent-status"
        );


    statusElement.textContent =
        status.toUpperCase();
}


function addActivity(
    time,
    agent,
    message
) {

    const item =
        document.createElement(
            "div"
        );

    item.className =
        "activity-item";


    item.innerHTML = `
        <div class="activity-time">
            ${time}
        </div>

        <div class="activity-message">
            <strong>${agent}</strong>
            — ${message}
        </div>
    `;


    activity.appendChild(item);

    activity.scrollTop =
        activity.scrollHeight;
}


function renderSources(
    sourceList
) {

    if (
        !sourceList ||
        sourceList.length === 0
    ) {

        sources.innerHTML =
            '<div class="empty">No sources found.</div>';

        return;
    }


    sources.innerHTML =
        sourceList.map(source => {

            const id =
                source.citation_id || "?";

            const title =
                escapeHtml(
                    source.title ||
                    "Untitled Source"
                );

            const type =
                escapeHtml(
                    source.source_type ||
                    "Unknown"
                );

            const abstract =
                escapeHtml(
                    (
                        source.abstract ||
                        source.content ||
                        source.full_text ||
                        "No description available."
                    ).substring(
                        0,
                        500
                    )
                );

            const url =
                source.url || "";


            return `
                <div class="source-card">

                    <div class="source-top">

                        <span class="source-number">
                            [${id}]
                        </span>

                        <span class="source-type">
                            ${type}
                        </span>

                    </div>

                    <h3>
                        ${title}
                    </h3>

                    <p>
                        ${abstract}
                    </p>

                    ${
                        url
                        ?
                        `<a
                            href="${url}"
                            target="_blank"
                            rel="noopener"
                        >
                            Open Source →
                        </a>`
                        :
                        ""
                    }

                </div>
            `;

        }).join("");
}


function renderConflicts(
    conflictList
) {

    if (
        !conflictList ||
        conflictList.length === 0
    ) {

        conflicts.innerHTML =
            '<div class="empty">No significant conflicts detected.</div>';

        return;
    }


    conflicts.innerHTML =
        conflictList.map(conflict => {

            return `
                <div class="conflict-card">

                    <h3>
                        ${escapeHtml(
                            conflict.claim ||
                            "Conflicting finding"
                        )}
                    </h3>

                    <p>
                        <strong>
                            Source ${conflict.source_a}
                        </strong>:
                        ${escapeHtml(
                            conflict.position_a ||
                            ""
                        )}
                    </p>

                    <p>
                        <strong>
                            Source ${conflict.source_b}
                        </strong>:
                        ${escapeHtml(
                            conflict.position_b ||
                            ""
                        )}
                    </p>

                    <p>
                        <strong>
                            Why:
                        </strong>
                        ${escapeHtml(
                            conflict.reason ||
                            ""
                        )}
                    </p>

                    <p>
                        <strong>
                            Severity:
                        </strong>
                        ${escapeHtml(
                            conflict.severity ||
                            "unknown"
                        )}
                    </p>

                </div>
            `;

        }).join("");
}


function handleMessage(
    data
) {

    if (
        data.type === "started"
    ) {

        addActivity(
            getTime(),
            "SYSTEM",
            data.message
        );

        return;
    }


    if (
        data.type === "agent_event"
    ) {

        updateAgent(
            data.agent,
            data.status
        );

        addActivity(
            data.timestamp ||
                getTime(),
            data.agent,
            data.message
        );

        return;
    }


    if (
        data.type === "result"
    ) {

        const result =
            data.result;


        sourceCount.textContent =
            result.sources.length;

        evidenceCount.textContent =
            result.evidence.length;

        conflictCount.textContent =
            result.conflicts.length;


        renderSources(
            result.sources
        );

        renderConflicts(
            result.conflicts
        );


        report.textContent =
            result.report;


        addActivity(
            getTime(),
            "SYSTEM",
            `Research #${result.research_id} saved to database.`
        );

        return;
    }


    if (
        data.type === "completed"
    ) {

        startButton.disabled =
            false;

        startButton.textContent =
            "START RESEARCH";

        addActivity(
            getTime(),
            "SYSTEM",
            data.message
        );

        return;
    }


    if (
        data.type === "error"
    ) {

        startButton.disabled =
            false;

        startButton.textContent =
            "START RESEARCH";

        addActivity(
            getTime(),
            "ERROR",
            data.message
        );

        return;
    }
}


function getTime() {

    return new Date()
        .toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            }
        );
}


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value;

    return div.innerHTML;
}


startButton.addEventListener(
    "click",
    startResearch
);


topicInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
        ) {

            startResearch();
        }
    }
);


async function startResearch() {

    const topic =
        topicInput.value.trim();


    if (!topic) {

        alert(
            "Please enter a research topic."
        );

        return;
    }


    resetDashboard();


    startButton.disabled =
        true;

    startButton.textContent =
        "RESEARCHING...";


    if (
        !socket ||
        socket.readyState !== WebSocket.OPEN
    ) {

        connectSocket();

        await new Promise(
            resolve => {

                const check =
                    setInterval(
                        () => {

                            if (
                                socket &&
                                socket.readyState ===
                                WebSocket.OPEN
                            ) {

                                clearInterval(
                                    check
                                );

                                resolve();
                            }

                        },
                        100
                    );
            }
        );
    }


    socket.send(
        JSON.stringify({
            topic: topic
        })
    );
}


copyButton.addEventListener(
    "click",
    async () => {

        const text =
            report.textContent;

        if (!text) return;

        await navigator.clipboard.writeText(
            text
        );

        copyButton.textContent =
            "COPIED";

        setTimeout(
            () => {

                copyButton.textContent =
                    "COPY";

            },
            1500
        );
    }
);


connectSocket();