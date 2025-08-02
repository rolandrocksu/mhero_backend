from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import WebsiteAnalyzeSerializer
from .token_utils import (
    get_client_ip,
    anonymous_can_use_token,
    anonymous_use_token,
    can_use_token,
    use_token
)
from .lambda_functions import analyze_website, fetch_reddit_data


class WebsiteAnalyzeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)

        if user:
            if not can_use_token(user):
                return Response(
                    {"detail": "Daily token limit reached."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        else:
            if not anonymous_can_use_token(ip):
                return Response(
                    {"detail": "Anonymous usage limit reached. Please sign up."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        serializer = WebsiteAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data['url']
        analysis_result = analyze_website(url)

        if user:
            use_token(user)
        else:
            anonymous_use_token(ip)

        return Response({"result": analysis_result})


class RedditDataView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)
        if user:
            if not can_use_token(user):
                return Response(
                    {"detail": "Daily token limit reached."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        else:
            if not anonymous_can_use_token(ip):
                return Response(
                    {"detail": "Anonymous usage limit reached. Please sign up."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        query = request.data.get("query")
        if not query:
            return Response(
                {"detail": "Missing required field: 'query'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reddit_result = fetch_reddit_data(query)

        if user:
            use_token(user)
        else:
            anonymous_use_token(ip)

        return Response({"result": reddit_result})
