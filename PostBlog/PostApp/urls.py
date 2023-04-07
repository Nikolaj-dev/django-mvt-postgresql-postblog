from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.create_profile, name='sign_up'),
    path('login/', views.login_, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('posts/', views.all_posts, name='posts'),
    path('posts/<int:pk>/', views.detailed_post, name='post'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/update/<int:pk>/', views.update_post, name='update_post'),
    path('posts/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('posts/user/<str:author>/', views.user_posts, name='user_posts'),
    path('posts/likes/<int:pk>', views.all_likes, name='likes_list'),
    path('posts/create_like/<int:pk>', views.create_like, name='create_like'),
    path('posts/comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('posts/comment/update/<int:pk>/', views.update_comment, name='update_comment'),
    path('profile/', views.detailed_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
