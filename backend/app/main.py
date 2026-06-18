import os
import hashlib
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from .config import ensure_dirs, THUMBNAIL_DIR, FILE_CATEGORIES, HOST, PORT, NAS_HOST_PREFIX
from .models import init_db, get_db
from .indexer import indexer, generate_thumbnail, get_file_icon, get_file_category
from .search import search_files

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="NAS-File-Search", version="1.0.0")


@app.on_event("startup")
async def startup():
    ensure_dirs()
    init_db()
    logger.info("NAS-File-Search started")


# --- Pydantic Models ---

class DirCreate(BaseModel):
    path: str
    exclude_dirs: str = ""
    min_size: int = 0
    max_size: int = 0


# --- API Routes ---

@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1),
    type: str = Query("all"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return search_files(q, type, page, size)


@app.get("/api/stats")
async def api_stats():
    db = get_db()
    row = db.execute("SELECT * FROM index_status WHERE id = 1").fetchone()
    dirs_count = db.execute("SELECT COUNT(*) as cnt FROM dirs WHERE enabled = 1").fetchone()["cnt"]
    type_stats = db.execute(
        "SELECT file_type, COUNT(*) as cnt, SUM(file_size) as total_size FROM files GROUP BY file_type ORDER BY cnt DESC"
    ).fetchall()
    db.close()

    return {
        "total_files": row["total_files"] if row else 0,
        "fulltext_files": row["fulltext_files"] if row else 0,
        "last_rebuild": row["last_rebuild"] if row else None,
        "is_indexing": bool(row["is_indexing"]) if row else False,
        "progress": row["progress"] if row else 0,
        "current_file": row["current_file"] if row else "",
        "dirs_count": dirs_count,
        "type_distribution": [
            {"type": t["file_type"], "count": t["cnt"], "total_size": t["total_size"] or 0}
            for t in type_stats
        ],
    }


@app.get("/api/dirs")
async def api_get_dirs():
    db = get_db()
    rows = db.execute("SELECT * FROM dirs ORDER BY id").fetchall()
    db.close()
    return [
        {
            "id": r["id"],
            "path": r["path"],
            "exclude_dirs": r["exclude_dirs"],
            "min_size": r["min_size"],
            "max_size": r["max_size"],
            "enabled": bool(r["enabled"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def to_container_path(host_path: str) -> str:
    """将宿主机路径转换为容器内路径，自动添加 /nas/host 前缀。"""
    host_path = host_path.strip()
    if not host_path:
        return host_path
    # 已经是容器路径的直接返回
    if host_path.startswith(NAS_HOST_PREFIX):
        return host_path
    # 以 / 开头但没有 /nas/host 前缀的，自动添加
    if host_path.startswith("/"):
        return NAS_HOST_PREFIX + host_path
    return host_path


@app.post("/api/dirs")
async def api_add_dir(dir_data: DirCreate):
    container_path = to_container_path(dir_data.path)
    if not os.path.isdir(container_path):
        raise HTTPException(status_code=400, detail=f"目录不存在: {dir_data.path}")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO dirs (path, exclude_dirs, min_size, max_size) VALUES (?, ?, ?, ?)",
            (container_path, dir_data.exclude_dirs, dir_data.min_size, dir_data.max_size),
        )
        db.commit()
        new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()
        return {"id": new_id, "path": container_path, "message": "目录已添加"}
    except Exception as e:
        db.close()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/dirs/{dir_id}")
async def api_delete_dir(dir_id: int):
    db = get_db()
    existing = db.execute("SELECT id FROM dirs WHERE id = ?", (dir_id,)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(status_code=404, detail="目录不存在")
    db.execute("DELETE FROM dirs WHERE id = ?", (dir_id,))
    db.execute("DELETE FROM files WHERE dir_id = ?", (dir_id,))
    db.commit()
    db.close()
    return {"message": "目录已删除"}


@app.post("/api/index/rebuild")
async def api_rebuild_index():
    success, msg = indexer.start_rebuild()
    if success:
        return {"message": msg}
    raise HTTPException(status_code=409, detail=msg)


@app.get("/api/index/status")
async def api_index_status():
    return indexer.get_status()


@app.get("/api/thumbnail")
async def api_thumbnail(path: str):
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="文件不存在")
    path_hash = hashlib.md5(path.encode()).hexdigest()
    thumb_path = os.path.join(THUMBNAIL_DIR, f"{path_hash}.jpg")
    if not os.path.exists(thumb_path):
        success = generate_thumbnail(path, thumb_path)
        if not success:
            raise HTTPException(status_code=400, detail="无法生成缩略图")
    return FileResponse(thumb_path, media_type="image/jpeg")


@app.get("/api/file-types")
async def api_file_types():
    return {cat: {"icon": info["icon"], "extensions": list(info["extensions"])} for cat, info in FILE_CATEGORIES.items()}


# --- Static Files & SPA ---

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    static_file = os.path.join(STATIC_DIR, full_path)
    if full_path and os.path.isfile(static_file):
        return FileResponse(static_file)
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
