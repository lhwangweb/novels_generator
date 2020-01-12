from mongoengine import *
import datetime


class Links(Document):
    """
    儲存連結 - 進度記錄用，防止收錄重複連結內容
    """
    meta = {'collection': 'links'}
    site = StringField(required=True, default='')
    novel_id = StringField(required=True, default='')
    title = StringField(required=True, default='')
    link = StringField(required=True, default='', unique=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.utcnow())


class Articles(Document):
    """
    儲存文章
    """
    meta = {'collection': 'raw_articles'}
    site = StringField(required=True, default='')
    novel = StringField(required=True, default='')
    novel_id = StringField(required=True, default='')
    article_id = StringField(required=True, default='')
    author = StringField(required=True, default='')
    title = StringField(required=True, default='')
    content = StringField(required=True, default='')
    link = StringField(required=True, default='', unique=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.utcnow())
    updated_at = DateTimeField()
