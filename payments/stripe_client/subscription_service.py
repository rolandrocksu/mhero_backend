import logging

import stripe
from datetime import datetime
from django.utils.timezone import make_aware

from payments.choices import SubscriptionStatusChoices
from payments.models import Subscription, SubscriptionPrice


class SubscriptionService:
    @staticmethod
    def upgrade_or_downgrade_subscription(
            user,
            new_price_id,
            proration_behavior=None
    ):
        try:
            subscription = Subscription.objects.filter(
                user=user,
                status=SubscriptionStatusChoices.ACTIVE
            ).first()
            stripe_subscription_id = subscription.stripe_subscription_id
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)

            current_item_id = stripe_subscription["items"]["data"][0]["id"]

            modify_params = {
                "items": [{"id": current_item_id, "price": new_price_id}],
            }
            if proration_behavior is not None:
                modify_params["proration_behavior"] = proration_behavior

            updated_subscription = stripe.Subscription.modify(
                stripe_subscription_id, **modify_params
            )

            # TODO invoice doesnt work in test mode
            invoice_id = updated_subscription.get("latest_invoice")
            invoice = stripe.Invoice.retrieve(invoice_id)
            final_price = invoice.total

            subscription.subscription_price = SubscriptionPrice.objects.get(
                stripe_price_id=new_price_id
            )
            subscription.final_price = final_price
            subscription.invoice_id = invoice_id
            subscription.status = updated_subscription["status"]
            subscription.current_period_start = make_aware(
                datetime.fromtimestamp(updated_subscription["current_period_start"])
            )
            subscription.current_period_end = make_aware(
                datetime.fromtimestamp(updated_subscription["current_period_end"])
            )
            subscription.save()

            logging.info(f"Subscription {subscription.id} has been updated")
            return True, "Subscription updated successfully"

        except Subscription.DoesNotExist:
            logging.error(f"No active subscription found for user={user}")
            return False, "No active subscription found"
        except Exception as e:
            logging.error(f"Exception occurred while updating subscription: {e}")
            return False, str(e)
