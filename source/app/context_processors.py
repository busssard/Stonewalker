from django.contrib.auth.models import User
from django.conf import settings


def shop_visibility(request):
    """
    Context processor to determine shop visibility based on user count.
    Shop is only visible when registered users >= SHOP_VISIBLE_USER_THRESHOLD.
    """
    threshold = getattr(settings, 'SHOP_VISIBLE_USER_THRESHOLD', 1000)
    user_count = User.objects.count()

    return {
        'user_count': user_count,
        'shop_visible': user_count >= threshold,
    }


def premium_status(request):
    """
    Context processor to expose premium subscription status to all templates.
    """
    if request.user.is_authenticated:
        try:
            is_premium = request.user.profile.is_premium
        except Exception:
            is_premium = False
    else:
        is_premium = False

    return {
        'is_premium_user': is_premium,
    }
