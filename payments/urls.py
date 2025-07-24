from django.urls import path

from payments.views import (
    StripeWebhookView,
    SubscriptionPlanList,
    ActiveSubscriptionView,
    CreateCheckoutSession,
    RetrieveStripeCouponsView,
    UpdateSubscriptionView,
    TransactionHistoryView,
    DownloadInvoiceView
)

urlpatterns = [
    path(
        'create-checkout-session/',
        CreateCheckoutSession.as_view(),
        name='create_checkout_session'
    ),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('subscription/plans/', SubscriptionPlanList.as_view(), name='subscription_plans'),
    path('subscription/update/', UpdateSubscriptionView.as_view(), name='update-subscription'),
    path('stripe/coupons/', RetrieveStripeCouponsView.as_view(), name='retrieve-stripe-coupons'),
    path('subscriptions/active/', ActiveSubscriptionView.as_view(), name='active-subscription'),
    path(
        'transactions/',
        TransactionHistoryView.as_view(),
        name='transactions'
    ),
    path(
        'subscription/invoice/<str:invoice_id>/',
        DownloadInvoiceView.as_view(),
        name='download-invoice'),
]
