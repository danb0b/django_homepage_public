from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.PostListView.as_view(), name='posts'),    
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post'),
    path('folders/', views.FolderListView.as_view(), name='folders'),
    path('<str:top_dir>/<path:subpath>', views.find_post_or_folder, name='find_post_or_folder'),
    path('<str:top_dir>/', views.find_post_or_folder, name='find_top_folder',kwargs={'subpath':''}),    
    ]