


这份 `api.md` 文档主要为 A 同学（后端）和 B 同学（前端/爬虫）在 MVP（最小可行产品）阶段的联调提供统一的标准。文档重点规范了全局响应格式、参数命名规范（统一使用 `snake_case` 下划线命名）以及核心业务流程的接口契约。

---

# 爬虫管理系统 MVP 阶段 API 接口文档

**版本**: v1.0.0 (MVP)
**基础路径 (Base URL)**: `http://localhost:8000/api`
**数据格式**: `application/json`

## 一、 全局规范

### 1. 统一响应格式
所有的接口响应必须被包装在以下统一的 JSON 结构中。前端 B 同学在拿到 Axios 响应后，应先判断 `code` 是否为 `0`。

```json
{
  "code": 0,           // 业务状态码：0 表示成功，非 0 表示各类失败
  "message": "success",// 提示信息：成功时为 "success" 或具体提示语，失败时为错误原因
  "data": { ... }      // 实际的数据载荷，如果为空可以返回 null 或 {}
}
```

### 2. 分页数据规范
凡是涉及列表返回（如任务列表、内容列表），`data` 内部的结构统一如下：

```json
"data": {
  "total": 100,       // 总记录数（用于前端渲染分页组件）
  "page": 1,          // 当前页码
  "page_size": 20,    // 每页条数
  "items": [ ... ]    // 当前页的数据数组
}
```

### 3. 时间格式
统一使用 ISO 8601 格式字符串，例如：`"2026-04-27T17:00:00Z"`，前端使用对应的时间库（如 Day.js 或直接写过滤器）进行格式化显示。

---

## 二、 核心业务接口

### 1. 提交爬取任务
- **接口地址**: `POST /tasks`
- **接口说明**: 前端提交需要爬取的起始 URL，后端写入 MySQL 后触发异步爬虫，立即返回任务 ID。
- **请求载荷 (Body)**:
  ```json
  {
    "target_url": "https://example.com/news"  // 必填，目标网址
  }
  ```
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "任务创建成功",
    "data": {
      "task_id": 1,          // 刚创建的任务 ID
      "status": "pending"    // 初始状态
    }
  }
  ```

### 2. 获取任务列表 (含状态轮询)
- **接口地址**: `GET /tasks`
- **接口说明**: 分页获取任务列表。前端可设置定时器（如每 5 秒）调用此接口刷新第一页的任务状态。
- **Query 参数**:
  - `page`: int (可选，默认 1)
  - `page_size`: int (可选，默认 10)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "total": 12,
      "page": 1,
      "page_size": 10,
      "items":[
        {
          "id": 1,
          "target_url": "https://example.com/news",
          "status": "running",       // 状态枚举: pending(排队中), running(执行中), done(已完成), failed(失败)
          "created_at": "2026-04-27T17:00:00Z",
          "finished_at": null,       // 未完成时为 null
          "error_msg": ""            // 若失败，这里会附带报错信息
        }
      ]
    }
  }
  ```

### 3. 检索内容列表 (整合 MySQL与 MongoDB)
- **接口地址**: `GET /contents`
- **接口说明**: 检索爬取成功的网页数据。后端 A 同学需要在此接口内部整合 MySQL 的网页元信息和 MongoDB 的正文/图片数据。
- **Query 参数**:
  - `keyword`: string (可选，正文搜索关键字)
  - `page`: int (可选，默认 1)
  - `page_size`: int (可选，默认 10)
- **成功响应**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "total": 42,
      "page": 1,
      "page_size": 10,
      "items":[
        {
          "webpage_id": 101,                           // MySQL中的主键ID
          "title": "测试新闻标题",                        // 取自 MySQL
          "url": "https://example.com/news/1",         // 取自 MySQL
          "text_content": "这是网页正文的开始部分...",       // 取自 MongoDB (注意字段对齐：叫 text_content)
          "images":[                                  // 为了 MVP 简化，前端无需单独查图片接口，后端直接将该网页关联的图片 URL 数组整合返回
            "https://example.com/img/1.jpg",
            "https://example.com/img/2.jpg"
          ],
          "crawl_time": "2026-04-27T17:05:00Z"         // 取自 MySQL
        }
      ]
    }
  }
  ```

---

## 三、 联调开发须知

1. **跨域问题 (CORS)**：
   - A 同学 (后端) 必须在 FastAPI 中配置 `CORSMiddleware`，允许前端（通常是 `http://localhost:5173` 等）跨域访问。
2. **字段对齐特别说明**：
   - 前后端统一采用 **蛇形命名法 (snake_case)** 进行数据传递（例如 `text_content` 而不是 `textContent`）。B 同学在 Vue 前端绑定数据时请注意 `item.text_content`。
3. **空值处理**：
   - 如果某个页面没有爬到图片，后端 A 同学返回的 `images` 字段应为 `
