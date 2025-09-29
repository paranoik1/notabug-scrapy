from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from notabug.spiders.notabug import NotabugSpider

settings = get_project_settings()
process = CrawlerProcess(settings)

crawl = process.crawl(NotabugSpider)
process.start()
