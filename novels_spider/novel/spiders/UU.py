import scrapy
from datetime import datetime
import pytz
import re
import json
from novel.repositary.UU import LinkRepositary as UULinkRepo
from novel.items import ArticleItem
from opencc import OpenCC


class UU(scrapy.Spider):
    """
    UU 看書
    """
    name = "UU"
    start_urls = [
        "https://sj.uukanshu.com/book.aspx?id=83004",
    ]

    def parse(self, response):
        # 解析書籍目錄
        raw_list = self.getLinkList(response)

        # 剔除重複、儲存 Link
        new_articles = UULinkRepo.getNewLinks(raw_list)

        # 每一篇文章，再發起一個 request 去爬
        for article in new_articles:
            yield response.follow(
                article["link"],
                callback=self.getOneArticle,
                meta={
                    "site_name": self.name,
                    "novel_name": raw_list["novel_name"],
                    "author": raw_list["author"],
                }
            )

    def getLinkList(cls, response):
        """
        解析目錄頁並彙整出 link list
        """
        titles2 = []
        site = cls.name
        tidRegex = re.compile(r'aspx\?id=(\d+)')
        matchT = tidRegex.search(response.url)
        novel_id = str(int(matchT.group(1)))

        novel_name = response.css("h1 a b::text").extract_first()
        author = response.css("div.book-info dd::text").extract_first()
        chapterList = response.css("ul#chapterList > li > a")
        links = chapterList.css("a::attr(href)").extract()
        titles = chapterList.css("a::text").extract()

        # 轉繁體
        cc = OpenCC('s2t')
        try:
            novel_name2 = cc.convert(novel_name)
            if novel_name2:
                novel_name = novel_name2
            author2 = cc.convert(author)
            if author2:
                author = author2
        except:
            pass

        for title in titles:
            title2 = cc.convert(title)
            if title2:
                titles2.append(title2)
            else:
                titles2.append(title)

        return {
            "site": site,
            "novel_id": novel_id,
            "author": author,
            "novel_name": novel_name,
            "links": links,
            "titles": titles2,
        }

    def getOneArticle(cls, response):
        """
        解析並取得單篇文章的內容
        """
        cc = OpenCC('s2t')
        article = ArticleItem()

        article_url = response.url
        # 從網址切出 小說 ＆ 文章 id
        tidRegex = re.compile(r'tid=(\d+)&')
        matchT = tidRegex.search(article_url)
        novel_id = str(int(matchT.group(1)))
        sidRegex = re.compile(r'sid=(\d+)')
        matchS = sidRegex.search(article_url)
        article_id = str(int(matchS.group(1)))
        article["novel_id"] = novel_id
        article["article_id"] = article_id
        article["site"] = response.meta["site_name"].strip()
        article["novel"] = response.meta["novel_name"].strip()
        article["author"] = response.meta["author"].replace("作者：", "").strip()

        article["link"] = article_url

        article["title"] = response.css("h3::text").extract_first()
        whitespacePattern = re.compile(r'\s+')
        article["title"] = re.sub(whitespacePattern, '', article["title"])

        content = response.css("div#bookContent")
        if content.extract_first():
            tags = content.css("div.ad_conetent")
            if tags:
                for tag in tags:
                    htmlNode = tag.root
                    if htmlNode is not None and htmlNode.getparent() is not None:
                        htmlNode.getparent().remove(htmlNode)
        article["content"] = content.extract_first()

        # 時間預設值之處理
        tz = pytz.timezone('Asia/Taipei')
        article["created_at"] = datetime.now(tz)
        article["updated_at"] = datetime.now(tz)

        # 轉繁體
        try:
            title2 = cc.convert(article["title"])
            if title2:
                article["title"] = title2
            author2 = cc.convert(article["author"])
            if author2:
                article["author"] = author2
            content2 = cc.convert(article["content"])
            if content2:
                article["content"] = content2
        except:
            pass

        yield article
