# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# from scrapy import Field, Item
from dataclasses import dataclass, field, Field
import logging
from datetime import datetime
from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader


class TakeFirstLoader(ItemLoader):
    default_output_processor = TakeFirst()


_Username = str
_OrganizationName = str

# Item example
# class AccountItem(Item):
#     username = Field()
#     avatar = Field()
#     link = Field()
#     location = Field()
#     organizations = Field(serializer=list)
#     repositories = Field(serializer=list)
#     followers = Field()
#     following = Field()
#     joined = Field()


from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class AccountItem:
    url: str
    username: _Username
    avatar: str
    joined: datetime | str = field(metadata={'format': "%b %d, %Y"})
    link: str | None = None
    location: str | None = None
    # organizations: list['OrganizationItem'] = field(default_factory=list)
    # repositories: list['RepositoryItem'] = field(default_factory=list)
    followers: int | str = 0
    following: int | str = 0
    # What?!?!
    # password: str | None = field(default=None)


@dataclass(slots=True)
class OrganizationItem:
    url: str | None = None
    joined: datetime | str | None = field(metadata={'format': "%b %d, %Y"}, default=None)
    name: _OrganizationName | None = None
    icon: str | None = None
    description: str | None = None
    link: str | None = None
    location: str | None = None
    persons: list[_Username] = field(default_factory=list)


@dataclass(slots=True)
class RepositoryItem:
    url: str
    owner: _Username | _OrganizationName | None
    title: str
    last_updated: datetime | str  = field(metadata={"format": "%a, %d %b %Y %H:%M:%S %Z"})
    stars: int | str = 0
    branches: int | str = 0
    description: str | None = None
    commits: int | str = 1
    releases: int | str = 0
    issues: int | str = 0

# @dataclass(slots=True)
# class RawAccountItem(AccountItem):
#     followers: str | None = field(default=None) # type: ignore
#     following: str | None = field(default=None) # type: ignore
#     joined: str | None = field(default=None) # type: ignore
