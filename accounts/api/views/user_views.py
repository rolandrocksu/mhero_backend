from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView, GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from accounts.api.permissions import IsOwner
from accounts.api.serializers import (
    UserReadOnlySerializer,
    UserUpdateSerializer,
    RequestAccountDeletionSerializer,
    ConfirmAccountDeletionSerializer
)
from accounts.models import MheroUser


class UserRetrieveUpdateAPIView(RetrieveAPIView, UpdateAPIView):
    http_method_names = ("get", "patch")
    permission_classes = [IsOwner]
    queryset = MheroUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserReadOnlySerializer


class RequestAccountDeletionAPIView(APIView):
    serializer_class = RequestAccountDeletionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RequestAccountDeletionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # user = request.user
        # send_otp_notification(user)

        return Response(
            {"detail": "OTP sent successfully.", "data": serializer.data},
            status=HTTP_200_OK,
        )


class ConfirmAccountDeletionAPIView(GenericAPIView):
    serializer_class = ConfirmAccountDeletionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User deleted"},
            status=HTTP_204_NO_CONTENT,
        )
