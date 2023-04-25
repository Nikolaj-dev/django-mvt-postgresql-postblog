from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostLike, PostComment, Profile, Follower
import logging
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache


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
    posts = cache.get("all_posts")
    if not posts:
        posts = Post.objects.all().order_by('title')
        cache.set("all_posts", posts, timeout=50)
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    logger.info(f'{request.user} connected {request.path}')
    return render(request, 'posts.html', context=context)


def detailed_post(request: HttpRequest, slug: str) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    post = cache.get("detailed_post %s" % (str(slug),))
    if not post:
        post = get_object_or_404(Post, slug=slug)
        cache.set("detailed_post %s" % (str(slug),), post, timeout=10)
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


@login_required
def user_posts(request: HttpRequest, author: str) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    posts = cache.get("%s's posts" % (str(author),))
    if not posts:
        posts = Post.objects.filter(author__profile__nickname=author).order_by('title')
        cache.set("%s's posts" % (str(author),), posts, timeout=10)
    author = Profile.objects.get(nickname=author)
    followed = Follower.objects.filter(
        who_followed=author,
        who_follow=request.user.profile
    )
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "author": author,
        "page_obj": page_obj,
        "followed": followed,
    }
    return render(request, 'user_posts.html', context=context)


def all_likes(request: HttpRequest, slug: int) -> HttpResponse:
    logger.info(f'{request.user} connected {request.path}')
    post = get_object_or_404(Post, slug=slug)
    likes = cache.get("%s's likes" % (str(slug),))
    if not likes:
        likes = PostLike.objects.filter(for_post_id=post.id)
        cache.set("%s's likes" % (str(slug),), likes, timeout=5)
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
    get_comment = PostComment.objects.get(for_post__slug=slug, who_commented=request.user)
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

    posts = cache.get("%s's profile posts" % (str(request.user.profile.nickname),))
    if not posts:
        posts = Post.objects.filter(author__profile=profile).order_by('title')
        cache.set("%s's profile posts" % (str(request.user.profile.nickname),), posts, timeout=10)
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
                user_email = User.objects.get(username=request.user.username)
                user_email.email = request.POST['email']
                user_email.save()
            logger.info(f'{request.user} updated profile.')
            return redirect('update_profile')
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


def my_followers(request: HttpRequest) -> HttpResponse:
    followers = cache.get("%s's followers" % (str(request.user.profile.nickname),))
    if not followers:
        followers = Follower.objects.all().filter(who_followed__nickname=request.user.profile.nickname)
        cache.set("%s's followers" % (str(request.user.profile.nickname),), followers, timeout=10)
    context = {
        "followers": followers,
    }
    logger.info(f'{request.user} connected {request.path}.')
    return render(request, 'followers.html', context=context)


def my_followings(request: HttpRequest) -> HttpResponse:
    followings = cache.get("%s's followings" % (str(request.user.profile.nickname),))
    if not followings:
        followings = Follower.objects.all().filter(who_follow__nickname=request.user.profile.nickname)
        cache.set("%s's followings" % (str(request.user.profile.nickname),), followings, timeout=10)
    context = {
        "followings": followings,
    }
    logger.info(f'{request.user} connected {request.path}.')
    return render(request, 'followings.html', context=context)


def user_followers(request: HttpRequest, nickname: str) -> HttpResponse:
    followers = cache.get("%s's followers" % (str(nickname),))
    if not followers:
        followers = Follower.objects.all().filter(who_followed__nickname=nickname)
        cache.set("%s's followers" % (str(nickname),), followers, timeout=10)
    context = {
        "followers": followers,
    }
    logger.info(f'{request.user} connected {request.path}.')
    return render(request, 'followers.html', context=context)


def user_followings(request: HttpRequest, nickname) -> HttpResponse:
    followings = cache.get("%s's followings" % (str(nickname),))
    if not followings:
        followings = Follower.objects.all().filter(who_follow__nickname=nickname)
        cache.set("%s's followings" % (str(nickname),), followings, timeout=10)
    context = {
        "followings": followings,
    }
    logger.info(f'{request.user} connected {request.path}.')
    return render(request, 'followings.html', context=context)


@login_required
def to_follow_user(request: HttpRequest, pk: int) -> HttpResponse:
    who_followed = get_object_or_404(Profile, pk=pk)
    who_follow = request.user.profile
    try:
        followed = Follower.objects.get(
            who_followed=who_followed,
            who_follow=who_follow,
        )
        if followed:
            followed.delete()
            logger.info(f'{request.user} unfollowed {who_followed.nickname}')
        else:
            Follower.objects.create(
                who_followed=who_followed,
                who_follow=who_follow,
            )
            logger.info(f'{request.user} followed {who_followed.nickname}')
    except Exception as error:
        try:
            Follower.objects.create(
                who_followed=who_followed,
                who_follow=who_follow,
            )
            logger.info(f'{request.user} followed {who_followed.nickname}')
        except Exception as error:
            logger.error(f'{request.user}: {error}')
            messages.add_message(request, messages.ERROR, 'Internal Server Error')
    logger.info(f'{request.user} connected {request.path}')
    return redirect(request.META.get('HTTP_REFERER', None))


@login_required
def my_likes(request: HttpRequest) -> HttpResponse:
    likes = cache.get("%s's likes" % (str(request.user.profile.nickname),))
    if not likes:
        likes = PostLike.objects.filter(
            who_liked=request.user,
            is_liked=True,
        ).order_by('for_post')
        cache.set("%s's likes" % (str(request.user.profile.nickname),), likes, timeout=5)
    paginator = Paginator(likes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "likes": page_obj,
    }
    logger.info(f'{request.user} connected {request.path}')
    return render(request, 'my_likes.html', context=context)


def search(request: HttpRequest) -> HttpResponse:
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(author__profile__nickname__icontains=query)
        ).distinct().order_by('title')
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    logger.info(f'{request.user} searched <{query}>')
    return render(request, 'search_bar.html', context)


def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')


def feedback(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        message = request.POST['feedback']
        if request.user.is_authenticated:
            try:
                send_mail(
                    f"Feedback from {request.user.email}",
                    str(message),
                    str(settings.EMAIL_HOST_USER),
                    [str(settings.FEEDBACK_EMAIL)],
                )
                logger.info(f"{request.user} sent a feedback!")
                messages.success(
                    request,
                    "Thank you for your feedback!"
                )
            except Exception as error:
                logger.error(f"{request.user}: {error}")
                messages.error(
                    request,
                    "Server Internal Error!"
                )
                return redirect("feedback")
        else:
            messages.info(
                request,
                "Please login! If you can't enter, please contact our help-center blogpost@internet.ru")
    return render(request, 'feedback.html')
