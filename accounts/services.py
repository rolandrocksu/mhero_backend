from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from lib.jwt_utils import is_valid_token
from .models import MheroUser


# def create_and_send_otp(user: MheroUser):
#     """Generate OTP and send it to the user."""
#     # By creating new otp it automatically deletes all previous otp
#     passcode = OTP.objects.create(user=user)
#     notification_type = "otp_notification"
#
#     if user.email:
#         notification = NotificationService(NotificationTransportChoices.email)
#         recipients = [user.email]
#         logging.info(f"OTP created for user {user.pk}, sending via email to {user.email}")
#     # elif user.phone_number:
#     else:
#         notification = NotificationService(NotificationTransportChoices.sms)
#         recipients = [user.phone_number]
#         logging.info(f"OTP created for user {user.pk}, sending via SMS to {user.phone_number}")
#
#     notification.send(
#         notification_type=notification_type,
#         context_dict=dict(passcode=passcode.key),
#         recipients=recipients,
#     )
#     logging.info(f"OTP sent successfully to user {user.pk}.")
#
#
# def validate_otp(passcode: OTP) -> bool:
#     """Check whether the given OTP is valid (is active and not expired), then deactivate it."""
#     if not passcode.is_active:
#         return False
#
#     seconds = (timezone.now() - passcode.created_at).total_seconds()
#     if seconds >= settings.OTP_EXPIRE_TIME:
#         is_valid = False
#     else:
#         is_valid = True
#
#     # deactivate passcode
#     passcode.is_active = False
#     passcode.save()
#     return is_valid


def blacklist_user_valid_tokens(user: MheroUser):
    """Blacklist user's all valid and not expired refresh tokens."""
    blacklisted_token_ids = BlacklistedToken.objects.values_list('token_id')
    qs = OutstandingToken.objects.filter(user=user).exclude(id__in=blacklisted_token_ids)

    for outstanding_token in qs:
        if is_valid_token(outstanding_token.token):
            BlacklistedToken.objects.create(token=outstanding_token)
