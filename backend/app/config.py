import os

DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
DB_PATH = os.path.join(DATA_DIR, "searcher.db")
WHOOSH_INDEX_DIR = os.path.join(DATA_DIR, "whoosh_index")
THUMBNAIL_DIR = os.path.join(DATA_DIR, "thumbnails")

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8083"))

# --- 安全配置 ---
# API Key 认证（可选）：留空则不启用认证，适合纯内网/已有反向代理鉴权的场景；
# 配置后所有 /api/* 请求需携带 X-API-Key 请求头。公网部署强烈建议设置一个长随机串。
API_KEY = os.environ.get("API_KEY", "").strip()
# 速率限制：每个 IP 在 RATE_WINDOW 秒内最多 RATE_LIMIT 次 /api 请求；0 表示禁用
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "120"))
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "60"))
# 缩略图防解压炸弹：允许处理的图片像素数上限
MAX_IMAGE_PIXELS = 25_000_000

THUMBNAIL_SIZE = (200, 200)
FULLTEXT_MAX_SIZE = 5 * 1024 * 1024  # 5MB max for fulltext indexing
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 宿主机根目录前缀。Docker 部署时为 /nas/host（宿主机 / 挂载到容器该路径）；
# 裸机部署时设为空字符串，直接使用真实绝对路径，不做前缀转换。
NAS_HOST_PREFIX = os.environ.get("NAS_HOST_PREFIX", "/nas/host").strip()

TEXT_EXTENSIONS = {
    "txt", "log", "md", "py", "js", "ts", "jsx", "tsx",
    "sh", "bash", "pl", "json", "yaml", "yml", "csv",
    "html", "css", "xml", "sql", "conf", "cfg", "ini",
    "toml", "env", "go", "java", "c", "cpp", "h", "hpp",
    "rs", "rb", "php", "lua", "r", "swift", "kt", "scala",
    "vue", "svelte", "mdx", "rst", "tex",
}

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "heic", "heif", "tiff", "svg"}
VIDEO_EXTENSIONS = {"mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"}
DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp"}
LOG_EXTENSIONS = {"log"}
SCRIPT_EXTENSIONS = {"py", "js", "ts", "sh", "bash", "pl", "rb", "go", "java", "php"}
ARCHIVE_EXTENSIONS = {"zip", "tar", "gz", "rar", "7z", "bz2", "xz"}
AUDIO_EXTENSIONS = {"mp3", "flac", "wav", "ogg", "aac", "wma", "m4a"}

# Category definitions: { category_name: { "icon": emoji, "extensions": set } }
FILE_CATEGORIES = {
    "图片": {"icon": "🖼️", "extensions": IMAGE_EXTENSIONS},
    "视频": {"icon": "🎬", "extensions": VIDEO_EXTENSIONS},
    "文档": {"icon": "📄", "extensions": DOCUMENT_EXTENSIONS},
    "日志": {"icon": "📋", "extensions": LOG_EXTENSIONS},
    "脚本": {"icon": "📜", "extensions": SCRIPT_EXTENSIONS},
    "压缩包": {"icon": "📦", "extensions": ARCHIVE_EXTENSIONS},
    "音频": {"icon": "🎵", "extensions": AUDIO_EXTENSIONS},
}

# Build reverse lookup: ext -> category
EXT_TO_CATEGORY = {}
for _cat, _info in FILE_CATEGORIES.items():
    for _ext in _info["extensions"]:
        EXT_TO_CATEGORY[_ext] = _cat


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WHOOSH_INDEX_DIR, exist_ok=True)
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
