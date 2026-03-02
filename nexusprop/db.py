"""
SQLite Persistence Layer — Property Insights Melbourne.

Zero-config, file-based, serverless persistence using Python's built-in
sqlite3 module.  No external DB service required.

Strategy:
  - Three tables: properties, deals, offers
  - Each row stores <id, json_blob, updated_at>
  - Pydantic models are serialised with model_dump_json() and
    deserialised with model_validate_json()
  - DB file lives at ./pia.db (configurable via settings.database_url)

Thread-safety: sqlite3 in WAL mode + check_same_thread=False.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar, Type

import structlog

from nexusprop.models.property import Property
from nexusprop.models.deal import Deal
from nexusprop.models.offer import OfferDocument

logger = structlog.get_logger(__name__)

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Module-level connection  (created on init_db)
# ---------------------------------------------------------------------------
_conn: sqlite3.Connection | None = None

DB_PATH = Path("pia.db")  # overridden by init_db(path=...)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_db(path: str | Path | None = None) -> None:
    """
    Create (or open) the SQLite database and ensure tables exist.

    Call once at application startup.
    """
    global _conn, DB_PATH

    if path:
        DB_PATH = Path(path)

    logger.info("db_init", path=str(DB_PATH))

    _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    _conn.execute("PRAGMA journal_mode=WAL")       # better concurrent reads
    _conn.execute("PRAGMA synchronous=NORMAL")      # safe + fast
    _conn.execute("PRAGMA busy_timeout=5000")        # 5s retry on lock

    _conn.executescript("""
        CREATE TABLE IF NOT EXISTS properties (
            id          TEXT PRIMARY KEY,
            data        TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS deals (
            id          TEXT PRIMARY KEY,
            data        TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS offers (
            id          TEXT PRIMARY KEY,
            data        TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        -- Scout run log — tracks auto-scout activity
        CREATE TABLE IF NOT EXISTS scout_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at      TEXT NOT NULL,
            new_props   INTEGER NOT NULL DEFAULT 0,
            new_deals   INTEGER NOT NULL DEFAULT 0,
            duration_ms INTEGER NOT NULL DEFAULT 0,
            notes       TEXT
        );
    """)
    _conn.commit()
    logger.info("db_tables_ready")


def _get_conn() -> sqlite3.Connection:
    if _conn is None:
        raise RuntimeError("Database not initialised — call init_db() first")
    return _conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def _save(table: str, obj_id: str, json_blob: str) -> None:
    conn = _get_conn()
    conn.execute(
        f"INSERT OR REPLACE INTO {table} (id, data, updated_at) VALUES (?, ?, ?)",
        (obj_id, json_blob, _now_iso()),
    )
    conn.commit()


def _load_all(table: str) -> list[tuple[str, str]]:
    """Return list of (id, json_blob) for every row in *table*."""
    conn = _get_conn()
    rows = conn.execute(f"SELECT id, data FROM {table} ORDER BY updated_at DESC").fetchall()
    return rows


def _delete(table: str, obj_id: str) -> bool:
    conn = _get_conn()
    cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (obj_id,))
    conn.commit()
    return cur.rowcount > 0


def _count(table: str) -> int:
    conn = _get_conn()
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return row[0] if row else 0


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def save_property(prop: Property) -> None:
    _save("properties", str(prop.id), prop.model_dump_json())


def save_properties_bulk(props: list[Property]) -> None:
    conn = _get_conn()
    now = _now_iso()
    conn.executemany(
        "INSERT OR REPLACE INTO properties (id, data, updated_at) VALUES (?, ?, ?)",
        [(str(p.id), p.model_dump_json(), now) for p in props],
    )
    conn.commit()


def load_all_properties() -> dict[str, Property]:
    """Load all properties as {id_str: Property} dict."""
    rows = _load_all("properties")
    store: dict[str, Property] = {}
    for obj_id, blob in rows:
        try:
            store[obj_id] = Property.model_validate_json(blob)
        except Exception as exc:
            logger.warning("db_property_parse_error", id=obj_id, error=str(exc))
    return store


def delete_property(prop_id: str) -> bool:
    return _delete("properties", prop_id)


def count_properties() -> int:
    return _count("properties")


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

def save_deal(deal: Deal) -> None:
    _save("deals", str(deal.id), deal.model_dump_json())


def save_deals_bulk(deals: list[Deal]) -> None:
    conn = _get_conn()
    now = _now_iso()
    conn.executemany(
        "INSERT OR REPLACE INTO deals (id, data, updated_at) VALUES (?, ?, ?)",
        [(str(d.id), d.model_dump_json(), now) for d in deals],
    )
    conn.commit()


def load_all_deals() -> dict[str, Deal]:
    rows = _load_all("deals")
    store: dict[str, Deal] = {}
    for obj_id, blob in rows:
        try:
            store[obj_id] = Deal.model_validate_json(blob)
        except Exception as exc:
            logger.warning("db_deal_parse_error", id=obj_id, error=str(exc))
    return store


def delete_deal(deal_id: str) -> bool:
    return _delete("deals", deal_id)


def count_deals() -> int:
    return _count("deals")


# ---------------------------------------------------------------------------
# Offers
# ---------------------------------------------------------------------------

def save_offer(offer: OfferDocument) -> None:
    _save("offers", str(offer.id), offer.model_dump_json())


def load_all_offers() -> dict[str, OfferDocument]:
    rows = _load_all("offers")
    store: dict[str, OfferDocument] = {}
    for obj_id, blob in rows:
        try:
            store[obj_id] = OfferDocument.model_validate_json(blob)
        except Exception as exc:
            logger.warning("db_offer_parse_error", id=obj_id, error=str(exc))
    return store


def delete_offer(offer_id: str) -> bool:
    return _delete("offers", offer_id)


def count_offers() -> int:
    return _count("offers")


# ---------------------------------------------------------------------------
# Scout run logging
# ---------------------------------------------------------------------------

def log_scout_run(
    new_props: int,
    new_deals: int,
    duration_ms: int,
    notes: str | None = None,
) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO scout_runs (run_at, new_props, new_deals, duration_ms, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (_now_iso(), new_props, new_deals, duration_ms, notes),
    )
    conn.commit()


def get_scout_history(limit: int = 20) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, run_at, new_props, new_deals, duration_ms, notes "
        "FROM scout_runs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [
        {
            "id": r[0],
            "run_at": r[1],
            "new_properties": r[2],
            "new_deals": r[3],
            "duration_ms": r[4],
            "notes": r[5],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Stats / health
# ---------------------------------------------------------------------------

def db_stats() -> dict:
    """Return summary counts for health/dashboard endpoints."""
    main_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    wal_path = DB_PATH.with_suffix(".db-wal")
    wal_size = wal_path.stat().st_size if wal_path.exists() else 0
    total_kb = round((main_size + wal_size) / 1024, 1)
    return {
        "properties": count_properties(),
        "deals": count_deals(),
        "offers": count_offers(),
        "db_path": str(DB_PATH),
        "db_size_kb": total_kb,
    }
