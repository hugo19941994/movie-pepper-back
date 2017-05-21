# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Movie(scrapy.Item):
    title = scrapy.Field()
    rating = scrapy.Field()
    genres = scrapy.Field()
    year = scrapy.Field()
    keywords = scrapy.Field()
    plot = scrapy.Field()
    director = scrapy.Field()
    url = scrapy.Field()
    reviews = scrapy.Field()
    poster = scrapy.Field()
