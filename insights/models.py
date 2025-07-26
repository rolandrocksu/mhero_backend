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
