from django.conf import settings

from .utils import get_user_permissions_context


def user_permissions(request):
    """Add user permissions to template context."""
    # SITE_BANNER: شريط فوق الصفحات للنسخة التجريبية عشان محدش يخلط بينها وبين الموقع الحقيقي
    context = {'site_banner': settings.SITE_BANNER}
    if request.user.is_authenticated:
        context['user_permissions_dict'] = get_user_permissions_context(request.user)
    else:
        context['user_permissions_dict'] = {}
    return context
