"""One-time SQLite migration helper for local V5 databases.

For production, use PostgreSQL + a formal migration tool. This helper exists so
local V5 users can preserve cases while moving to the V5.1 tenant/auth schema.
"""
from __future__ import annotations
import argparse, shutil, sqlite3
from pathlib import Path


def cols(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def add_column(conn, table, ddl):
    name=ddl.split()[0]
    if name not in cols(conn,table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def main():
    ap=argparse.ArgumentParser();ap.add_argument('db',nargs='?',default='qarar.db');ap.add_argument('--tenant',default='migrated-default');ap.add_argument('--subject',default='migration-admin');args=ap.parse_args()
    p=Path(args.db)
    if not p.exists():raise SystemExit(f"Database not found: {p}")
    backup=p.with_suffix(p.suffix+'.v5-backup');shutil.copy2(p,backup)
    conn=sqlite3.connect(p)
    try:
        if 'decision_cases' in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
            add_column(conn,'decision_cases',f"tenant_id VARCHAR(80) NOT NULL DEFAULT '{args.tenant}'")
            add_column(conn,'decision_cases',f"created_by VARCHAR(200) NOT NULL DEFAULT '{args.subject}'")
        if 'knowledge_items' in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
            add_column(conn,'knowledge_items',f"tenant_id VARCHAR(80) NOT NULL DEFAULT '{args.tenant}'")
        if 'automation_runs_v5' in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
            add_column(conn,'automation_runs_v5',f"tenant_id VARCHAR(80) NOT NULL DEFAULT '{args.tenant}'")
            add_column(conn,'automation_runs_v5',"actor VARCHAR(200)")
        conn.execute("""CREATE TABLE IF NOT EXISTS decision_approvals_v51 (
            id INTEGER PRIMARY KEY,
            tenant_id VARCHAR(80) NOT NULL,
            case_id INTEGER NOT NULL,
            option_id VARCHAR(40) NOT NULL,
            decision_owner VARCHAR(200) NOT NULL,
            approved_by VARCHAR(200) NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'approved',
            approved_at DATETIME
        )""")
        conn.commit()
    finally:conn.close()
    print(f"Migration complete. Backup: {backup}")

if __name__=='__main__':main()
