from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts import views as posts_views

urlpatterns = [
    path('', posts_views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('accounts/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)