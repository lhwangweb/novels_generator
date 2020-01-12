# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkItem(scrapy.Item):
    site = scrapy.Field()
    novel_id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()


class ArticleItem(scrapy.Item):
    """
    單篇文章 Model
    """
    site = scrapy.Field()
    novel = scrapy.Field()
    novel_id = scrapy.Field()
    article_id = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
