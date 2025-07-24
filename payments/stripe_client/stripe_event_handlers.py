import logging
from datetime import datetime

import stripe
from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND
)

from accounts.models import MheroUser
from payments.choices import SubscriptionStatusChoices
from payments.models import Subscription, SubscriptionPlan, SubscriptionPrice, TransactionHistory
from payments.services import get_object_with_retry


class StripeEventHandler:

    @staticmethod
    def retrieve_and_create_subscription(stripe_subscription_id, user=None):
        stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        price_id = stripe_subscription["items"]["data"][0]["price"]["id"]

        subscription_price = get_object_with_retry(SubscriptionPrice, stripe_price_id=price_id)
        if not user:
            sessions = stripe.checkout.Session.list(subscription=stripe_subscription_id)

            if not sessions.data:
                logging.error(f"No session found for subscription {stripe_subscription_id}")
                return False, Response(
                    {"error": "Checkout session not found"},
                    status=HTTP_404_NOT_FOUND
                )

            session = sessions.data[0]
            user_id = session.get("client_reference_id")

            user = MheroUser.objects.get(id=user_id)

        # Check for the correct field for the start date
        start_date = stripe_subscription.get("start", stripe_subscription.get("created"))
        if start_date:
            start_date = make_aware(datetime.fromtimestamp(start_date))
        else:
            logging.error(f"Start date not found for subscription {stripe_subscription_id}")
            return False, Response({"error": "Start date not found"}, status=HTTP_404_NOT_FOUND)
        try:
            subscription = Subscription.objects.create(
                user=user,
                stripe_subscription_id=stripe_subscription_id,
                subscription_price=subscription_price,
                status=stripe_subscription["status"],
                start_date=start_date,
                current_period_start=make_aware(
                    datetime.fromtimestamp(stripe_subscription["current_period_start"])
                ),
                current_period_end=make_aware(
                    datetime.fromtimestamp(stripe_subscription["current_period_end"])
                ),
            )
            return True, subscription
        except Exception as e:
            return False, str(e)

    @staticmethod
    def handle_checkout_completed(event):
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        stripe_subscription_id = session.get("subscription")

        if not user_id or not stripe_subscription_id:
            logging.error(
                f"Missing data for subscription "
                f"id={stripe_subscription_id} or client_reference_id={user_id}"
            )
            return Response(
                {"error": "Missing user ID or subscription ID"},
                status=HTTP_400_BAD_REQUEST
            )

        try:
            user = MheroUser.objects.get(id=user_id)
        except MheroUser.DoesNotExist:
            logging.error(f"User not found {user_id}")
            return Response(
                {"error": "User not found"},
                status=HTTP_404_NOT_FOUND
            )

        succ, response = StripeEventHandler.retrieve_and_create_subscription(
            stripe_subscription_id, user
        )
        if not succ:
            return response

        return Response({"status": "subscription created"}, status=HTTP_200_OK)

    @staticmethod
    def handle_invoice_payment_succeeded(event):
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice["subscription"]

        final_price = invoice['total']
        invoice_id = invoice['id']

        try:
            subscription = get_object_with_retry(
                Subscription,
                stripe_subscription_id=stripe_subscription_id
            )
        except Subscription.DoesNotExist:
            logging.warning(
                f"Subscription not found, retrieving from Stripe: {stripe_subscription_id}"
            )
            succ, response = StripeEventHandler.retrieve_and_create_subscription(
                stripe_subscription_id
            )
            if not succ:
                return response

            subscription = response

        subscription.final_price = final_price
        subscription.invoice_id = invoice_id
        subscription.status = SubscriptionStatusChoices.ACTIVE
        subscription.save()

        TransactionHistory.objects.create(
            user=subscription.user,
            subscription=subscription,
            invoice_id=invoice_id,
            event_type='payment_succeeded',
            amount=final_price,
            status="succeeded",
            event_data=invoice
        )

        return Response({"status": "subscription updated"}, status=HTTP_200_OK)

    @staticmethod
    def handle_invoice_payment_failed(event):
        invoice = event["data"]["object"]
        stripe_subscription_id = invoice["subscription"]

        try:
            subscription = get_object_with_retry(
                Subscription,
                stripe_subscription_id=stripe_subscription_id
            )
        except Subscription.DoesNotExist:
            logging.warning(
                f"Subscription not found, retrieving from Stripe: {stripe_subscription_id}"
            )
            succ, subscription = StripeEventHandler.retrieve_and_create_subscription(
                stripe_subscription_id
            )

        subscription.status = SubscriptionStatusChoices.PAST_DUE
        subscription.save()

        logging.info(f"Subscription {stripe_subscription_id} marked as past_due.")
        return Response(
            {"status": "payment failed - subscription updated to past_due"},
            status=HTTP_200_OK
        )

    @staticmethod
    def handle_subscription_updated(event):
        stripe_subscription = event["data"]["object"]
        stripe_subscription_id = stripe_subscription["id"]
        status = stripe_subscription["status"]
        invoice_id = stripe_subscription.get("latest_invoice")

        try:
            subscription = get_object_with_retry(
                Subscription,
                stripe_subscription_id=stripe_subscription_id
            )
        except Subscription.DoesNotExist:
            logging.error(
                f"Subscription not found "
                f"stripe_subscription_id={stripe_subscription_id}"
            )
            return Response({"error": "Subscription not found"}, status=HTTP_404_NOT_FOUND)

        subscription.status = status
        subscription.invoice_id = invoice_id
        subscription.current_period_start = make_aware(
            datetime.fromtimestamp(stripe_subscription["current_period_start"])
        )
        subscription.current_period_end = make_aware(
            datetime.fromtimestamp(stripe_subscription["current_period_end"])
        )
        subscription.save()

        return Response({"status": "subscription updated"}, status=HTTP_200_OK)

    @staticmethod
    def handle_subscription_deleted(event):
        stripe_subscription = event["data"]["object"]
        stripe_subscription_id = stripe_subscription["id"]

        try:
            subscription = get_object_with_retry(
                Subscription,
                stripe_subscription_id=stripe_subscription_id
            )
        except Subscription.DoesNotExist:
            logging.error(
                f"Subscription not found "
                f"stripe_subscription_id={stripe_subscription_id}"
            )
            return Response({"error": "Subscription not found"}, status=HTTP_404_NOT_FOUND)

        subscription.status = SubscriptionStatusChoices.CANCELED
        subscription.save()

        return Response({"status": "subscription canceled"}, status=HTTP_200_OK)

    @staticmethod
    def handle_product_created(event):
        product = event["data"]["object"]

        SubscriptionPlan.objects.create(
            name=product["name"],
            stripe_plan_id=product["id"],
        )

        logging.info(f"Product created: {product['id']} - {product['name']}")
        return Response({"status": "product created"}, status=HTTP_200_OK)

    @staticmethod
    def handle_product_updated(event):
        product = event["data"]["object"]

        # Update the SubscriptionPlan if it exists
        try:
            plan = get_object_with_retry(SubscriptionPlan, stripe_plan_id=product["id"])
            # plan = SubscriptionPlan.objects.get(stripe_plan_id=product["id"])
            plan.name = product["name"]
            plan.save()
            logging.info(f"Product updated: {product['id']} - {product['name']}")
            return Response({"status": "product updated"}, status=HTTP_200_OK)
        except SubscriptionPlan.DoesNotExist:
            logging.error(f"Product not found for update: {product['id']}")
            return Response({"error": "Product not found"}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_price_created(event):
        price_data = event["data"]["object"]
        stripe_price_id = price_data["id"]
        stripe_plan_id = price_data["product"]
        unit_amount = price_data["unit_amount"]
        pricing_type = price_data.get("type", "recurring")

        try:
            plan = get_object_with_retry(SubscriptionPlan, stripe_plan_id=stripe_plan_id)
            # plan = SubscriptionPlan.objects.get(stripe_plan_id=stripe_plan_id)
        except SubscriptionPlan.DoesNotExist:
            logging.error(f"Plan not found for price creation: {stripe_plan_id}")
            return Response({"error": "Plan not found"}, status=404)

        SubscriptionPrice.objects.create(
            name=f"{plan.name} Price",
            pricing_type=pricing_type,
            stripe_price_id=stripe_price_id,
            price=unit_amount,
            subscription_plan=plan
        )

        logging.info(f"Price created for plan {plan.name}: ${unit_amount}")
        return Response({"status": "price created"}, status=200)

    @staticmethod
    def handle_price_updated(event):
        price_data = event["data"]["object"]
        stripe_price_id = price_data["id"]
        unit_amount = price_data["unit_amount"]
        # stripe_plan_id = price_data["product"]

        try:
            price = get_object_with_retry(SubscriptionPrice, stripe_price_id=stripe_price_id)
            # price = SubscriptionPrice.objects.get(stripe_price_id=stripe_price_id)
            price.price = unit_amount
            price.save()
            logging.info(f"Price updated for plan {price.name}: ${unit_amount}")
            return Response({"status": "price updated"}, status=200)
        except SubscriptionPlan.DoesNotExist:
            logging.error(f"Price not found for price update: {stripe_price_id}")
            return Response({"error": "Plan not found"}, status=404)
