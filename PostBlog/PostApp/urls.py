from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', views.create_profile, name='sign_up'),
    path('login/', views.login_, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('posts/', views.all_posts, name='posts'),
    path('posts/<slug:slug>/', views.detailed_post, name='post'),
    path('posts/new/create/', views.create_post, name='create_post'),
    path('posts/new/update/<slug:slug>/', views.update_post, name='update_post'),
    path('posts/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('posts/user/<str:author>/', views.user_posts, name='user_posts'),
    path('posts/likes/<slug:slug>/', views.all_likes, name='likes_list'),
    path('posts/create_like/<slug:slug>/', views.create_like, name='create_like'),
    path('posts/comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('posts/comment/update/<slug:slug>/', views.update_comment, name='update_comment'),
    path('profile/', views.detailed_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/reset-password/', views.change_password, name='change_password'),
]
