from __future__ import unicode_literals

from django.db import models
from mongoengine import *
import datetime

# Mongo 連線資訊
MONGO_USER = "test_user"
MONGO_PASSWD = "test_password"
MONGO_HOST = "your.mongodb.hosr"
MONGO_DBNAME = "novels"

conn = connect(
    alias='default',
    db=MONGO_DBNAME,
    host=MONGO_HOST,
    username=MONGO_USER,
    password=MONGO_PASSWD,
    port=27017
)

class ArticleMongoModel(Document):
    class Meta:
        app_lable = 'mongo'
    meta = {'collection': 'articles'}
    _id = ObjectIdField()
    title = StringField(required=True, default='')
    content = StringField(required=True, default='')
    epochs = StringField(required=False, default='')
    num_articles = StringField(required=False, default='')
    sequence_length = StringField(required=False, default='')
    article_length = StringField(required=False, default='')
    first_input = StringField(required=False, default='')
    raw_text = StringField(required=False, default='')
    created_at = DateTimeField(required=True, default=datetime.datetime.utcnow())
    # updated_at = DateTimeField()

    def link(self):
        """
        生產 link
        """
        return "/detail/" + str(self._id)
