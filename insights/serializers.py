# insights/serializers.py
from rest_framework import serializers


class WebsiteAnalyzeSerializer(serializers.Serializer):
    url = serializers.URLField()


class RedditDataSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
