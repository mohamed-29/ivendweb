from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("gemini/", views.gemini_proxy, name="gemini_proxy"),
]
