import scrapy

class LinkRepositary:
    name = "UU"

    def __init__(self):
        # self.name = "UU"
        pass
    
    @classmethod
    def getNewLinks(self, raw_links):
        """
        處理剛抓下來的文章清單
         1. 比對重複
         2. 儲存新網址
        """
        links = raw_links["links"]
        titles = raw_links["titles"]
        site = raw_links["site"]
        novel_id = raw_links["novel_id"]

        from novel.db.mongo import Links as LinksOnMongo
        from novel.db import mongo_connection
        mongo_connection()

        datas = []
        if len(links) == len(titles) and len(titles) > 0:
            lenData = len(links)
            for i in range(0, lenData):
                link = links[i]
                title = titles[i]
                if link and title:
                    link = link.strip()
                    title = title.strip()
                    if link.find("http") == -1:
                        link = "https://sj.uukanshu.com/" + link
                    # 從 mongo 內的 links 這邊確認之前是否收錄過
                    try:
                        existedLink = LinksOnMongo.objects(link=link).get()
                    except Exception as e:
                        # 沒有資料會噴 Exception
                        existedLink = None
                    if not existedLink:
                        newLink = LinksOnMongo(site=site, novel_id=novel_id, title=title, link=link)
                        newLink.save()
                        datas.append({
                            'title':title,
                            'link':link
                        })

        return datas

class ArticleRepositary:
    
    name = "UU"
    
    def __init__(self):
        pass 

    def insertArticle(articleItem):
        from novel.db.mongo import Articles as ArticlesOnMongo
        from novel.db import mongo_connection

        # Insert 整個 Scrapy Item 到 Mongo
        newArticle = ArticlesOnMongo(
            site = articleItem["site"],
            novel = articleItem["novel"],
            novel_id = articleItem["novel_id"],
            article_id = articleItem["article_id"],
            author = articleItem["author"],
            link = articleItem["link"],
            title = articleItem["title"],
            content = articleItem["content"],
            created_at =  articleItem["created_at"],
            updated_at =  articleItem["updated_at"],
        )
        newArticle.save()