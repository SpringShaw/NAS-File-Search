#!/bin/bash
# NAS-File-Search 裸机运行脚本（无 Docker）
# 构建前端 → 安装后端依赖 → 以裸机模式启动（不做 /nas/host 前缀转换）
set -e

cd "$(dirname "$0")"

# 可通过环境变量覆盖：HOST / PORT / DATA_DIR / API_KEY 等
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8083}"
export DATA_DIR="${DATA_DIR:-$(pwd)/data}"
# 裸机模式：前缀置空，直接使用真实绝对路径
export NAS_HOST_PREFIX=""

echo "🔨 构建前端..."
cd frontend
npm install
npm run build
cd ..

echo "📦 安装后端依赖..."
cd backend
pip install -r requirements.txt
cd ..

echo "🚀 启动服务 (http://${HOST}:${PORT}, DATA_DIR=${DATA_DIR})"
cd backend
exec uvicorn app.main:app --host "$HOST" --port "$PORT"
