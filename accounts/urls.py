from django.urls import path

from accounts.api.views import (
    LogoutAPIView,
    TokenRefreshAPIView,
    TokenVerifyAPIView,
    GoogleLoginAPIView,
    AppleLoginAPIView,
    UserRetrieveUpdateAPIView,
    RequestAccountDeletionAPIView,
    ConfirmAccountDeletionAPIView,
    TestLoginView,
)

urlpatterns = [
    # login paths
    # path("login/", LoginAPIView.as_view(), name="login"),
    path('login/test/', TestLoginView.as_view(), name='google-login'),
    path('login/google/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('login/apple/', AppleLoginAPIView.as_view(), name='apple-login'),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyAPIView.as_view(), name="token-verify"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),

    # reset password paths
    # path("reset-password/", ResetPasswordAPIView.as_view(), name="password-reset"),
    # path(
    #     "reset-password-confirm/",
    #     ResetPasswordConfirmAPIView.as_view(),
    #     name="password_reset_confirm",
    # ),

    # user related paths
    path(
        "users/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="get-update-user"
    ),
    path(
        'delete/request/',
        RequestAccountDeletionAPIView.as_view(),
        name='request-account-deletion'
    ),
    path(
        'delete/confirm/',
        ConfirmAccountDeletionAPIView.as_view(),
        name='confirm-account-deletion'
    ),
]
