# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy import Spider
from dataclasses import Field
from .items import AccountItem, RepositoryItem, OrganizationItem
from datetime import datetime
from typing import get_args, get_origin
from types import UnionType


Items = RepositoryItem | AccountItem | OrganizationItem


class ConvertToCorrectTypesPipeline:
    def process_item(self, item: Items, spider: Spider) -> Items:
        fields: dict[str, Field] = item.__dataclass_fields__
        for field_name in item.__slots__:
            value = getattr(item, field_name, None)
            field_obj = fields.get(field_name)

            if not field_obj or value is None:
                continue

            target_type = field_obj.type
            origin_type = get_origin(target_type)
            
            if origin_type:
                match (origin_type):
                    # Если целевой тип - UnionType (str | None или int | str | None и т д)
                    case t if t is UnionType:
                        # Если да, получаем первый тип
                        target_type = get_args(target_type)[0]
                    case _:
                        target_type = origin_type

            # Если уже правильный тип — пропускаем
            if isinstance(value, target_type): # type: ignore
                continue

            # Конвертация для datetime
            if target_type is datetime and isinstance(value, str):
                fmt = field_obj.metadata.get("format")
                if fmt:
                    date = datetime.strptime(value, fmt)
                    setattr(item, field_name, date)
                else:
                    raise ValueError(f"No format specified for datetime field '{field_name}'")
            else:
                # Пробуем сконвертировать в целевой тип
                try:
                    value = target_type(value) # type: ignore
                    setattr(item, field_name, value)
                except Exception as e:
                    raise TypeError(f"Cannot convert {field_name}={value!r} to {target_type}") from e

        return item


class StripStringsPipeline:
    def process_item(self, item: Items, spider: Spider) -> Items:
        for field_name in item.__slots__:
            value = getattr(item, field_name, None)

            if value is not None and isinstance(value, str):
                setattr(item, field_name, value.strip())

        return item


class JoinedCleanPipeline:
    def process_item(self, item: Items, spider: Spider) -> Items:
        if isinstance(item, RepositoryItem): 
            return item
        
        if not isinstance(item.joined, str):
            spider.logger.error("Поле joined не является строкой")
            return item

        joined_splited = item.joined.split()[-3:]
        item.joined = " ".join(joined_splited)

        return item
