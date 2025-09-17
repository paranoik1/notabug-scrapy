# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Item, Spider
from scrapy.exceptions import DropItem

from .items import AccountItem


class NotabugPipeline:
    def __init__(self) -> None:
        self.accounts_parsed: set[str] = set()

    def process_item(self, item: AccountItem, spider: Spider):
        username: str = item.get("username", "")
        if username in self.accounts_parsed:
            raise DropItem("Duplicate account username found: " + username)

        for field in item.fields:
            item.setdefault(field, None)

        spider.logger.info(item)
        self.accounts_parsed.add(username)

        return item
