# insights/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from .models import UserDailyTokenUsage
from .serializers import WebsiteAnalyzeSerializer, RedditDataSerializer
from .utils import analyze_website, fetch_reddit_data

MAX_DAILY_TOKENS = 3


def can_use_token(user):
    today = timezone.now().date()
    usage, _ = UserDailyTokenUsage.objects.get_or_create(
        user=user,
        date=today
    )
    return usage.tokens_used < MAX_DAILY_TOKENS


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
        if usage.tokens_used >= MAX_DAILY_TOKENS:
            return False
        usage.tokens_used += 1
        usage.save()
    return True


class WebsiteAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not can_use_token(user):
            return Response(
                {"detail": "Daily token limit reached."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = WebsiteAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data['url']

        # Call your website analysis utility function here
        analysis_result = analyze_website(url)

        # Increment token usage
        use_token(user)

        return Response({"result": analysis_result})


class RedditDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not can_use_token(user):
            return Response(
                {"detail": "Daily token limit reached."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = RedditDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['query']

        # Call your reddit data fetching function here
        reddit_result = fetch_reddit_data(query)

        # Increment token usage
        use_token(user)

        return Response({"result": reddit_result})
