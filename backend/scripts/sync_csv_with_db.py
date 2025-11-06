#!/usr/bin/env python3
"""
Sync CSV files with the current database state (messages and groups tables).

Usage:
  python3 scripts/sync_csv_with_db.py

This will overwrite the CSVs under PATHS['csv'] with fresh exports:
  - all_messages.csv
  - tech_jobs.csv (from messages.job_type)
  - non_tech_jobs.csv (from messages.job_type)
  - freelance_jobs.csv (from messages.job_type)
  - joined_groups.csv

Backup: Creates timestamped backups of existing CSVs before overwriting.
"""
import os
import sys
import csv
import sqlite3
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PATHS, DATABASE


def backup_file(path: str) -> None:
    if os.path.exists(path):
        ts = int(datetime.now().timestamp())
        backup_path = f"{path}.backup.{ts}.csv"
        os.replace(path, backup_path)


def export_query_to_csv(conn: sqlite3.Connection, query: str, out_path: str) -> int:
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    # Backup then write
    backup_file(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    db_path = os.path.join(PATHS["database"], DATABASE["name"])
    csv_dir = PATHS["csv"]

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)

    print("============================================================")
    print("🔄 Sync CSV with Database")
    print("============================================================\n")

    # 1) all_messages.csv
    all_messages_q = """
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages
        ORDER BY date DESC
    """
    count_all = export_query_to_csv(conn, all_messages_q, os.path.join(csv_dir, "all_messages.csv"))
    print(f"✅ all_messages.csv updated: {count_all} rows")

    # 2) tech_jobs.csv (from messages.job_type)
    tech_q = """
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages
        WHERE job_type LIKE '%tech%' AND job_type NOT LIKE '%non_tech%'
        ORDER BY date DESC
    """
    count_tech = export_query_to_csv(conn, tech_q, os.path.join(csv_dir, "tech_jobs.csv"))
    print(f"✅ tech_jobs.csv updated: {count_tech} rows")

    # 3) non_tech_jobs.csv
    non_tech_q = """
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages
        WHERE job_type = 'non_tech'
        ORDER BY date DESC
    """
    count_non = export_query_to_csv(conn, non_tech_q, os.path.join(csv_dir, "non_tech_jobs.csv"))
    print(f"✅ non_tech_jobs.csv updated: {count_non} rows")

    # 4) freelance_jobs.csv (includes freelance_tech, etc.)
    freelance_q = """
        SELECT message_id, group_name, group_link, sender, date, message_text,
               keywords_found, account_used, job_type
        FROM messages
        WHERE job_type LIKE '%freelance%'
        ORDER BY date DESC
    """
    count_free = export_query_to_csv(conn, freelance_q, os.path.join(csv_dir, "freelance_jobs.csv"))
    print(f"✅ freelance_jobs.csv updated: {count_free} rows")

    # 5) joined_groups.csv
    groups_q = """
        SELECT group_name, group_link, join_date
        FROM groups
        WHERE join_date IS NOT NULL
        ORDER BY join_date DESC
    """
    count_groups = export_query_to_csv(conn, groups_q, os.path.join(csv_dir, "joined_groups.csv"))
    print(f"✅ joined_groups.csv updated: {count_groups} rows")

    conn.close()

    print("\n============================================================")
    print("✅ CSV sync complete!")
    print("============================================================")


if __name__ == "__main__":
    main()



