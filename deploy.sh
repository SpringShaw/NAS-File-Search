#!/bin/bash
# NAS-File-Search 部署脚本
set -e

echo "🔨 构建前端..."
cd frontend
npm install
npm run build
cd ..

echo "🐳 构建 Docker 镜像..."
sg docker -c "docker compose down 2>/dev/null || true"
sg docker -c "docker compose up -d --build"

echo "✅ 部署完成！访问 http://localhost:8083"
