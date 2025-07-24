from rest_framework import serializers
from .models import Subscription, SubscriptionPlan, SubscriptionPrice, TransactionHistory


class SubscriptionPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPrice
        fields = ['name', 'stripe_price_id', 'price', 'pricing_type']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    subscription_prices = SubscriptionPriceSerializer(read_only=True, many=True)

    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'stripe_plan_id', 'subscription_prices']


class ActiveSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="subscription_price.name")
    price_id = serializers.CharField(source="subscription_price.stripe_price_id")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan_name",
            "price_id",
            "status",
            "current_period_start",
            "current_period_end",
        ]


class CheckoutSessionSerializer(serializers.Serializer):
    price_id = serializers.CharField(max_length=100)
    coupon_code = serializers.CharField(max_length=100, required=False)


class UpdateSubscriptionSerializer(serializers.Serializer):
    price_id = serializers.CharField(max_length=100)


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = ['id', 'invoice_id', 'event_type', 'amount', 'status', 'created_at']
