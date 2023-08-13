from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseForbidden
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostLike, PostComment, Profile, Follower
import logging
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse


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


def sign_up(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        profile_image = request.FILES.get('image')

        if all([username, password1, password2, email, nickname, profile_image]):
            if password1 == password2 and len(password1) >= 8:
                try:
                    # Validate the password against AUTH_PASSWORD_VALIDATORS
                    validate_password(password1, user=User)
                except ValidationError as error:
                    # Log password validation error
                    logger.warning(f'Password validation failed for user {username}: {error.messages}')
                    messages.error(request, '\n'.join(error.messages))
                    return redirect('sign_up')

                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password1,
                        email=email,
                    )
                    profile = Profile(user=user, profile_img=profile_image, nickname=nickname)
                    profile.save()

                    # Automatically log in the user after successful sign-up
                    user = authenticate(request, username=username, password=password1)
                    if user is not None:
                        login(request, user)

                    # Log successful sign-up
                    logger.info(f'User {username} signed up successfully.')
                    messages.success(request, 'You have successfully signed up!')
                    return redirect('posts')
                except Exception as error:
                    # Log user creation error
                    logger.exception(f'Error creating user {username}: {error}')
                    messages.error(request, 'User already exists!')
                    return redirect('sign_up')
            else:
                messages.error(request, 'Passwords are not equal or contain less than 8 letters!')
                return redirect('sign_up')
        else:
            messages.error(request, 'All fields must be set!')
            return redirect('sign_up')
    else:
        return render(request, 'sign_up.html')


def all_posts(request: HttpRequest) -> HttpResponse:
    posts = cache.get("all_posts")
    if not posts:
        posts = Post.objects.all().order_by('title')
        cache.set("all_posts", posts, timeout=15)
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
        cache.set("detailed_post %s" % (str(slug),), post, timeout=15)
    context = {
        "post": post,
    }
    return render(request, 'post.html', context=context)


@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            title = request.POST['title']
            body = request.POST['body']
            image = request.FILES['image']
            if not (str(title).strip() and str(body).strip()):
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Please ensure that all fields in the form are completed.'
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
                'Please load the image!'
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
            if 'title' in request.POST:
                title = request.POST['title']
                post.title = title
                if str(title).strip():
                    post.save()
                    logger.info(f'{request.user} updated the title in {post.title}')
            if 'body' in request.POST:
                body = request.POST['body']
                post.body = body
                if str(body).strip():
                    post.save()
                    logger.info(f'{request.user} updated the body in {post.title}')
            if 'image' in request.FILES:
                post.image = request.FILES['image']
                post.save()
                logger.info(f'{request.user} updated the image {post.title}')
            return redirect('update_post', slug=slug)
    else:
        return HttpResponse("Method not allowed!")
    return render(request, 'update_post.html', context=context)


@login_required
def delete_post(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        post = get_object_or_404(Post, pk=pk)
        if request.user == post.author:
            post.delete()
            logger.info(f'{request.user} deleted post "{post.title}"')
            messages.success(request, 'Post deleted successfully!')
        else:
            messages.error(request, 'You are not authorized to delete this post.')
        return redirect('posts')
    else:
        # Handle GET request
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


@login_required
def all_likes(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    logger.info(f'{request.user} connected {request.path}')
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
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        user = request.user
        try:
            like = PostLike.objects.get(for_post=post, who_liked=user)
            like.delete()
            logger.info(f'{request.user} disliked {post.title}')
        except PostLike.DoesNotExist:
            PostLike.objects.create(
                who_liked=user,
                for_post=post,
            )
            logger.info(f'{request.user} liked {post.title}')
        except Exception as error:
            logger.error(f'{request.user}: {error}')
            messages.add_message(request, messages.ERROR, 'Internal Server Error')
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse('post', kwargs={'slug': slug}))
    else:
        return HttpResponse("Method not allowed!")


@login_required
def create_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        comment = request.POST.get('comment')
        if comment and comment.strip():
            try:
                PostComment.objects.create(
                    who_commented=request.user,
                    for_post=post,
                    comment=comment,
                )
                logger.info(f'{request.user} left a comment for {post.title}')
            except Exception as error:
                logger.error(f'{request.user}: {error}')
                messages.error(request, 'Server error! Comment could not be posted.')
        else:
            messages.error(request, 'Comment can not be empty!')

    return redirect('post', slug=slug)


@login_required
def delete_comment(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == 'POST':
        comment = get_object_or_404(PostComment, pk=pk)
        if request.user == comment.who_commented:
            comment.delete()
            logger.info(f'{request.user} deleted comment for {comment.for_post.title}')
        else:
            return HttpResponseForbidden("You do not have permission to delete this comment.")
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse('posts'))
    else:
        return HttpResponse('Method not allowed.')


@login_required
def update_comment(request: HttpRequest, slug: str, comment_id: int) -> HttpResponse:
    try:
        get_comment = PostComment.objects.get(for_post__slug=slug, who_commented=request.user, id=comment_id)
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
                try:
                    # Attempt to save the updated comment
                    get_comment.comment = comment
                    get_comment.save()
                    logger.info(f'{request.user} updated comment for {get_comment.for_post.title}')
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'Comment updated successfully!'
                    )
                except Exception as e:
                    logger.error(f'{request.user} got an error while updating comment: {e}')
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'An error occurred while updating the comment. Please try again later.'
                    )
            return redirect('post', slug=slug)
        context = {
            "comment": get_comment,
        }
        return render(request, 'comment_update.html', context=context)
    except PostComment.DoesNotExist:
        raise Http404


