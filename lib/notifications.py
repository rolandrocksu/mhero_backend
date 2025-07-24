import logging

from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.exceptions import APIException

from accounts.choices import NotificationTransportChoices


class NotificationServiceStrategy(ABC):
    def __init__(self):
        self.email_template_base = "email"
        self.sms_template_base = "sms"

    @abstractmethod
    def send(
        self,
        notification_type: str,
        context_dict: Dict,
        recipients: List[str],
        subject: Optional[str],
        reply_to: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
    ):
        raise NotImplementedError


class SmsSendingStrategy(NotificationServiceStrategy):
    def send(
        self,
        notification_type: str,
        context_dict: Dict,
        recipients: List[str],
        subject: Optional[str],
        reply_to: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
    ):
        # TODO Add SMS Client
        # sms_client = ClickSendSMSClient(settings.CLICKSEND_API_KEY, settings.CLICKSEND_BASE_URL)
        template_name = f"{self.sms_template_base}/{notification_type}/body.txt"
        sms_text = render_to_string(template_name, context_dict)
        if settings.DEBUG:
            logging.info(f"Sending SMS {sms_text}")
        # phone_number = recipients[0]
        # try:
        #     sms_client.send_sms(sms_text, phone_number, None)
        # except ClickSendError as exc:
        #     logging.error("Error sending sms")


class EmailSendingStrategy(NotificationServiceStrategy):
    def send(
        self,
        notification_type: str,
        context_dict: Dict,
        recipients: List[str],
        subject: Optional[str],
        reply_to: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
    ):
        """Generate email notification message, could be used for any `notification_type`."""
        components = {}
        for item in ("subject.txt", "body.txt", "body.html"):
            components[item] = render_to_string(
                f"{self.email_template_base}/{notification_type}/{item}", context_dict
            )
        msg = EmailMultiAlternatives(
            headers={
                "Reply-To": reply_to if reply_to else settings.DEFAULT_FROM_EMAIL,
            },
            subject=components["subject.txt"].strip() if subject is None else subject,
            body=components["body.txt"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            cc=cc,
            bcc=bcc,
        )
        msg.attach_alternative(components["body.html"], "text/html")
        msg.send()
        return True


class NotificationService:
    def __init__(self, transport_type: NotificationTransportChoices):
        if transport_type == NotificationTransportChoices.sms:
            self.notification = SmsSendingStrategy()
        elif transport_type == NotificationTransportChoices.email:
            self.notification = EmailSendingStrategy()
        else:
            raise APIException(
                f"Unsupported transport type {transport_type}"
            )

    def send(
        self,
        *,
        notification_type: str,
        context_dict: Dict,
        recipients: List[str],
        subject: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ):
        return self.notification.send(
            notification_type=notification_type,
            context_dict=context_dict,
            recipients=recipients,
            subject=subject,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
        )
