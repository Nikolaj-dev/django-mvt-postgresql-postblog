from django.urls import path
from . import views
import django.contrib.auth.views as auth_views


urlpatterns = [
    path('accounts/signup/', views.create_profile, name='sign_up'),
    path('accounts/login/', views.login_, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
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
    path('accounts/update/', views.update_profile, name='update_profile'),
    path('accounts/change-password/', views.change_password, name='change_password'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/my-followers/', views.my_followers, name='my_followers'),
    path('profile/my-followings/', views.my_followings, name='my_followings'),
    path('posts/user-followers/<str:nickname>/', views.user_followers, name='user_followers'),
    path('posts/user-followings/<str:nickname>/', views.user_followings, name='user_followings'),
    path('posts/user/follow/<int:pk>/', views.to_follow_user, name='to_follow_user'),
]
