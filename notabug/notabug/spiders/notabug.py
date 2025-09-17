import scrapy
from ..items import AccountItem, OrganizationItem, RepositoryItem
from scrapy.http.response.html import HtmlResponse


class NotabugSpider(scrapy.Spider):
    name = "notabug"
    allowed_domains = ["notabug.org"]
    start_urls = ["https://notabug.org/explore/users"]

    def parse(self, response: HtmlResponse): # type: ignore
        user_profiles = response.css("div.user > div.item a")
        yield from response.follow_all(user_profiles, callback=self.parse_user_profile)

        next_url = response.css(".borderless > a::attr(href)").getall()[-1]
        yield response.follow(next_url, callback=self.parse) # type: ignore

    def parse_user_profile(self, response):
        profile = response.css("div.ui.card")[0]
        extra_content = profile.css("div.extra.content")[0]

        avatar = profile.css("span.image > img::attr(src)").get()
        if avatar.startswith("/"):
            avatar = response.urljoin(avatar)

        user_profile = AccountItem(
            avatar=avatar, 
            username=profile.css("span.username::text").get(),
            repositories=[],
            organizations=[]
        )

        for li in extra_content.css("li"):
            i_attr_class = li.css("i::attr(class)").get()
            if i_attr_class is None:
                for link in li.css("a"):
                    organization = OrganizationItem(
                        icon=response.urljoin(link.css("img::attr(src)").get()),
                        link=response.urljoin(link.css("::attr(href)").get()),
                    )
                    user_profile["organizations"].append(organization)
                continue

            match i_attr_class.split()[-1]:
                case "octicon-clock":
                    user_profile["joined"] = li.css("::text").get().strip()
                case "octicon-person":
                    person = li.css("a::text").getall()
                    user_profile["followers"] = int(person[0].strip().split()[0])
                    user_profile["following"] = int(person[1].strip().split()[0])
                case "octicon-link":
                    user_profile["link"] = li.css("a::text").get().strip()
                case "octicon-location":
                    user_profile["location"] = li.css("::text").get().strip()

            for repo in self.parse_repositories(response):
                user_profile["repositories"].append(repo)
        
        for link in ["/following", "/followers"]:
            yield scrapy.Request(response.url + link, self.parse_following_and_followers)

        yield user_profile

    def parse_repositories(self, response):
        for repository in response.css("div.repository > div.item"):
            header = repository.css("div.header > a.name")[0]
            metas = repository.css("div.metas > span.text")

            repo_item = RepositoryItem(
                title=header.css("::text").get(),
                url=response.urljoin(header.css("::attr(href)").get()),
                stars=int(metas[0].css("::text").get().strip()),
                branches=int(metas[1].css("::text").get().strip()),
                last_updated=repository.css("p.time > span::text").get()
            )

            try:
                repo_item["description"] = repository.css("p.has-emoji::text").get()
            except:
                self.logger.error("Не удалось получить описание репозитория: %s", repo_item.url)

            yield repo_item

    def parse_following_and_followers(self, response):
        profiles_links = response.css("ul.list > li.item > a")
        yield from response.follow_all(profiles_links, self.parse_user_profile)

        next_link_list = response.css(".borderless > a").getall()
        if not next_link_list:
            return
        
        next_link = next_link_list[-1]
        self.logger.debug("Next link: %s", next_link)

        if next_link:
            yield response.follow(next_link, callback=self.parse_following_and_followers)

    # def response_is_ban(self, request, response):
    #     return b'banned' in response.body

    # def exception_is_ban(self, request, exception):
    #     return None
