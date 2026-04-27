BOT_NAME = "crawler"
SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# 反爬设置
ROBOTSTXT_OBEY = False     # MVP 阶段建议设为 False
DOWNLOAD_DELAY = 1.5       # 请求间隔，防止被封
DEPTH_LIMIT = 1            # 爬取深度限制，防止无限爬取

# 启用 Pipeline
ITEM_PIPELINES = {
   "crawler.pipelines.DatabasePipeline": 300,
}

# 数据库配置 (请根据实际情况修改密码和 host，Docker 环境下 host 通常为 'mysql' 和 'mongo')
MYSQL_SETTINGS = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root102',  # 替换成你的密码
    'db': 'crawler_db',
    'charset': 'utf8mb4'
}

MONGO_SETTINGS = {
    'uri': 'mongodb://127.0.0.1:27017/',
    'db_name': 'crawler_db'
}

# 解决高版本 Scrapy 异步报错
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"