from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User
from posts.models import Post, ContentType
import os


def home_view(request):
    """Перенаправление на главную страницу (для совместимости)"""
    return redirect('home')


def register_view(request):
    """Представление для регистрации"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'users/register.html', context)


def login_view(request):
    """Представление для входа"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')

                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    """Представление для выхода"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


def profile_view(request, username=None):
    """Просмотр профиля пользователя"""
    if username is None:
        if not request.user.is_authenticated:
            return redirect('users:login')
        profile_user = request.user
        is_owner = True
    else:
        profile_user = get_object_or_404(User, username=username)
        is_owner = (request.user == profile_user) if request.user.is_authenticated else False

    posts = Post.objects.filter(author=profile_user, is_published=True).order_by('-published_at')

    query = request.GET.get('search', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    content_type_filter = request.GET.get('type', '')
    if content_type_filter:
        posts = posts.filter(content_type__slug=content_type_filter)

    is_following = False
    if request.user.is_authenticated and not is_owner:
        is_following = request.user.following.filter(id=profile_user.id).exists()

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'query': query,
        'content_type_filter': content_type_filter,
        'content_types': ContentType.objects.all(),
        'is_owner': is_owner,
        'is_following': is_following,  # НОВЫЙ КОД
    }
    return render(request, 'users/profile.html', context)




# НОВЫЙ КОД: представления для подписчиков и подписок
def followers_view(request, username):
    """Страница подписчиков"""
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.followers.all()
    context = {
        'profile_user': profile_user,
        'users': followers,
        'title': 'Подписчики',
    }
    return render(request, 'users/user_list.html', context)


def following_view(request, username):
    """Страница подписок"""
    profile_user = get_object_or_404(User, username=username)
    following = profile_user.following.all()
    context = {
        'profile_user': profile_user,
        'users': following,
        'title': 'Подписки',
    }
    return render(request, 'users/user_list.html', context)


@login_required
@require_POST
def follow_user_view(request, username):
    """API для подписки/отписки"""
    user_to_follow = get_object_or_404(User, username=username)

    if request.user == user_to_follow:
        return JsonResponse({'success': False, 'error': 'Нельзя подписаться на себя'}, status=400)

    if request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.remove(user_to_follow)
        is_following = False
    else:
        request.user.following.add(user_to_follow)
        is_following = True

    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'followers_count': user_to_follow.followers.count()
    })



@login_required
def profile_edit_view(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user = request.user

        user.bio = request.POST.get('bio', user.bio)
        user.location = request.POST.get('location', user.location)
        user.website = request.POST.get('website', user.website)
        user.phone = request.POST.get('phone', user.phone)

        if request.FILES.get('avatar'):
            if user.avatar and os.path.isfile(user.avatar.path):
                os.remove(user.avatar.path)
            user.avatar = request.FILES['avatar']

        if request.FILES.get('cover'):
            if user.cover and hasattr(user, 'cover') and os.path.isfile(user.cover.path):
                os.remove(user.cover.path)
            user.cover = request.FILES['cover']

        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('users:profile')

    return render(request, 'users/profile_edit.html', {'user': request.user})

@require_POST
def like_post_view(request):
    """API для лайка поста"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_auth': True,
            'message': 'Чтобы поставить лайк, необходимо войти или зарегистрироваться'
        }, status=401)

    post_id = request.POST.get('post_id')
    return JsonResponse({'success': True, 'likes_count': 43})


@require_POST
def follow_user_view(request):
    """API для подписки"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'requires_auth': True,
            'message': 'Чтобы подписаться, необходимо войти или зарегистрироваться'
        }, status=401)

    user_id = request.POST.get('user_id')
    return JsonResponse({'success': True, 'is_following': True})