@login_required
def detailed_profile(request: HttpRequest) -> HttpResponse:
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        logger.info(f'{request.user} connected {request.path}')
    except Profile.DoesNotExist:
        logger.error(f'User {request.user} does not have a profile.')
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
    profile = request.user.profile

    if request.method == "POST":
        try:
            if 'for_nickname' in request.POST:
                nickname = request.POST['nickname']
                if not str(nickname).strip():
                    messages.error(request, 'Nickname cannot be empty!')
                    return redirect('update_profile')
                profile.nickname = nickname
                profile.save()

            if 'for_image' in request.POST and 'image' in request.FILES:
                profile.profile_img = request.FILES['image']
                profile.save()

            if 'for_about' in request.POST:
                profile.about = request.POST['about']
                profile.save()

            if 'for_email' in request.POST:
                new_email = request.POST['email']
                validate_email(new_email)

                if User.objects.filter(email=new_email).exclude(username=request.user.username).exists():
                    messages.error(request, 'This email is already in use by another user.')
                    return redirect('update_profile')

                request.user.email = new_email
                request.user.save()
                messages.success(request, 'Email updated successfully.')
                logger.info(f'{request.user} updated email to {new_email}.')

            messages.success(request, 'Profile updated successfully.')
            logger.info(f'{request.user} updated profile.')

            return redirect('update_profile')
        except ValidationError as e:
            messages.error(request, 'Please enter a valid email address.')
        except Exception as e:
            messages.error(request, 'Server error!')
            logger.error(f'{request.user}: {e}')

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


@login_required
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


@login_required
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


@login_required
def user_followers(request: HttpRequest, nickname: str) -> HttpResponse:
    profile = Profile.objects.filter(nickname=nickname)
    if profile:
        followers = cache.get("%s's followers" % (str(nickname),))
        if not followers:
            followers = Follower.objects.all().filter(who_followed__nickname=nickname)
            cache.set("%s's followers" % (str(nickname),), followers, timeout=10)
        context = {
            "followers": followers,
        }
        logger.info(f'{request.user} connected {request.path}.')
        return render(request, 'followers.html', context=context)
    else:
        raise Http404


@login_required
def user_followings(request: HttpRequest, nickname) -> HttpResponse:
    profile = Profile.objects.filter(nickname=nickname)
    if profile:
        followings = cache.get("%s's followings" % (str(nickname),))
        if not followings:
            followings = Follower.objects.all().filter(who_follow__nickname=nickname)
            cache.set("%s's followings" % (str(nickname),), followings, timeout=10)
        context = {
            "followings": followings,
        }
        logger.info(f'{request.user} connected {request.path}.')
        return render(request, 'followings.html', context=context)
    else:
        raise Http404


@login_required
def to_follow_user(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == 'POST':
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
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return redirect(referer)
        else:
            return redirect(reverse('posts'))
    else:
        return HttpResponse('Method not allowed!')


@login_required
def my_likes(request: HttpRequest) -> HttpResponse:
    likes = cache.get("%s's likes" % (str(request.user.profile.nickname),))
    if not likes:
        likes = PostLike.objects.filter(
            who_liked=request.user,
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
        if str(message).strip() != '':
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
                return redirect('feedback')
        else:
            messages.info(
                request,
                "All fields must be field!"
            )
            return redirect('feedback')
    return render(request, 'feedback.html')
