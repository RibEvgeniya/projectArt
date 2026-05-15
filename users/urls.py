from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль
    path('profile/', views.profile_view, name='profile'),


    # Редактирование профиля — ДОЛЖНО БЫТЬ ПЕРЕД profile/<str:username>/
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),

    path('profile/<str:username>/followers/', views.followers_view, name='followers'),
    path('profile/<str:username>/following/', views.following_view, name='following'),

    # НОВЫЙ КОД: API для подписки
    path('api/follow/<str:username>/', views.follow_user_view, name='api_follow'),
    path('api/like/', views.like_post_view, name='api_like'),
    path('api/follow/', views.follow_user_view, name='api_follow'),
]