针对“网络数据爬取管理系统”的**最小可行产品（MVP，Minimum Viable Product）**，核心目标是**跑通“提交任务 ➔ 自动爬取 ➔ 存入双库 ➔ 界面展示/检索”的核心业务闭环**。

在 MVP 阶段，可以先暂缓复杂的统计图表、高级过滤、CSV导出以及严格的错误重试机制，优先保障主流程运转。基于报告草稿中的《6.2 人员分工与模块对应》，以下是 A 同学和 B 同学在 MVP 阶段的具体工作清单：

### 🧑‍💻 成员 A（主攻：关系型数据库与后端接口）

**目标**：提供稳定运行的后端 API 服务，支持任务的创建与状态查询，支持前后端的数据交互。

1. **数据库初始化（MySQL）**
   - **建库建表**：编写 SQL 脚本，创建 MVP 最核心的 3 张表：`Website`（网站）、`Webpage`（网页，存标题/URL）、`CrawlTask`（任务表，存目标 URL 和状态）。
   - *（注：MVP 阶段可先简化 `DataSource` 表，重点保证网页基本信息的存储）*
2. **后端基础框架搭建（FastAPI + SQLAlchemy）**
   - 初始化 FastAPI 项目结构，配置 SQLAlchemy 连接 MySQL。
   - 编写对应 MySQL 表的 ORM 模型（Models）。
3. **实现核心 API 接口**
   - **任务接口**：
     - `POST /api/tasks`：接收前端传来的 URL，在 `CrawlTask` 表生成一条 `status='pending'` 的记录，并通过 `BackgroundTasks` 异步调用 B 同学写好的 Scrapy 启动脚本。
     - `GET /api/tasks`：返回爬取任务列表，供前端轮询状态。
   - **内容检索接口**：
     - `GET /api/contents`：连接 MongoDB，实现简单的分页查询和正文关键字模糊匹配（正则），将结果组装为 JSON 返回给前端。
4. **基础设施支持（Docker 选做 / 本地环境）**
   - 如果决定采用 Docker，为 MySQL 和 MongoDB 编写基础的 `docker-compose.yml` 供两人本地开发联调使用；如果时间紧凑，可先让双方在本地安装环境。

---

### 🧑‍💻 成员 B（主攻：爬虫数据抓取与前端界面）

**目标**：实现通用爬虫抓取目标网页数据并正确入库，提供用户可视化的操作界面。

1. **爬虫基础开发（Scrapy）**
   - **Spider 编写**：编写一个能接收外部参数（起始 URL）的通用爬虫。MVP 阶段不需要做太深的链接跟随（配置 depth=1 或仅爬当前页即可）。
   - **解析逻辑**：使用 XPath 或 BeautifulSoup 提取网页的标题（Title）、正文文本（Text）以及页面中的图片链接（Image URLs）。
2. **数据入库管道（Scrapy Pipeline & MongoDB）**
   - 配置 MongoDB 连接。
   - **MySQL Pipeline**：将提取到的网站域名、网页 URL、标题等结构化信息插入 A 同学建好的 MySQL 数据库（使用 pymysql 即可，拿到自增的 `webpage_id`）。
   - **MongoDB Pipeline**：将长文本内容、关键字、图片链接，附带上 `webpage_id`，写入 MongoDB 的 `contents` 和 `images` 集合。
3. **前端 MVP 页面开发（Vue 3 + Element Plus）**
   - **搭建脚手架**：初始化 Vue 3 项目，引入 Element Plus 和 axios。
   - **爬取任务页**：一个输入框（填 URL）+ 一个提交按钮；下方一个表格展示任务列表（调用 A 同学的 `/api/tasks` 接口，可设置简单定时器每 5 秒刷新一次列表）。
   - **内容检索页**：一个搜索框（按关键字）+ 搜索按钮；下方使用列表或卡片展示爬取到的文章标题、部分正文和图片缩略图（调用 A 同学的 `/api/contents` 接口）。

---

### 🤝 双方必须共同完成的“联调”工作（极度重要）

为了让 MVP 顺利跑通，两人需要坐在一起（或线上会议）确认以下事项：

1. **接口字段对齐**：A 明确返回的 JSON 格式（如字段叫 `text_content` 还是 `content`），B 按此格式渲染前端。
2. **爬虫触发机制对接**：确认 A 同学的 FastAPI 后端如何启动 B 同学的 Scrapy 爬虫。
   *最简单的 MVP 方案：A 同学在后台任务中使用 Python 的 `subprocess.Popen(['scrapy', 'crawl', 'general', '-a', f'start_url={url}'])` 调起爬虫。*
3. **联调测试**：找一个简单的测试网页（如新浪新闻、或某个结构简单的博客页面），前端输入 URL -> 后端触发爬虫 -> 爬虫入库 -> 前端刷新出结果，跑通这个“大动脉”。