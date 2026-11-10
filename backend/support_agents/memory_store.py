
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from math import ceil

DB_PATH = Path(__file__).resolve().parent.parent / "supportmind.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS customer_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                resolution TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS shared_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue TEXT NOT NULL,
                resolution TEXT NOT NULL,
                approved_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                resolution TEXT NOT NULL,
                status TEXT DEFAULT 'pending_review',
                reviewer TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                response_time_ms INTEGER,
                estimated_input_tokens INTEGER,
                estimated_output_tokens INTEGER,
                repeat_issue INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)


def save_customer_memory(customer_id, issue, resolution):
    initialize_database()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO customer_memories
            (customer_id, issue, resolution, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            customer_id, issue, resolution,
            datetime.now(timezone.utc).isoformat()
        ))

    return "Customer support memory saved successfully."


def search_customer_memory(customer_id):
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT issue, resolution, created_at
            FROM customer_memories
            WHERE customer_id = ?
            ORDER BY id DESC LIMIT 10
        """, (customer_id,)).fetchall()

    if not rows:
        return "No previous support history found."

    return "\n".join(
        f"Issue: {r['issue']} | Resolution: {r['resolution']}"
        for r in rows
    )


def search_shared_knowledge(issue):
    """Find previously approved solutions for similar issues."""
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT issue, resolution
            FROM shared_knowledge
            ORDER BY id DESC LIMIT 200
        """).fetchall()

    query_words = set(issue.lower().split())
    query_words = {w for w in query_words if len(w) > 2}

    matches = []

    for row in rows:
        words = set(row["issue"].lower().split())
        words = {w for w in words if len(w) > 2}

        if not query_words or not words:
            continue

        score = len(query_words & words) / len(query_words)

        if score >= 0.25:
            matches.append((score, row["issue"], row["resolution"]))

    matches.sort(reverse=True)

    if not matches:
        return "No matching approved shared solutions found."

    return "\n".join(
        f"Previous Issue: {issue}\nVerified Resolution: {resolution}"
        for _, issue, resolution in matches[:5]
    )


def create_support_ticket(
    customer_id, issue, resolution, response_time_ms
):
    initialize_database()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO support_tickets
            (customer_id, issue, resolution, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            customer_id, issue, resolution,
            datetime.now(timezone.utc).isoformat()
        ))

        ticket_id = cursor.lastrowid

        repeat = connection.execute("""
            SELECT COUNT(*) FROM shared_knowledge
            WHERE lower(issue) = lower(?)
        """, (issue,)).fetchone()[0] > 0

        connection.execute("""
            INSERT INTO performance_metrics
            (ticket_id, response_time_ms,
             estimated_input_tokens, estimated_output_tokens,
             repeat_issue, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            response_time_ms,
            ceil(len(issue) / 4),
            ceil(len(resolution) / 4),
            int(repeat),
            datetime.now(timezone.utc).isoformat()
        ))

    return ticket_id


def get_support_tickets():
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM support_tickets
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def review_support_ticket(ticket_id, approved, reviewer="Human Reviewer"):
    initialize_database()

    with get_connection() as connection:
        ticket = connection.execute("""
            SELECT * FROM support_tickets WHERE id = ?
        """, (ticket_id,)).fetchone()

        if not ticket:
            return False, "Ticket not found."

        if ticket["status"] != "pending_review":
            return False, "Ticket has already been reviewed."

        if approved:
            connection.execute("""
                INSERT INTO shared_knowledge
                (issue, resolution, approved_by, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                ticket["issue"],
                ticket["resolution"],
                reviewer,
                datetime.now(timezone.utc).isoformat()
            ))

        status = "approved" if approved else "rejected"

        connection.execute("""
            UPDATE support_tickets
            SET status = ?, reviewer = ?
            WHERE id = ?
        """, (status, reviewer, ticket_id))

    return True, status


def get_performance_metrics():
    initialize_database()

    with get_connection() as connection:
        total = connection.execute("""
            SELECT COUNT(*) FROM support_tickets
        """).fetchone()[0]

        approved = connection.execute("""
            SELECT COUNT(*) FROM support_tickets
            WHERE status = 'approved'
        """).fetchone()[0]

        metrics = connection.execute("""
            SELECT
                COUNT(*) AS total,
                AVG(response_time_ms) AS avg_time,
                SUM(estimated_input_tokens) AS input_tokens,
                SUM(estimated_output_tokens) AS output_tokens,
                SUM(repeat_issue) AS repeat_issues
            FROM performance_metrics
        """).fetchone()

    return {
        "total_tickets": total,
        "approved_tickets": approved,
        "average_response_time_ms": round(metrics["avg_time"] or 0),
        "estimated_input_tokens": metrics["input_tokens"] or 0,
        "estimated_output_tokens": metrics["output_tokens"] or 0,
        "repeat_issues": metrics["repeat_issues"] or 0
    }


initialize_database()
