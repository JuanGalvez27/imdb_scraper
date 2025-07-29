from imdb_scraper.items import MovieItem
from scrapy import Request, Spider, http
from imdb_scraper.loaders import parse_duration
from scrapy_splash import SplashRequest

class Setting:

    main_url = "https://www.imdb.com"
    movies_amount = 50
    main_actors_amount = 3
    custom_cookies = {
        "ad-oo": "0",
        "aws-waf-token": "448399a1-d064-4a46-a3fe-1b02d726bded:EAoAZ91tGcgTAQAA:g5nrWOBUFIR4h9x7oKacJ4Op1zbNyBwNM8YFoAVvINNRmiLCF9ANV9jQWOt/wt+eSw7KvE1h9FvkiVDxVWJYkpdH3OyMp/RunwtoRGLVpBSKlFYPY6VXX/fPAy3vx+9D5QWOmzXoznlF3omB3uWYhVpOcrN9GtTTosLFk1srfbeqnOo4qC+abuYiCkmPxZY=",
        "ci": "eyJpc0dkcHIiOmZhbHNlfQ",
        "csm-hit": "tb:SE5W4FT11KT36SGH8P3T+s-SE5W4FT11KT36SGH8P3T|1753544055796&t:1753544055797&adb:adblk_no",
        "international-seo": "es-ES",
        "session-id": "131-4561504-9943001",
        "session-id-time": "2082787201l",
        "ubid-main": "131-2790063-6133641",
        "XID": "13C2a24d3228de42545dff91753544055",
    }
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.imdb.com/chart/top/",
    }


class PageObject:
    movie_a = "//html/body/div[2]/main/div/div[2]/section/div/div[2]/div/ul/li/div/div/div/div/div[2]/div[1]/a"


class MoviePageObject:
    title = "//html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span//text()"
    release_year = "//html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a//text()"
    rating = "//html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]//text()"
    duration = "//html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]//text()"
    metascore = "//html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/ul/li[3]/a/span/span[1]/span//text()"
    main_actors = "//html/body/div[2]/main/div/section[1]/div/section/div/div[1]/section[4]/div[2]/div[2]/div/div[2]/a//text()"


class MovieSpider(Spider):
    name = "movies"

    start_urls = [Setting.main_url]

    custom_settings = {
        "FEED_URI": "movies.csv",
        "FEED_FORMAT": "csv",
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEED_EXPORT_FIELDS": [
            "title",
            "release_year",
            "rating",
            "duration_minutes",
            "metascore",
            "main_actors",
        ],
    }


    def start_requests(self):
        yield Request(Setting.main_url + "/chart/top/")

    def parse(self, response: http.Response):
        proxy_used = response.meta.get("proxy", "No proxy used")
        self.logger.info(f"Proxy used: {proxy_used}")
        # next_data = response.css("script[id='__NEXT_DATA__']::text").get()
        movies_url = response.xpath(PageObject.movie_a)[:50]
        print(len(movies_url))
        movie_links = [Setting.main_url + a.xpath(".//@href").get() for a in movies_url]
        # print("response.text", response.text)
        print("movie_links", movie_links)

        for url in movie_links:
            yield Request(url, callback=self.parse_movie)

    def parse_movie(self, response: http.Response):
        item = MovieItem()

        title = response.xpath(MoviePageObject.title).get(default="")
        release_year = response.xpath(MoviePageObject.release_year).get(default="")
        rating = response.xpath(MoviePageObject.rating).get(default="")
        duration = parse_duration(response.xpath(MoviePageObject.duration).get(default=""))
        metascore = response.xpath(MoviePageObject.metascore).get(default="")
        actors = response.xpath(MoviePageObject.main_actors).getall()[:3]

        item["title"] = title
        item["release_year"] = release_year
        item["rating"] = rating
        item["duration_minutes"] = duration
        item["metascore"] = metascore
        item["main_actors"] = actors

        self.logger.info(f"Parsed movie item: {item}")

        yield item
