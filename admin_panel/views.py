from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry

@staff_member_required
def dashboard(request):
    """
    Кастомная дашборд-панель для администраторов
    """
    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'creators': User.objects.filter(is_creator=True).count(),
        'moderators': User.objects.filter(is_moderator=True).count(),
        'recent_logs': LogEntry.objects.all().order_by('-action_time')[:10],
    }
    return render(request, 'admin_panel/dashboard.html', context)