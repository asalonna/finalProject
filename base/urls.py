from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/<int:pk>', views.task, name='task'),
    path('create', views.create_question, name='create_question'),
    path('access', views.access, name='access_question'),
    path('track', views.track, name='tracking'),
    path('next/<int:pk>', views.next_question, name='next'),
]

