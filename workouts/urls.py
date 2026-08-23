from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.day_select, name='day_select'),
    path('day/create/', views.create_day, name='create_day'),
    path('day/<int:day_id>/delete/', views.delete_day, name='delete_day'),
    path('day/<int:day_id>/exercises/', views.manage_exercises, name='manage_exercises'),
    path('day/<int:day_id>/', views.day_program, name='day_program'),

    path('exercise/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),

    path('progress/', views.progress_list, name='progress_list'),
    path('progress/<int:exercise_id>/', views.progress_chart, name='progress_chart'),
    path('progress/<int:exercise_id>/data/', views.progress_data, name='progress_data'),

    path('export/excel/', views.export_excel, name='export_excel'),
]