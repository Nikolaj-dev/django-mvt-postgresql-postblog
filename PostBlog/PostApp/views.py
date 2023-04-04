from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Index Page!")


def sign_up(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserCreationForm,
    }
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('posts')
    return render(request, 'sign_up.html', context=context)


def login_(request: HttpRequest) -> HttpResponse:
    context = {

    }
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user is not None:
            login(request, user)
        return redirect('posts')
    return render(request, 'login.html', context=context)


def all_posts(request: HttpRequest) -> HttpResponse:
    context = {
        "posts": Post.objects.all()
    }
    return render(request, 'posts.html', context=context)


def detailed_posts(request: HttpRequest, pk: int) -> HttpResponse:
    context = {
        "post": get_object_or_404(Post, pk=pk)
    }
    return render(request, 'post.html', context=context)


def create_post(request: HttpRequest) -> HttpResponse:
    context = {

    }
    if request.method == "POST":
        title = request.POST['title']
        body = request.POST['body']
        image = request.FILES['image']
        Post.objects.create(
            title=title,
            body=body,
            author=request.user,
            image=image,
        )
        return redirect('posts')
    return render(request, 'create_post.html', context=context)


def update_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.filter(pk=pk)
    context = {
        "title_value": Post.objects.get(pk=pk).title,
        "body_value": Post.objects.get(pk=pk).body
    }
    if request.method == "POST":
        title = request.POST['title']
        body = request.POST['body']
        post.update(
            title=title,
            body=body,
        )
        return redirect('posts')
    return render(request, 'update_post.html', context=context)


def delete_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.filter(pk=pk)
    post.delete()
    return redirect("posts")


def user_posts(request: HttpRequest, author: str) -> HttpResponse:
    posts = Post.objects.filter(author__username=author)
    context = {
        "posts": posts,
    }
    return render(request, 'user_posts.html', context=context)

