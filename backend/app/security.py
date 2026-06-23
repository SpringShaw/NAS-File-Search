"""安全相关工具与中间件：路径越界校验、可选 API Key 认证、IP 速率限制。"""
import os
import time
import hmac
import logging
from collections import defaultdict

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import NAS_HOST_PREFIX, API_KEY, RATE_LIMIT, RATE_WINDOW

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 路径越界校验
# ---------------------------------------------------------------------------

def safe_join(base: str, target: str) -> str:
    """将 target 相对 base 拼接并返回 realpath，若越出 base 子树则抛 404。

    用于防止 ``/{full_path}`` 这类静态文件路由的路径遍历（如 ``../../etc/passwd``）。
    """
    real_base = os.path.realpath(base)
    candidate = os.path.realpath(os.path.join(base, target))
    try:
        if os.path.commonpath([real_base, candidate]) != real_base:
            raise HTTPException(status_code=404, detail="Not found")
    except ValueError:
        # 路径位于不同驱动器或无法求公共前缀
        raise HTTPException(status_code=404, detail="Not found")
    return candidate


def assert_within_nas_host(path: str) -> str:
    """校验 path 必须位于 NAS_HOST_PREFIX 子树内，返回 realpath。

    所有可访问宿主机文件内容的接口（如缩略图）都必须先经过该校验，
    防止读取容器内或宿主机根目录以外的任意文件。
    """
    if not path:
        raise HTTPException(status_code=400, detail="路径不能为空")
    root = os.path.realpath(NAS_HOST_PREFIX)
    real = os.path.realpath(path)
    try:
        if os.path.commonpath([root, real]) != root:
            raise HTTPException(status_code=403, detail="路径超出允许范围")
    except ValueError:
        raise HTTPException(status_code=403, detail="路径超出允许范围")
    return real


# ---------------------------------------------------------------------------
# 可选 API Key 认证
# ---------------------------------------------------------------------------

class APIKeyMiddleware(BaseHTTPMiddleware):
    """可选的 API Key 认证中间件。

    当 ``API_KEY`` 环境变量为空时不做任何拦截（向后兼容纯内网部署）；
    配置后，所有 ``/api/`` 开头的请求必须携带匹配的 ``X-API-Key`` 请求头。
    静态前端资源不受影响，以便首次访问时可加载页面并提示输入 Key。
    使用 ``hmac.compare_digest`` 防止时序攻击。
    """

    async def dispatch(self, request, call_next):
        if API_KEY and request.url.path.startswith("/api/"):
            provided = request.headers.get("X-API-Key", "")
            if not hmac.compare_digest(provided, API_KEY):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "无效或缺失的 API Key"},
                )
        return await call_next(request)


# ---------------------------------------------------------------------------
# IP 速率限制（固定窗口，单进程内存计数）
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """对 ``/api/`` 请求做基于客户端 IP 的固定窗口限流。

    单进程部署场景下足够；多 worker 部署时需换用 Redis 等共享存储。
    ``RATE_LIMIT`` 为 0 时禁用。
    """

    def __init__(self, app, limit=RATE_LIMIT, window=RATE_WINDOW):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._hits = defaultdict(list)

    async def dispatch(self, request, call_next):
        if self.limit > 0 and request.url.path.startswith("/api/"):
            ip = request.client.host if request.client else "unknown"
            now = time.monotonic()
            cutoff = now - self.window
            recent = [t for t in self._hits[ip] if t > cutoff]
            self._hits[ip] = recent
            if len(recent) >= self.limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "请求过于频繁，请稍后再试"},
                    headers={"Retry-After": str(self.window)},
                )
            self._hits[ip].append(now)
            # 防止 IP 集合无限增长
            if len(self._hits) > 10000:
                self._cleanup(now)
        return await call_next(request)

    def _cleanup(self, now):
        cutoff = now - self.window
        for ip in list(self._hits.keys()):
            self._hits[ip] = [t for t in self._hits[ip] if t > cutoff]
            if not self._hits[ip]:
                del self._hits[ip]
