import os
import time
import threading
import logging
from datetime import datetime

from .config import (
    FILE_CATEGORIES, TEXT_EXTENSIONS, FULLTEXT_MAX_SIZE,
    WHOOSH_INDEX_DIR, THUMBNAIL_DIR, THUMBNAIL_SIZE,
    EXT_TO_CATEGORY, MAX_IMAGE_PIXELS, ensure_dirs,
)
from .models import get_db

logger = logging.getLogger(__name__)


def get_file_category(ext):
    ext_lower = ext.lower().lstrip(".")
    return EXT_TO_CATEGORY.get(ext_lower, "其他")


def get_file_icon(ext):
    cat = get_file_category(ext)
    if cat in FILE_CATEGORIES:
        return FILE_CATEGORIES[cat]["icon"]
    return "📁"


def read_text_file(filepath, max_size=FULLTEXT_MAX_SIZE):
    """Read text content from a file for fulltext indexing."""
    try:
        size = os.path.getsize(filepath)
        if size > max_size or size == 0:
            return ""
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc, errors="strict") as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return ""
    except Exception:
        return ""


def scan_directory(dir_path, exclude_dirs=None, min_size=0, max_size=0):
    """Walk a directory and yield file info dicts."""
    exclude_set = set()
    if exclude_dirs:
        for d in exclude_dirs.split(","):
            d = d.strip()
            if d:
                exclude_set.add(os.path.normpath(os.path.join(dir_path, d)))

    for root, dirs, files in os.walk(dir_path, followlinks=False):
        norm_root = os.path.normpath(root)
        if any(norm_root.startswith(ex) for ex in exclude_set):
            dirs.clear()
            continue
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for fname in files:
            if fname.startswith("."):
                continue
            filepath = os.path.join(root, fname)
            try:
                if not os.path.isfile(filepath):
                    continue
                stat = os.stat(filepath)
                if min_size > 0 and stat.st_size < min_size:
                    continue
                if max_size > 0 and stat.st_size > max_size:
                    continue
                _, ext = os.path.splitext(fname)
                ext = ext.lower().lstrip(".")
                yield {
                    "dir_id": None,  # set by caller
                    "file_path": filepath,
                    "file_name": fname,
                    "file_ext": ext,
                    "file_size": stat.st_size,
                    "file_type": get_file_category(ext),
                    "has_fulltext": 1 if ext in TEXT_EXTENSIONS else 0,
                    "modified_time": stat.st_mtime,
                }
            except (OSError, PermissionError):
                continue


def generate_thumbnail(filepath, thumbnail_path):
    """Generate a thumbnail for image files."""
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS  # 防解压炸弹
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        with Image.open(filepath) as img:
            # 再次校验尺寸，拒绝异常大图
            if img.width * img.height > MAX_IMAGE_PIXELS:
                logger.warning(f"Image too large, skip thumbnail: {filepath}")
                return False
            img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumbnail_path, "JPEG", quality=85)
        return True
    except Exception as e:
        logger.warning(f"Thumbnail generation failed for {filepath}: {e}")
        return False


class Indexer:
    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None

    def _is_indexing(self):
        db = get_db()
        row = db.execute("SELECT is_indexing FROM index_status WHERE id = 1").fetchone()
        db.close()
        return row and row["is_indexing"] == 1

    def start_rebuild(self):
        with self._lock:
            if self._is_indexing():
                return False, "索引正在进行中"
            db = get_db()
            db.execute(
                "UPDATE index_status SET is_indexing = 1, progress = 0, current_file = '', error = '' WHERE id = 1"
            )
            db.commit()
            db.close()

        self._thread = threading.Thread(target=self._rebuild_index, daemon=True)
        self._thread.start()
        return True, "索引重建已开始"

    def _rebuild_index(self):
        try:
            self._do_rebuild()
        except Exception as e:
            logger.exception("Index rebuild failed")
            try:
                db = get_db()
                db.execute("UPDATE index_status SET is_indexing = 0, error = ? WHERE id = 1", (str(e),))
                db.commit()
                db.close()
            except Exception:
                logger.exception("Failed to update error status")

    def _do_rebuild(self):
        from .search import rebuild_whoosh_index

        db = get_db()
        db.execute("DELETE FROM files")

        dirs = db.execute("SELECT * FROM dirs WHERE enabled = 1").fetchall()

        all_files = []
        for d in dirs:
            for f in scan_directory(d["path"], d["exclude_dirs"] or "", d["min_size"] or 0, d["max_size"] or 0):
                f["dir_id"] = d["id"]
                all_files.append(f)

        total = len(all_files)

        for i, f in enumerate(all_files):
            db.execute(
                """INSERT OR REPLACE INTO files
                   (dir_id, file_name, file_path, file_ext, file_size, file_type, has_fulltext, modified_time, indexed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (f["dir_id"], f["file_name"], f["file_path"], f["file_ext"],
                 f["file_size"], f["file_type"], f["has_fulltext"], f["modified_time"])
            )

            progress = (i + 1) / total * 100 if total > 0 else 100
            db.execute(
                "UPDATE index_status SET progress = ?, current_file = ? WHERE id = 1",
                (progress, f["file_name"])
            )

            if (i + 1) % 500 == 0:
                db.commit()

        # Count fulltext files
        fulltext_count = db.execute("SELECT COUNT(*) FROM files WHERE has_fulltext = 1").fetchone()[0]

        db.execute(
            """UPDATE index_status SET
               total_files = ?, fulltext_files = ?,
               last_rebuild = datetime('now'),
               is_indexing = 0, progress = 100, current_file = '', error = ''
               WHERE id = 1""",
            (total, fulltext_count)
        )
        db.commit()
        db.close()

        # Rebuild whoosh fulltext index (best effort)
        try:
            rebuild_whoosh_index()
        except Exception as e:
            logger.warning(f"Whoosh index rebuild failed (non-fatal): {e}")

        # 清理旧缩略图缓存（重建后文件路径可能变化，旧缓存失效）
        try:
            for name in os.listdir(THUMBNAIL_DIR):
                p = os.path.join(THUMBNAIL_DIR, name)
                if os.path.isfile(p):
                    os.remove(p)
        except OSError as e:
            logger.warning(f"Failed to clean thumbnail cache: {e}")

        logger.info(f"Index rebuild complete: {total} files, {fulltext_count} fulltext")

    def get_status(self):
        db = get_db()
        row = db.execute("SELECT * FROM index_status WHERE id = 1").fetchone()
        db.close()
        if row:
            return {
                "total_files": row["total_files"],
                "fulltext_files": row["fulltext_files"],
                "last_rebuild": row["last_rebuild"],
                "is_indexing": bool(row["is_indexing"]),
                "progress": row["progress"],
                "current_file": row["current_file"],
                "error": row["error"],
            }
        return {
            "total_files": 0, "fulltext_files": 0, "last_rebuild": None,
            "is_indexing": False, "progress": 0, "current_file": "", "error": "",
        }


indexer = Indexer()
