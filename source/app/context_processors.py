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
    Also exposes is_early_user so templates can show the "early supporter" badge/message
    (e.g., premium.html shows "lifetime premium" instead of pricing for early users,
    and nav_links.html can differentiate the Premium link destination).
    """
    is_premium = False
    is_early = False

    if request.user.is_authenticated:
        try:
            is_premium = request.user.profile.is_premium
        except Exception:
            pass

        from accounts.models import is_early_user
        is_early = is_early_user(request.user)

    return {
        'is_premium_user': is_premium,
        'is_early_user': is_early,
    }
