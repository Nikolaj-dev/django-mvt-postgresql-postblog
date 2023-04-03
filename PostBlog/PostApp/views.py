from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404

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
            return HttpResponse('Registered successfully!')
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
        return HttpResponse('Logged In!')
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

