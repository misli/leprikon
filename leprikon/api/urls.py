from django.urls import path

from . import views


def l_path(pattern, name):
    return path(pattern, getattr(views, name), name=name)


app_name = 'leprikon.api'
urlpatterns = [
    l_path('participants/<int:subject_id>/', 'participants'),
    l_path('rocketchat/$', 'rocketchat'),
]
