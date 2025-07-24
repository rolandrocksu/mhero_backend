import logging

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from accounts.choices import NotificationTransportChoices, AccountDeletionChoices
from accounts.models import MheroUser, AccountDeletion
from accounts.services import blacklist_user_valid_tokens
from lib.notifications import NotificationService
from lib.serializer_fields import Base64ImageField


class UserReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = MheroUser
        fields = (
            'id', 'first_name', 'last_name', 'company', 'last_login', 'is_active',
            'email', 'phone_number', 'profile_photo', 'created_at'
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_photo = Base64ImageField(allow_null=True)

    class Meta:
        model = MheroUser
        fields = ('id', 'first_name', 'last_name', 'profile_photo')
        read_only_fields = ('id',)


class RequestAccountDeletionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountDeletion
        fields = ['id', 'user', 'identifier', 'request_date', 'state', 'reason']
        read_only_fields = ['id', 'user', 'identifier', 'request_date', 'state']

    def validate(self, attrs):
        user = self.context['request'].user
        last_account_deletion = user.deletion_requests.order_by('-request_date').first()
        if (
            last_account_deletion and
            last_account_deletion.state == AccountDeletionChoices.DONE
        ):
            raise ValidationError({'detail': "Account already deleted."})
        identifier = user.email if user.email else user.phone_number
        attrs['identifier'] = identifier
        attrs['user'] = user
        return attrs


class ConfirmAccountDeletionSerializer(serializers.Serializer):
    passcode = serializers.CharField()

    def validate(self, attrs):
        # user = self.context['request'].user
        # passcode = OTP.objects.filter(user=user, key=attrs['passcode']).first()
        # if not passcode or not validate_otp(passcode):
        #     raise serializers.ValidationError({'detail': "Invalid passcode."})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.is_deleted = True
        user.save()

        blacklist_user_valid_tokens(user)

        account_deletion = user.deletion_requests.order_by('-request_date').first()
        account_deletion.state = AccountDeletionChoices.DONE
        account_deletion.save()

        notification_type = "account_deletion"

        if user.email:
            notification = NotificationService(NotificationTransportChoices.email)
            recipients = [user.email]
            logging.info(f"OTP created for user {user.pk}, sending via email to {user.email}")
        # elif user.phone_number:
        else:
            notification = NotificationService(NotificationTransportChoices.sms)
            recipients = [user.phone_number]
            logging.info(f"OTP created for user {user.pk}, sending via SMS to {user.phone_number}")

        notification.send(
            notification_type=notification_type,
            context_dict=dict(user=user),
            recipients=recipients,
        )
        logging.info(f"OTP sent successfully to user {user.pk}.")

        return user
