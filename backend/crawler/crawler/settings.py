import os

BOT_NAME = "crawler"
SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# 反爬设置
ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1          # 请求间隔（秒）
DEPTH_LIMIT = 4             # 爬取深度：0=起始页，1=一级链接，2=二级链接
CLOSESPIDER_PAGECOUNT = 100 # 每次任务最多爬取 100 页，防止 Wikipedia 类站点无限扩散

# 启用 Pipeline
ITEM_PIPELINES = {
   "crawler.pipelines.DatabasePipeline": 300,
}

# 数据库配置：优先读取环境变量，本地开发回退到 127.0.0.1
MYSQL_SETTINGS = {
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root102'),
    'db': os.getenv('MYSQL_DB', 'crawler_db'),
    'charset': 'utf8mb4'
}

MONGO_SETTINGS = {
    'uri': os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017/'),
    'db_name': 'crawler_db'
}

# 解决高版本 Scrapy 异步报错
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# 只保留 WARNING 及以上，屏蔽 Scrapy/pymongo 的 DEBUG/INFO 噪音
LOG_LEVEL = "WARNING"