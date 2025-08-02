# insights/models.py
from django.db import models
from django.utils import timezone
from accounts.models import MheroUser  # adjust import if needed


class UserDailyTokenUsage(models.Model):
    user = models.ForeignKey(MheroUser, on_delete=models.CASCADE, related_name='daily_token_usage')
    date = models.DateField(default=timezone.now)
    tokens_used = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.tokens_used} tokens used"


class WebsiteAnalysisCache(models.Model):
    url = models.URLField(unique=True)
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Optional: expire after 7 days
        from django.utils.timezone import now
        return (now() - self.created_at).days >= 7


class RedditDataCache(models.Model):
    query_hash = models.CharField(max_length=64, unique=True)
    original_query = models.JSONField()  # Optional, for debugging/inspection
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from django.utils.timezone import now
        return (now() - self.created_at).days >= 7
