from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


def profile_view(request, username=None):
    if username is None and request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.filter(is_published=True).order_by('-published_at')
    is_owner = request.user == profile_user
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_owner': is_owner,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user = request.user
        user.bio = request.POST.get('bio', user.bio)
        user.location = request.POST.get('location', user.location)
        user.website = request.POST.get('website', user.website)
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, 'Профиль обновлён')
        return redirect('profile', username=user.username)
    return render(request, 'users/profile_edit.html', {'user': request.user})


@login_required
@require_POST
def follow_user_view(request):
    username = request.POST.get('username')
    user_to_follow = get_object_or_404(User, username=username)
    if request.user == user_to_follow:
        return JsonResponse({'success': False, 'error': 'Нельзя подписаться на себя'})
    if request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.remove(user_to_follow)
        is_following = False
    else:
        request.user.following.add(user_to_follow)
        is_following = True
    return JsonResponse({'success': True, 'is_following': is_following})


from django.shortcuts import render

# Create your views here.
