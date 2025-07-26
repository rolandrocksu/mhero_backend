from django.urls import path
from .views import WebsiteAnalyzeView, RedditDataView

urlpatterns = [
    path('analyze-website/', WebsiteAnalyzeView.as_view(), name='analyze-website'),
    path('reddit-data/', RedditDataView.as_view(), name='reddit-data'),
]
