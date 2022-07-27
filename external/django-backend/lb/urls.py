from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.hello),
    path('leaderboard', views.leaderboard),
    path('history/<slug:username>', views.history),
    path('vote', views.vote),
    path('submit', views.submit)
]