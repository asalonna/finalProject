from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_classroom', views.create_classroom, name='create_classroom'),
    path('create_question', views.create_question, name='create_question'),
    path('access', views.access, name='access_question'),
    path('task/<int:pk>', views.task, name='task'),
    path('next/<str:pk>', views.next_question, name='next'),
    path('end_screen', views.end_of_questions, name='end_screen'),
    path('track', views.track, name='tracking'),
    path('dsl_guide', views.dsl_guide, name='dsl_guide'),
]

