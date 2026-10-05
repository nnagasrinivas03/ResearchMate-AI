import sqlite3
import json
from datetime import datetime

from .config import DATABASE_PATH


def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        research_runs (
            id INTEGER PRIMARY KEY
            AUTOINCREMENT,

            topic TEXT NOT NULL,

            report TEXT,

            sources_count INTEGER
            DEFAULT 0,

            evidence_count INTEGER
            DEFAULT 0,

            conflicts_count INTEGER
            DEFAULT 0,

            sources_json TEXT,

            evidence_json TEXT,

            conflicts_json TEXT,

            created_at TEXT
        )
        """
    )

    connection.commit()

    connection.close()


def save_research(
    topic,
    report,
    sources,
    evidence,
    conflicts
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO research_runs
        (
            topic,
            report,
            sources_count,
            evidence_count,
            conflicts_count,
            sources_json,
            evidence_json,
            conflicts_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            topic,
            report,
            len(sources),
            len(evidence),
            len(conflicts),
            json.dumps(sources),
            json.dumps(evidence),
            json.dumps(conflicts),
            datetime.now().isoformat()
        )
    )

    connection.commit()

    research_id = cursor.lastrowid

    connection.close()

    return research_id


def get_recent_research(limit=10):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            sources_count,
            evidence_count,
            conflicts_count,
            created_at
        FROM research_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]