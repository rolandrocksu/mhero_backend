import logging
import requests
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN
)
from rest_framework.views import APIView

from .choices import SubscriptionStatusChoices
from .models import SubscriptionPlan, TransactionHistory
from .serializers import (
    ActiveSubscriptionSerializer,
    CheckoutSessionSerializer,
    SubscriptionPlanSerializer,
    UpdateSubscriptionSerializer,
    TransactionHistorySerializer,
)
from payments.stripe_client.stripe_event_handlers import StripeEventHandler
from .stripe_client.subscription_service import SubscriptionService

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = CheckoutSessionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            price_id = serializer.validated_data['price_id']
            coupon_code = serializer.validated_data.get('coupon_code')
            user = self.request.user
            self.ensure_stripe_customer(user)

            discounts = []
            if coupon_code:
                try:
                    coupon = stripe.Coupon.retrieve(coupon_code)
                    discounts = [{"coupon": coupon.id}]
                except Exception as e:
                    return Response(
                        {"error": f"Invalid coupon code {e}"},
                        status=HTTP_400_BAD_REQUEST
                    )

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                client_reference_id=str(user.id),
                customer=user.stripe_customer_id,
                discounts=discounts,
            )

            return Response({'sessionId': session.id, 'url': session.url}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def ensure_stripe_customer(user):
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )
            user.stripe_customer_id = customer['id']
            user.save()

        else:
            stripe.Customer.modify(
                user.stripe_customer_id,
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )


class StripeWebhookView(APIView):
    permission_classes = []
    authentication_classes = []
    schema = None

    def post(self, request, *args, **kwargs):
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logging.error("Webhook error while parsing basic request." + str(e))
            return Response({"error": "Invalid payload"}, status=HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            logging.error("Webhook signature verification failed." + str(e))
            return Response({"error": "Invalid signature"}, status=HTTP_400_BAD_REQUEST)

        event_type = event["type"]
        logging.info(f"Received Stripe event: {event_type}")

        event_processor = {
            "checkout.session.completed": StripeEventHandler.handle_checkout_completed,
            "invoice.payment_succeeded": StripeEventHandler.handle_invoice_payment_succeeded,
            # "invoice.payment_failed": StripeEventHandler.handle_invoice_payment_failed,
            "customer.subscription.updated": StripeEventHandler.handle_subscription_updated,
            "customer.subscription.deleted": StripeEventHandler.handle_subscription_deleted,
            "product.created": StripeEventHandler.handle_product_created,
            "product.updated": StripeEventHandler.handle_product_updated,
            "price.created": StripeEventHandler.handle_price_created,
            "price.updated": StripeEventHandler.handle_price_updated,
        }

        if event_type in event_processor.keys():
            return event_processor[event_type](event)

        logging.info(f"Ignored Stripe event: {event_type}")
        return Response({'status': 'ignored'}, status=209)


class SubscriptionPlanList(ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class RetrieveStripeCouponsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve all coupons from Stripe
            coupons = stripe.Coupon.list()

            coupon_data = [{
                "id": coupon["id"],
                "name": coupon.get("name"),
                "percent_off": coupon.get("percent_off"),
                "amount_off": coupon.get("amount_off"),
                "currency": coupon.get("currency"),
                "duration": coupon.get("duration"),
                "duration_in_months": coupon.get("duration_in_months"),
            } for coupon in coupons["data"]]

            return Response({"coupons": coupon_data}, status=HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


class ActiveSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = self.request.user.subscriptions.filter(
            status=SubscriptionStatusChoices.ACTIVE
        ).order_by('-current_period_end')
        if subscriptions:
            serializer = ActiveSubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({"detail": "No active subscription found"}, status=HTTP_404_NOT_FOUND)


class UpdateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user
        serializer = UpdateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_price_id = serializer.validated_data["price_id"]

        success, message = SubscriptionService.upgrade_or_downgrade_subscription(
            user, new_price_id
        )

        if not success:
            return Response({"error": message}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": message}, status=HTTP_200_OK)


class TransactionHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionHistorySerializer

    def get_queryset(self):
        user = self.request.user
        return TransactionHistory.objects.filter(user=user).order_by('-created_at')


class DownloadInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        user = self.request.user

        try:
            if not user.stripe_customer_id:
                return Response(
                    {"detail": "User Stripe customer ID not found."},
                    status=HTTP_400_BAD_REQUEST,
                )

            invoice = stripe.Invoice.retrieve(invoice_id)

            if invoice.customer != user.stripe_customer_id:
                return Response(
                    {"detail": "Invoice does not belong to the authenticated user."},
                    status=HTTP_403_FORBIDDEN,
                )

            pdf_url = invoice.invoice_pdf
            if not pdf_url:
                return Response(
                    {"detail": "PDF URL not found for this invoice."},
                    status=HTTP_400_BAD_REQUEST,
                )

            response = requests.get(pdf_url)
            if response.status_code != 200:
                return Response(
                    {"detail": "Failed to download the invoice PDF."},
                    status=HTTP_400_BAD_REQUEST,
                )

            pdf_content = response.content
            http_response = HttpResponse(pdf_content, content_type='application/pdf')
            http_response['Content-Disposition'] = (
                f'attachment; filename="invoice_{invoice_id}.pdf"'
            )
            return http_response

        except stripe.error.InvalidRequestError:
            return Response(
                {"detail": "Invalid invoice ID."},
                status=HTTP_400_BAD_REQUEST
            )
        except stripe.error.StripeError as e:
            return Response(
                {"detail": str(e)},
                status=HTTP_400_BAD_REQUEST
            )
