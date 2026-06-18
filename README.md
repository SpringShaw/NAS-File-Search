# 🔍 NAS-File-Search

一个轻量级的 NAS 全局文件搜索工具，支持文件名搜索、全文内容搜索、多目录配置，自带 Apple 风格 Web 界面。

## 📖 项目背景

NAS 用久了，文件会越攒越多——照片、视频、代码、文档、配置文件，散落在各个目录里。NAS 自带的文件管理器搜索功能普遍很弱，基本只能做文件名精确匹配，想搜文件内容里的关键词根本做不到。而 Windows 上好用的工具如 Everything 又跑不了 NAS。

NAS-File-Search 就是为了解决这个问题做的：一个跑在 Docker 里的 Web 文件搜索引擎，支持文件名 + 全文内容搜索，图片自动出缩略图，手机浏览器也能用。不管文件在哪个目录，搜一下就能找到。

## ✨ 功能特性

- **多目录管理** — Web 界面添加/删除搜索目录，支持排除子目录和文件大小过滤
- **文件名搜索** — 基于 SQLite 的快速文件名模糊匹配
- **全文内容搜索** — 基于 Whoosh 引擎，支持 40+ 种文本文件的内容搜索（代码、配置、文档等）
- **8 大文件分类** — 图片/视频/文档/日志/脚本/压缩包/音频/其他，一键筛选
- **图片缩略图** — 自动生成缩略图预览
- **索引进度实时显示** — 大量文件也不慌，进度一目了然
- **响应式设计** — 桌面和移动端均可正常使用

## 🛠️ 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.11 + FastAPI |
| 搜索 | SQLite（文件名） + Whoosh（全文） |
| 前端 | Vue 3 + Vite + TailwindCSS |
| 部署 | Docker / Docker Compose |

## 🚀 快速开始

### Docker Compose（推荐）

```bash
git clone https://github.com/yourname/nas-searcher.git
cd NAS-File-Search
docker compose up -d --build
```

访问 `http://localhost:8083`

### 本地开发

```bash
# 前端
cd frontend
npm install
npm run dev

# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8083
```

## 📁 项目结构

```
NAS-File-Search/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口 + API 路由
│   │   ├── config.py         # 配置常量（端口、分类、扩展名）
│   │   ├── models.py         # SQLite 数据库模型
│   │   ├── indexer.py        # 文件扫描 + 索引构建
│   │   └── search.py         # 搜索引擎（SQLite + Whoosh）
│   ├── static/               # 前端构建产物
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   ├── services/api.js   # API 封装
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
├── docker-compose.yml
├── Dockerfile
└── deploy.sh
```

## ⚙️ 配置说明

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 8083 | 监听端口 |
| DATA_DIR | /app/data | 数据存储目录（数据库、索引、缩略图） |

Docker 部署时，宿主机根目录 `/` 以只读方式挂载到容器 `/nas/host`，Web 界面中添加目录时使用宿主机原始路径即可，程序会自动转换。

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/search?q=&type=&page=&size= | 搜索文件 |
| GET | /api/stats | 索引统计信息 |
| GET | /api/dirs | 获取目录列表 |
| POST | /api/dirs | 添加搜索目录 |
| DELETE | /api/dirs/{id} | 删除目录 |
| POST | /api/index/rebuild | 触发索引重建 |
| GET | /api/index/status | 索引进度 |
| GET | /api/thumbnail?path= | 获取图片缩略图 |
| GET | /api/file-types | 获取文件分类配置 |

## 📸 截图

> TODO: 添加截图

## 📄 License

MIT
