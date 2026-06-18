import os
import shutil
import logging

from whoosh import index as whoosh_index
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.analysis import SimpleAnalyzer

from .config import WHOOSH_INDEX_DIR, TEXT_EXTENSIONS, FULLTEXT_MAX_SIZE, ensure_dirs
from .models import get_db
from .indexer import read_text_file, get_file_category, get_file_icon

logger = logging.getLogger(__name__)

SCHEMA = Schema(
    path=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=SimpleAnalyzer()),
    content=TEXT(stored=False, analyzer=SimpleAnalyzer()),
    file_type=KEYWORD(stored=True),
    file_ext=KEYWORD(stored=True),
)


def _get_whoosh_index():
    ensure_dirs()
    if whoosh_index.exists_in(WHOOSH_INDEX_DIR):
        return whoosh_index.open_dir(WHOOSH_INDEX_DIR)
    return whoosh_index.create_in(WHOOSH_INDEX_DIR, SCHEMA)


def rebuild_whoosh_index():
    """Rebuild the Whoosh fulltext index from SQLite."""
    ensure_dirs()
    try:
        if os.path.exists(WHOOSH_INDEX_DIR):
            shutil.rmtree(WHOOSH_INDEX_DIR, ignore_errors=True)
            import time
            time.sleep(0.5)
    except Exception as e:
        logger.warning(f"Failed to remove old index: {e}")

    ix = whoosh_index.create_in(WHOOSH_INDEX_DIR, SCHEMA)
    writer = ix.writer()

    db = get_db()
    files = db.execute(
        "SELECT file_path, file_name, file_ext, file_type, has_fulltext FROM files WHERE has_fulltext = 1"
    ).fetchall()
    db.close()

    count = 0
    for f in files:
        content = read_text_file(f["file_path"])
        if content:
            try:
                writer.add_document(
                    path=f["file_path"],
                    name=f["file_name"],
                    content=content,
                    file_type=f["file_type"],
                    file_ext=f["file_ext"],
                )
                count += 1
            except Exception as e:
                logger.warning(f"Failed to index {f['file_path']}: {e}")

    writer.commit()
    logger.info(f"Whoosh index rebuilt: {count} documents")


def search_files(query: str, file_type: str = "all", page: int = 1, size: int = 20):
    """Search files by name (SQLite) and content (Whoosh)."""
    db = get_db()
    offset = (page - 1) * size
    like_q = f"%{query}%"

    # --- Filename search in SQLite ---
    where = "WHERE (file_name LIKE ? OR file_path LIKE ?)"
    params = [like_q, like_q]
    if file_type and file_type != "all":
        where += " AND file_type = ?"
        params.append(file_type)

    total = db.execute(f"SELECT COUNT(*) as cnt FROM files {where}", params).fetchone()["cnt"]
    rows = db.execute(
        f"SELECT * FROM files {where} ORDER BY file_name LIMIT ? OFFSET ?",
        params + [size, offset]
    ).fetchall()

    results = []
    seen = set()
    for row in rows:
        seen.add(row["file_path"])
        results.append({
            "id": row["id"],
            "file_name": row["file_name"],
            "file_path": row["file_path"],
            "file_size": row["file_size"],
            "file_type": row["file_type"],
            "file_ext": row["file_ext"],
            "modified_time": row["modified_time"],
            "icon": get_file_icon(row["file_ext"]),
            "is_image": get_file_category(row["file_ext"]) == "图片",
            "snippet": "",
        })

    # --- Whoosh fulltext search ---
    try:
        ix = _get_whoosh_index()
        with ix.searcher() as searcher:
            parser = MultifieldParser(["name", "content"], schema=ix.schema, group=OrGroup)
            whoosh_query = parser.parse(query)
            whoosh_results = searcher.search(whoosh_query, limit=50)
            for hit in whoosh_results:
                if hit["path"] not in seen:
                    seen.add(hit["path"])
                    # Get from DB
                    info = db.execute("SELECT * FROM files WHERE file_path = ?", (hit["path"],)).fetchone()
                    snippet = ""
                    try:
                        snippet = hit.highlights("content", top=3) or ""
                    except Exception:
                        pass
                    if info:
                        results.append({
                            "id": info["id"],
                            "file_name": info["file_name"],
                            "file_path": info["file_path"],
                            "file_size": info["file_size"],
                            "file_type": info["file_type"],
                            "file_ext": info["file_ext"],
                            "modified_time": info["modified_time"],
                            "icon": get_file_icon(info["file_ext"]),
                            "is_image": get_file_category(info["file_ext"]) == "图片",
                            "snippet": snippet,
                        })
    except Exception as e:
        logger.warning(f"Whoosh search failed: {e}")

    db.close()

    # Paginate merged results
    merged = results[offset:offset + size]
    return {
        "results": merged,
        "total": len(results),
        "page": page,
        "size": size,
    }
