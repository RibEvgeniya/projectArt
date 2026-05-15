from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts import views as posts_views  # Импортируем views из posts

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная страница - напрямую, без пространства имен
    path('', posts_views.home_view, name='home'),  # Теперь 'home' доступен глобально

    # Остальные маршруты posts с пространством имен
    path('', include('posts.urls')),  # Это добавит /post/create/ и т.д.

    path('accounts/', include('users.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)