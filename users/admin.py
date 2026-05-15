from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Кастомизация отображения пользователей в админке
    """
    list_display = ('username', 'email', 'is_creator', 'is_moderator', 'is_staff')
    list_filter = ('is_creator', 'is_moderator', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'cover', 'bio', 'is_creator', 'is_moderator', 'phone', 'location', 'website')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'cover', 'bio', 'is_creator', 'is_moderator', 'phone', 'location', 'website')
        }),
    )

admin.site.register(User, CustomUserAdmin)