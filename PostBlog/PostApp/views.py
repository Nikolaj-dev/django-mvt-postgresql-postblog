from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostLike, PostComment, Profile
import logging


logger = logging.getLogger('main')


def login_(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(
                request,
                username=username,
                password=password,
            )
            if user is not None:
                login(request, user)
                logger.info(f'{user} logged in.')
                return redirect('posts')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Wrong login or password!'
                )
                return redirect('login')
        except Exception as error:
            logger.error(f'{request.user}:{error}')
            return redirect('login')
    return render(request, 'login.html')


def create_profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            profile_image = request.FILES['image']
            nickname = request.POST['nickname']
            email = request.POST['email']
            if password1 == password2:
                try:
                    User.objects.create_user(
                        username=username,
                        password=password1,
                        email=email,
                    )
                    user_instance = User.objects.get(
                        username=username,
                    )
                    Profile.objects.create(
                        user=user_instance,
                        profile_img=profile_image,
                        nickname=nickname,
                    )
                except Exception as error:
                    logger.error(f'{request.user}:{error}')
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'User already exists!')
                    return redirect('sign_up')
                user = authenticate(request, username=username, password=password1)
                if user is not None:
                    login(request, user)
                    logger.info(f'{user} signed up.')
                    return redirect('posts')
                else:
                    return redirect('sign_up')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Passwords are not equal!')
                return redirect('sign_up')
        except Exception:
            messages.add_message(
                request,
                messages.ERROR,
                'All fields must be set!')
            return redirect('sign_up')
    return render(request, 'sign_up.html')


def all_posts(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.all().order_by('title')
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    logger.info(f'{request.user} connected {request.path}')
    return render(request, 'posts.html', context=context)


def detailed_post(request: HttpRequest, slug: str) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    post = get_object_or_404(Post, slug=slug)
    context = {
        "post": post,
    }
    if request.method == "POST":
        comment = request.POST['comment']
        if str(comment).strip() == '':
            messages.add_message(
                request,
                messages.ERROR,
                'Comment can not be empty!'
            )
            return redirect('post', slug=slug)
        else:
            try:
                PostComment.objects.create(
                    who_commented_id=request.user.id,
                    for_post_id=post.id,
                    comment=comment,
                )
                logger.info(f'{request.user} left comment for {post.title}')
            except Exception as error:
                logger.error(f'{request.user}:{error}')
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Server error!'
                )
        return redirect('post', slug=slug)

    return render(request, 'post.html', context=context)


@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            title = request.POST['title']
            body = request.POST['body']
            image = request.FILES['image']
            if str(title).strip() == '' or str(body).strip() == '':
                messages.add_message(
                    request,
                    messages.ERROR,
                    'All fields must be set!'
                )
                return redirect('create_post')
            else:
                try:
                    Post.objects.create(
                            title=title,
                            body=body,
                            author=request.user,
                            image=image,
                        )
                    logger.info(f'{request.user} created post {title}')
                    return redirect('posts')
                except Exception as error:
                    logger.error(f'{request.user}:{error}')
                    return redirect('posts')
        except Exception:
            messages.add_message(
                request,
                messages.ERROR,
                'Image filed must be set!'
            )
            return redirect('create_post')
    return render(request, 'create_post.html')


@login_required
def update_post(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    if request.user.username == post.author.username:
        context = {
            "title_value": post.title,
            "body_value": post.body,
            "img_value": post.image,
            "slug": slug,
        }
        if request.method == "POST":
            if 'for_title' in request.POST:
                title = request.POST['title']
                post.title = title
                if str(title).strip() != '':
                    post.save()
            elif 'for_body' in request.POST:
                body = request.POST['body']
                post.body = body
                if str(body).strip() != '':
                    post.save()
            elif 'for_image' in request.POST:
                post.image = request.FILES['image']
                post.save()
            logger.info(f'{request.user} updated post {post.title}')
            return redirect('update_post', slug=slug)
    else:
        return HttpResponse("Method not allowed!")
    return render(request, 'update_post.html', context=context)


@login_required
def delete_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if request.user.pk == post.author_id:
        post.delete()
        logger.info(f'{request.user} deleted post {post.title}')
        return redirect("posts")
    else:
        return HttpResponse("Method not allowed!")


def user_posts(request: HttpRequest, author: str) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    posts = Post.objects.filter(author__profile__nickname=author).order_by('title')
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "author": Profile.objects.get(
            nickname=author,
        ),
        "page_obj": page_obj,
    }
    return render(request, 'user_posts.html', context=context)


