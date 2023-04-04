from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.sign_up, name='sign_up'),
    path('login/', views.login_, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('posts/', views.all_posts, name='posts'),
    path('posts/<int:pk>/', views.detailed_posts, name='post'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/update/<int:pk>/', views.update_post, name='update_post'),
    path('posts/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('posts/user/<str:author>/', views.user_posts, name='user_posts'),
]
