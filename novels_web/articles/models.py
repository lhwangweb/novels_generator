from __future__ import unicode_literals

from django.db import models
from mongoengine import *
import datetime

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
        return "/detail/" + str(self._id)
