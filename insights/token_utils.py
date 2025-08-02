from django.core.cache import cache

from django.utils import timezone
from django.db import transaction
from django.conf import settings

from .models import UserDailyTokenUsage


def can_use_token(user):
    today = timezone.now().date()
    usage, _ = UserDailyTokenUsage.objects.get_or_create(
        user=user,
        date=today
    )
    return usage.tokens_used < settings.MAX_DAILY_TOKENS


def use_token(user):
    today = timezone.now().date()
    with transaction.atomic():
        usage, _ = (
            UserDailyTokenUsage
            .objects.select_for_update()
            .get_or_create(
                user=user,
                date=today
            )
        )
        if usage.tokens_used >= settings.MAX_DAILY_TOKENS:
            return False
        usage.tokens_used += 1
        usage.save()
    return True


def anonymous_can_use_token(ip):
    key = f"anon_token_used:{ip}"
    return not cache.get(key)


def anonymous_use_token(ip):
    key = f"anon_token_used:{ip}"
    # Set key with a 24-hour timeout
    cache.set(key, True, timeout=60 * 60 * 24)  # 1 day


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
