from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, PostLike, PostComment, Profile


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Index Page!")


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


def all_posts(request):
    posts = Post.objects.all()
    context = {
        "posts": posts,
    }
    return render(request, 'posts.html', context=context)


def detailed_post(request: HttpRequest, pk: int) -> HttpResponse:
    context = {
        "post": get_object_or_404(Post, pk=pk)
    }
    if request.method == "POST":
        try:
            PostComment.objects.create(
                who_commented_id=request.user.id,
                for_post_id=pk,
                comment=request.POST['comment']
            )
        except Exception as error:
            return HttpResponse(str(error))
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
            return redirect('post', pk=pk)
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
    posts = Post.objects.filter(author__profile__nickname=author)
    context = {
        "posts": posts,
        "author": Profile.objects.get(
            nickname=author,
        )
    }
    return render(request, 'user_posts.html', context=context)


def all_likes(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.get(pk=pk)
    likes = PostLike.objects.filter(for_post_id=post.id)
    context = {
        "likes": likes,
    }
    return render(request, 'likes_list.html', context=context)


def create_like(request: HttpRequest, pk: int) -> HttpResponse:
    post = Post.objects.get(pk=pk)
    user = request.user
    try:
        like = PostLike.objects.get(for_post=post, who_liked=user)
        if like.is_liked:
            like.is_liked = False
            like.save()
        else:
            like.is_liked = True
            like.save()
    except Exception as error:
        PostLike.objects.create(
            who_liked=user,
            for_post=post,
        )
    return redirect(request.META.get('HTTP_REFERER', None))


@login_required
def delete_comment(request: HttpRequest, pk: int) -> HttpResponse:
    comment = PostComment.objects.get(pk=pk)
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', None))


@login_required
def update_comment(request: HttpRequest, pk: int) -> HttpResponse:
    get_comment = PostComment.objects.get(pk=pk)
    if request.method == "POST":
        get_comment.comment = request.POST.get('comment')
        get_comment.save()
        return redirect('post', pk=get_comment.for_post_id)

    context = {
        "comment": get_comment,
    }
    return render(request, 'comment_update.html', context=context)


def detailed_profile(request: HttpRequest) -> HttpResponse:
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Exception as error:
        return redirect(request.META.get('HTTP_REFERER', None))
    context = {
        "profile": profile,
        "posts": Post.objects.filter(
            author__profile=profile,
        )
    }
    return render(request, 'profile.html', context=context)


def create_profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        profile_image = request.FILES['image']
        nickname = request.POST['nickname']
        if password1 == password2:
            User.objects.create_user(
                username=username,
                password=password1,
            )
            user_instance = User.objects.get(
                username=username,
            )
            Profile.objects.create(
                user=user_instance,
                profile_img=profile_image,
                nickname=nickname,
            )
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
                return redirect('posts')
            else:
                return redirect('sign_up')

        else:
            messages.add_message(request, messages.ERROR, 'Passwords are not equal!')
            return redirect('sign_up')
    return render(request, 'sign_up.html')


@login_required
def update_profile(request: HttpRequest) -> HttpResponse:
    get_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":

        if 'for_nickname' in request.POST:
            get_profile.nickname = request.POST['nickname']
            get_profile.save()

        if 'for_image' in request.POST:
            get_profile.profile_img = request.FILES['image']
            get_profile.save()
        if 'for_about' in request.POST:
            get_profile.about = request.POST['about']
            get_profile.save()

        return redirect('profile')

    return render(request, 'update_profile.html')


def change_password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user = request.user
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.add_message(request, messages.SUCCESS, 'Password has been changed.')
            return redirect('profile')
    context = {
        "form": PasswordChangeForm(request.user),
    }
    return render(request, 'change_user_password.html', context=context)

