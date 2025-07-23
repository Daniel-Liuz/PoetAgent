# E:\Program\poetry_project\poetry_project\urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # 它的唯一任务就是把所有请求转发给 core 应用
]
