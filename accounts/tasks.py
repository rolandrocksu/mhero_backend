# import logging
#
# from .models import MheroUser
# from .services import create_and_send_otp


# def send_otp_notification(user: MheroUser):
#     logging.info('Create OTP and send it to the user.')
#     # can be used pk if this will be task (celery)
#     # user = MheroUser.objects.get(pk=user_pk)
#     create_and_send_otp(user)
