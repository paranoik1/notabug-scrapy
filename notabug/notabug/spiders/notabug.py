from collections.abc import AsyncIterator
from typing import Any, Callable
import scrapy
from scrapy.http.response.html import HtmlResponse
from ..items import OrganizationItem, RepositoryItem, AccountItem, TakeFirstLoader
from urllib.parse import urljoin


class NotabugSpider(scrapy.Spider):
    name = "notabug"
    allowed_domains = ["notabug.org"]
    organization_explore_url = "https://notabug.org/explore/organizations"

    async def start(self) -> AsyncIterator[Any]:
        urls_callbacks = [
            ("https://notabug.org/explore/users", self.explore_accounts),
            (self.organization_explore_url, self.explore_organizations),
            ("https://notabug.org/explore/repos", self.parse_repositories)
        ]

        for url, callback in urls_callbacks:
            yield scrapy.Request(url, callback=callback, dont_filter=True) # type: ignore

    def _follow_next_link(self, response: HtmlResponse, callback: Callable, **kwargs):
        next_link = response.css(".borderless > a:last-child::attr(href)").get()
        if next_link:
            return response.follow(next_link, callback=callback, **kwargs)


    def explore_organizations(self, response):
        for org in response.css("div.ui.list > div.item"):
            url = org.css("span.header > a::attr(href)").get()
            if not url:
                self.logger.critical("Не найден url для организации: " + response.url)
                continue

            name = org.xpath("normalize-space(.//span[@class='header']/text()[last()])").get()
            icon = org.css("img.avatar::attr(src)").get()
            joined = org.xpath("normalize-space(.//div[@class='description']/text()[last()])").get()

            item = OrganizationItem(
                url=response.urljoin(url),
                name=name or url.strip("/"),
                icon=icon,
                joined=joined,
            )
            yield response.follow(url, self.parse_organization_item, cb_kwargs={"item": item})

        yield self._follow_next_link(response, self.explore_organizations)

    def parse_organization_item(self, response: HtmlResponse, item: OrganizationItem):
        loader = TakeFirstLoader(item, response=response)
        loader.add_css("description", "p.desc::text")
        loader.add_css("link", "div.meta i.octicon-link + a::attr(href)")
        loader.add_css("location", "div.meta i.octicon-location + *::text")

        item = loader.load_item()
        item.persons = response.css("div.members > a::attr(href)").getall()
        
        if item.icon and item.icon.startswith("/"):
            item.icon = response.urljoin(item.icon)

        yield from response.follow_all(item.persons, callback=self.parse_account_item) # type: ignore

        yield from self.parse_repositories(response, owner=item.name)

        yield item


    def parse_repositories(self, response: HtmlResponse, owner: str | None = None):
        # open_in_browser(response)

        for repository in response.css("div.repository > div.item"):
            header = repository.css("div.header")[0]
            metas = header.css("div.metas > span.text::text").getall()
            title = header.css("a.name")[0]

            title_text = title.css("::text").get()
            if title_text is None:
                self.logger.critical("Не удалось получить заголовок репозитория: " + response.url)
                continue

            if owner is None:
                # assert " / " in title_text, "В заголовке репозитория нет разделительной черты для получения имени владельца: " + title_text
                if " / " in title_text:
                    owner = title_text.split(" / ")[0]
                else:
                    self.logger.critical("В заголовке репозитория нет разделительной черты для получения имени владельца: " + title_text)

            _href = title.attrib.get("href")
            if _href is None:
                self.logger.critical("Не удалось получить href аттрибут: " + response.url + " " + str(title.attrib))
                continue

            url = response.urljoin(_href)
            last_updated = repository.css("p.time > span.time-since::attr(title)").get()
            if not last_updated:
                self.logger.critical("Не удалось получить last_updated: " + response.url)
                continue

            repo_item = RepositoryItem(
                owner=owner,
                title=title_text,
                url=url,
                stars=metas[0],
                branches=metas[1],
                last_updated=last_updated,
            )

            repo_item.description = repository.css("p.has-emoji::text").get()

            yield response.follow(url, callback=self.parse_repo_item, cb_kwargs={'item': repo_item}) # type: ignore

        yield self._follow_next_link(response, callback=self.parse_repositories, cb_kwargs={"owner": owner})

    def parse_repo_item(self, response: HtmlResponse, item: RepositoryItem):
        git_stats_selector = "#git-stats div.item"
        navbar_selector = ".tabular > a"
        right_menu_selector = "div.labeled"

        loader = TakeFirstLoader(item, response=response)
        loader.add_css("commits", git_stats_selector + ":first-child b::text")
        loader.add_css("releases", git_stats_selector + ":last-child b::text")

        loader.add_css("issues", navbar_selector + ":nth-child(2) > span.label::text")
        loader.add_css("pulls", navbar_selector + ":nth-child(3) > span.label::text")

        loader.add_css("watchers", right_menu_selector + ":nth-child(1) > a:nth-child(2)::text")
        loader.add_css("forks", right_menu_selector + ":nth-child(3) > a:nth-child(2)::text")

        yield loader.load_item()

    def explore_accounts(self, response: HtmlResponse):
        profiles = response.css("div.ui.list > div.item span.header > a")

        yield from response.follow_all(profiles, callback=self.parse_account_item) # type: ignore

        yield self._follow_next_link(response, callback=self.explore_accounts)

    def parse_account_item(self, response: HtmlResponse):  # type: ignore
        profile = response.css("div.ui.card")[0]
        extra_content = profile.css("div.extra.content")[0]

        avatar = profile.css("span.image > img::attr(src)").get("")
        if not avatar:
            self.logger.error("Не удалось получить аватар пользователя: " + response.url)
        elif avatar.startswith("/"):
            avatar = response.urljoin(avatar)

        username = profile.css("span.username::text").get("")
        if not username:
            self.logger.error("Не удалось получить имя пользователя: " + response.url)

        user_profile = AccountItem(
            url=response.url,
            avatar=avatar,
            username=username,
            joined=""
        )

        for li in extra_content.css("li"):
            icon_class = li.css("i::attr(class)").get()
            if not icon_class:
                urls = li.css("a::attr(href)").getall()
                for url in urls:
                    organization_id = url.removeprefix("/")
                    yield response.follow(self.organization_explore_url + "?q=" + organization_id, callback=self.explore_organizations)
                    
                continue

            # Извлекаем последнее слово из класса иконки: "octicon-clock" → "clock"
            icon_name = icon_class.strip().split()[-1].removeprefix("octicon-")

            text = li.xpath("normalize-space(./text()[last()])").get("")
            link_text = li.css("a::text").get()

            match icon_name:
                case "clock":
                    if not text:
                        self.logger.critical("Не удалось получить дату присоединения пользователя: " + response.url)
                        continue
                    user_profile.joined = text
                case "person":
                    person = li.css("a::text").getall()
                    try:
                        user_profile.followers = int(person[0].strip().split()[0])
                        user_profile.following = int(person[1].strip().split()[0])
                    except (ValueError, IndexError):
                        self.logger.error("Не удалось получить кол-во подписчиков/подписок: " + response.url)
                case "octicon-link":
                    user_profile.link = link_text
                case "octicon-location":
                    user_profile.location = link_text

        yield from self.parse_repositories(response, user_profile.username)

        for part_url in ["following", "followers"]:
            if getattr(user_profile, part_url) > 0:
                yield response.follow(
                    urljoin(response.url + "/", part_url), self.parse_following_and_followers
                )
            
        yield user_profile

    def parse_following_and_followers(self, response):
        profiles_links = response.css("ul.list > li.item > a::attr(href)")
        yield from response.follow_all(profiles_links, self.parse_account_item)

        yield self._follow_next_link(response, callback=self.parse_following_and_followers)

    # def response_is_ban(self, request, response):
    #     return b'banned' in response.body

    # def exception_is_ban(self, request, exception):
    #     return None
