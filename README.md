# Web Crawler System — MVP

一个全栈网页爬虫系统，用户通过浏览器提交目标 URL，后端自动爬取该页面及其一层链接，将结构化元数据存入 MySQL，将正文内容存入 MongoDB，并在前端实时展示爬取结果。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus |
| 后端 | FastAPI + Uvicorn |
| 爬虫 | Scrapy（由后端以子进程方式调用） |
| 关系型数据库 | MySQL 8.0 |
| 文档数据库 | MongoDB 6.0 |
| 部署 | Docker + Docker Compose |

---

## 架构说明

```
浏览器
  │  HTTP /api/*
  ▼
前端容器 (Vite :5173)
  │  反向代理 /api → backend:8000
  ▼
后端容器 (FastAPI :8000)
  ├── POST /api/tasks   → 写入 MySQL，subprocess 启动 Scrapy
  └── GET  /api/contents → 读取 MongoDB

Scrapy（在后端容器内运行）
  ├── 爬取网页元数据   → MySQL  (Website, Webpage, CrawlTask)
  └── 爬取正文 / 图片  → MongoDB (contents, images)
```

### 数据库分工

**MySQL** — 结构化、强一致性数据：
- `CrawlTask`：任务队列，记录 URL、状态（pending / running / finished / failed）、耗时
- `Website`：去重域名表
- `Webpage`：已爬取页面 URL 去重记录

**MongoDB** — 非结构化、高写入量数据：
- `contents`：正文文本、关键词、爬取时间
- `images`：图片 URL、alt 描述、来源页面

---

## 快速启动（Docker）

**前置条件**：已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone <repo-url>
cd database-project
docker compose up --build
```

启动完成后：

| 服务 | 地址 |
|---|---|
| 前端页面 | http://localhost:5173 |
| 后端 API 文档 | http://localhost:8000/docs |
| MySQL | localhost:3306 |
| MongoDB | localhost:27017 |

> 首次启动会拉取镜像并安装依赖，约需 3–5 分钟。后续启动直接 `docker compose up`。

**停止并保留数据：**
```bash
docker compose down
```

**停止并清除所有数据（含数据库 volume）：**
```bash
docker compose down -v
```

---

## 本地开发（不使用 Docker）

### 1. 数据库

确保本地 MySQL（端口 3306）和 MongoDB（端口 27017）已运行，MySQL 中存在数据库 `crawler_db`。

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

本地开发时无需设置任何环境变量，代码中已配置回退默认值 `127.0.0.1`。

---

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/tasks` | 提交爬取任务，body: `{"url": "https://..."}` |
| `GET` | `/api/contents` | 获取最新 50 条爬取内容 |

---

## 项目结构

```
database-project/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI 入口
│   ├── db/
│   │   ├── mysql.py          # SQLAlchemy 连接
│   │   └── mongo.py          # PyMongo 连接
│   ├── models/
│   │   └── CrawlTask.py      # ORM 模型
│   ├── routers/
│   │   ├── tasks.py          # 任务接口
│   │   └── contents.py       # 内容查询接口
│   └── crawler/              # Scrapy 项目
│       └── crawler/
│           ├── settings.py   # 数据库配置（读取环境变量）
│           ├── items.py
│           ├── pipelines.py  # 双写 MySQL + MongoDB
│           └── spiders/
│               └── general_spider.py
└── frontend/
    ├── Dockerfile
    └── src/
        ├── views/
        │   └── HomeView.vue  # 主页面
        └── api/
            └── task.ts       # axios 封装
```

---

## MVP 已知限制

- 爬虫为单进程子进程模式，并发任务会相互竞争资源
- 爬取深度固定为 1 层，不可通过界面配置
- 前端无任务状态轮询，需手动点击「刷新列表」
- 无用户认证，接口完全公开
- 图片数据写入 MongoDB 但前端暂未展示
