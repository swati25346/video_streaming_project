from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_video, name='upload_video'),
    path('edit/<int:video_id>/', views.edit_video, name='edit_video'),
    path('delete/<int:video_id>/', views.delete_video, name='delete_video'),
    path('search/', views.search_videos, name='search_videos'),
    path('list/', views.video_list, name='video_list'),
    path('watch/<int:video_id>/', views.watch_video, name='watch_video'),
]
