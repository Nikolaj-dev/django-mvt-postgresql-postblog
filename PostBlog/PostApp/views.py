from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
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


@login_required
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


@login_required
def update_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.get(pk=pk)
    if request.user.username == post.author.username:
        context = {
            "title_value": post.title,
            "body_value": post.body,
            "img_value": post.image,
        }
        if request.method == "POST":
            if request.FILES.get('image') is None:
                post.title = request.POST['title']
                post.body = request.POST['body']
                post.save()
            else:
                post.title = request.POST['title']
                post.body = request.POST['body']
                post.image = request.FILES.get('image')
                post.save()
            return redirect('posts')
    else:
        return HttpResponse("Method not allowed!")
    return render(request, 'update_post.html', context=context)


@login_required
def delete_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.get(pk=pk)
    if request.user.pk == post.author_id:
        post.delete()
        return redirect("posts")
    else:
        return HttpResponse("Method not allowed!")


def user_posts(request: HttpRequest, author: str) -> HttpResponse:
    posts = Post.objects.filter(author__username=author)
    context = {
        "posts": posts,
    }
    return render(request, 'user_posts.html', context=context)

