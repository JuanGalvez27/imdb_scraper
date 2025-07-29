# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    title = scrapy.Field()
    release_year = scrapy.Field()
    rating = scrapy.Field()
    duration_minutes = scrapy.Field()
    metascore = scrapy.Field()
    main_actors = scrapy.Field()
