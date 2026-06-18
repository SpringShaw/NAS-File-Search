import os
import sqlite3
from .config import DB_PATH


def get_db():
    """Get a synchronous sqlite3 connection with row_factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database tables."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS dirs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            exclude_dirs TEXT DEFAULT '',
            min_size INTEGER DEFAULT 0,
            max_size INTEGER DEFAULT 0,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dir_id INTEGER,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            file_ext TEXT,
            file_size INTEGER DEFAULT 0,
            file_type TEXT DEFAULT '其他',
            has_fulltext INTEGER DEFAULT 0,
            modified_time REAL DEFAULT 0,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dir_id) REFERENCES dirs(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_files_filename ON files(file_name);
        CREATE INDEX IF NOT EXISTS idx_files_ext ON files(file_ext);
        CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);
        CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);
        CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size);

        CREATE TABLE IF NOT EXISTS index_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_files INTEGER DEFAULT 0,
            fulltext_files INTEGER DEFAULT 0,
            last_rebuild TIMESTAMP,
            is_indexing INTEGER DEFAULT 0,
            progress REAL DEFAULT 0,
            current_file TEXT DEFAULT '',
            error TEXT DEFAULT ''
        );

        INSERT OR IGNORE INTO index_status (id, total_files, fulltext_files)
        VALUES (1, 0, 0);
    """)
    db.commit()
    db.close()
