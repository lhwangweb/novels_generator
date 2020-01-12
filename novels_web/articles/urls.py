from django.urls import path

from . import views

urlpatterns = [
    # 清單
    path('', views.index, name='article_list'),
    # 文章內容
    path('detail/<str:obj_id>', views.detail, name='article_detail'),
]
