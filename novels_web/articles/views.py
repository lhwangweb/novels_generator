from django.shortcuts import render
# from django.http import HttpResponse
from django.shortcuts import render_to_response
from articles.models import ArticleMongoModel

def index(request):
    """
    文章列表頁
    """
    articles = ArticleMongoModel.objects.all()
    return render_to_response("articles/list.html", {"articles": articles})


def detail(request, obj_id=""):
    """
    文章詳細頁，以 _id 查找文章
    """
    article = ArticleMongoModel.objects.filter(_id=str(obj_id)).first()
    return render_to_response("articles/detail.html", {"article": article})