def all_likes(request: HttpRequest, slug: int) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    post = get_object_or_404(Post, slug=slug)
    likes = PostLike.objects.filter(for_post_id=post.id)
    context = {
        "likes": likes,
    }
    return render(request, 'likes_list.html', context=context)


@login_required
def create_like(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    user = request.user
    try:
        like = PostLike.objects.get(for_post=post, who_liked=user)
        if like.is_liked:
            like.is_liked = False
            like.save()
            logger.info(f'{request.user} disliked {post.title}')
        else:
            like.is_liked = True
            like.save()
            logger.info(f'{request.user} liked {post.title}')
    except Exception as error:
        try:
            PostLike.objects.create(
                who_liked=user,
                for_post=post,
            )
            logger.info(f'{request.user} liked {post.title}')
        except Exception as error:
            logger.error(f'{request.user}: {error}')
            messages.add_message(request, messages.ERROR, 'Internal Server Error')
    logger.info(f'{request.user} connected {request.path}')
    return redirect(request.META.get('HTTP_REFERER', None))


@login_required
def delete_comment(request: HttpRequest, pk: int) -> HttpResponse:
    comment = get_object_or_404(PostComment, pk=pk)
    comment.delete()
    logger.info(f'{request.user} deleted comment for {comment.for_post.title}')
    return redirect(request.META.get('HTTP_REFERER', None))


@login_required
def update_comment(request: HttpRequest, slug: str) -> HttpResponse:
    get_comment = PostComment.objects.get(for_post__slug=slug)

    if request.method == "POST":
        comment = request.POST['comment']
        if str(comment).strip() == '':
            messages.add_message(
                request,
                messages.ERROR,
                'Comment can not be empty!'
            )
            return redirect('update_comment', slug=slug)
        else:
            get_comment.comment = comment
            get_comment.save()
            logger.info(f'{request.user} updated comment for {get_comment.for_post.title}')
        return redirect('post', slug=slug)

    context = {
        "comment": get_comment,
    }
    return render(request, 'comment_update.html', context=context)


@login_required
def detailed_profile(request: HttpRequest) -> HttpResponse:
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        logger.info(f'{request.user} connected {request.path}')
    except Exception as error:
        logger.error(f'User {request.user} got error: {error}')
        return redirect('posts')

    posts = Post.objects.filter(author__profile=profile).order_by('title')
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "profile": profile,
        "page_obj": page_obj,
    }
    return render(request, 'profile.html', context=context)


@login_required
def update_profile(request: HttpRequest) -> HttpResponse:
    get_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        try:
            if 'for_nickname' in request.POST:
                nickname = request.POST['nickname']
                if str(nickname).strip() == '':
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'Nickname cannot be empty!'
                    )
                    return redirect('update_profile')
                get_profile.nickname = nickname
                get_profile.save()
            if 'for_image' in request.POST:
                get_profile.profile_img = request.FILES['image']
                get_profile.save()
            if 'for_about' in request.POST:
                get_profile.about = request.POST['about']
                get_profile.save()
            if 'for_email' in request.POST:
                get_profile.user.email = request.POST['email']
                get_profile.save()
            logger.info(f'{request.user} updated profile.')
            return redirect('profile')
        except Exception as error:
            logger.error(f'{request.user}:{error}')
            messages.add_message(
                request,
                messages.ERROR,
                'Server error!'
            )
            return redirect('update_profile')

    return render(request, 'update_profile.html')


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user = request.user
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.add_message(request, messages.SUCCESS, 'Password has been changed.')
            logger.info(f'{request.user} changed their password.')
            return redirect('profile')
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'Form is not valid! Check the correction of the fields!'
            )
            return redirect('change_password')
    context = {
        "form": PasswordChangeForm(request.user),
    }
    return render(request, 'change_user_password.html', context=context)

