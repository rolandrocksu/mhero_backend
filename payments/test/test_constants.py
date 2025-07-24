from datetime import datetime, timedelta

import pytz

# Dynamically generate dates for the event
current_period_start = int(datetime.now(tz=pytz.UTC).timestamp())
current_period_end = int((datetime.now(tz=pytz.UTC) + timedelta(days=30)).timestamp())
created_date = int((datetime.now(tz=pytz.UTC) - timedelta(days=30)).timestamp())

CHECKOUT_SESSION_COMPLETED_EVENT = {
    "object": {
        "id": "cs_test_a1wE9798d4d9ftc9d5LaqxllET13iX87BZ5MfoZ2ok4ndAuPQ2yih5bsbd",
        "object": "checkout.session",
        "adaptive_pricing": None,
        "after_expiration": None,
        "allow_promotion_codes": None,
        "amount_subtotal": 12000,
        "amount_total": 12000,
        "automatic_tax": {
            "enabled": False,
            "liability": None,
            "status": None
        },
        "billing_address_collection": None,
        "cancel_url": "http://localhost:4200/cancel",
        "client_reference_id": "11",
        "client_secret": None,
        "collected_information": {
            "shipping_details": None
        },
        "consent": None,
        "consent_collection": None,
        "created": 1740124947,
        "currency": "usd",
        "currency_conversion": None,
        "custom_fields": [],
        "custom_text": {
            "after_submit": None,
            "shipping_address": None,
            "submit": None,
            "terms_of_service_acceptance": None
        },
        "customer": "cus_Rmz7cqfuNOT1Lg",
        "customer_creation": None,
        "customer_details": {
            "address": {
                "city": None,
                "country": "AM",
                "line1": None,
                "line2": None,
                "postal_code": None,
                "state": None
            },
            "email": "roland@mhero.com",
            "name": "Roland Poghosyan",
            "phone": None,
            "tax_exempt": "none",
            "tax_ids": []
        },
        "customer_email": None,
        "discounts": [],
        "expires_at": 1740211347,
        "invoice": "in_1QurDHCAmBA4OZOP6B5vj6In",
        "invoice_creation": None,
        "livemode": False,
        "locale": None,
        "metadata": {},
        "mode": "subscription",
        "payment_intent": None,
        "payment_link": None,
        "payment_method_collection": "always",
        "payment_method_configuration_details": None,
        "payment_method_options": {
            "card": {
                "request_three_d_secure": "automatic"
            }
        },
        "payment_method_types": [
            "card"
        ],
        "payment_status": "paid",
        "phone_number_collection": {
            "enabled": False
        },
        "recovered_from": None,
        "saved_payment_method_options": {
            "allow_redisplay_filters": [
                "always"
            ],
            "payment_method_remove": None,
            "payment_method_save": None
        },
        "setup_intent": None,
        "shipping_address_collection": None,
        "shipping_cost": None,
        "shipping_details": None,
        "shipping_options": [],
        "status": "complete",
        "submit_type": None,
        "subscription": "sub_123",
        "success_url": "http://localhost:4200/success",
        "total_details": {
            "amount_discount": 0,
            "amount_shipping": 0,
            "amount_tax": 0
        },
        "ui_mode": "hosted",
        "url": None
    },
    "previous_attributes": None
}

MOCK_SUBSCRIPTION_DATA = {
    "id": "sub_123",
    "status": "active",
    "items": {
        "data": [{"price": {"id": "price_basic_123"}}]
    },
    "current_period_start": current_period_start,
    "current_period_end": current_period_end,
    "created": created_date
}

MOCK_SESSION_LIST_DATA = {
    "data": [
        {
            "id": "cs_test_123",
            "client_reference_id": "11",
        }
    ]
}

CUSTOMER_SUBSCRIPTION_UPDATED_EVENT = {
    "object": {
        "id": "sub_123",
        "status": "Another status",
        "items": {
            "data": [{"price": {"id": "price_basic_123"}}]
        },
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "created": created_date
    }
}

CUSTOMER_SUBSCRIPTION_DELETED_EVENT = {
    "object": {
        "id": "sub_123",
        "status": "canceled"
    }
}

INVOICE_PAYMENT_SUCCEEDED_EVENT = {
    "object": {
        "id": "in_1QurDHCAmBA4OZOP6B5vj6In",
        "object": "invoice",
        "account_country": "US",
        "account_name": "Mhero",
        "account_tax_ids": None,
        "amount_due": 12000,
        "amount_paid": 12000,
        "amount_remaining": 0,
        "amount_shipping": 0,
        "application": None,
        "application_fee_amount": None,
        "attempt_count": 1,
        "attempted": True,
        "auto_advance": False,
        "automatic_tax": {
            "disabled_reason": None,
            "enabled": False,
            "liability": None,
            "status": None
        },
        "automatically_finalizes_at": None,
        "billing_reason": "subscription_create",
        "charge": "ch_3QurDICAmBA4OZOP1vf6GZS6",
        "collection_method": "charge_automatically",
        "created": 1740125039,
        "currency": "usd",
        "custom_fields": None,
        "customer": "cus_Rmz7cqfuNOT1Lg",
        "customer_address": None,
        "customer_email": "roland@mhero.com",
        "customer_name": "Roland Poghosyan",
        "customer_phone": None,
        "customer_shipping": None,
        "customer_tax_exempt": "none",
        "customer_tax_ids": [],
        "default_payment_method": None,
        "default_source": None,
        "default_tax_rates": [],
        "description": None,
        "discount": None,
        "discounts": [],
        "due_date": None,
        "effective_at": 1740125039,
        "ending_balance": 0,
        "footer": None,
        "from_invoice": None,
        "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1Q2nHVCAmBA4OZOP/?s=ap",
        "invoice_pdf": "https://pay.stripe.com/invoice/acct_1Q2nHVCAmBA4OZOP/pdf?s=ap",
        "issuer": {
            "type": "self"
        },
        "last_finalization_error": None,
        "latest_revision": None,
        "lines": {
            "object": "list",
            "data": [
                {
                    "id": "il_1QurDHCAmBA4OZOPe4GjvMLn",
                    "object": "line_item",
                    "amount": 12000,
                    "amount_excluding_tax": 12000,
                    "currency": "usd",
                    "description": "1 × Mhero Testing (at $120.00 / month)",
                    "discount_amounts": [],
                    "discountable": True,
                    "discounts": [],
                    "invoice": "in_1QurDHCAmBA4OZOP6B5vj6In",
                    "livemode": False,
                    "metadata": {},
                    "period": {
                        "end": 1742544239,
                        "start": 1740125039
                    },
                    "plan": {
                        "id": "price_basic_123",
                        "object": "plan",
                        "active": True,
                        "aggregate_usage": None,
                        "amount": 12000,
                        "amount_decimal": "12000",
                        "billing_scheme": "per_unit",
                        "created": 1739885601,
                        "currency": "usd",
                        "interval": "month",
                        "interval_count": 1,
                        "livemode": False,
                        "metadata": {},
                        "meter": None,
                        "nickname": None,
                        "product": "prod_RnRpgfshcqYGgS",
                        "tiers_mode": None,
                        "transform_usage": None,
                        "trial_period_days": None,
                        "usage_type": "licensed"
                    },
                    "pretax_credit_amounts": [],
                    "price": {
                        "id": "price_basic_123",
                        "object": "price",
                        "active": True,
                        "billing_scheme": "per_unit",
                        "created": 1739885601,
                        "currency": "usd",
                        "custom_unit_amount": None,
                        "livemode": False,
                        "lookup_key": None,
                        "metadata": {},
                        "nickname": None,
                        "product": "prod_RnRpgfshcqYGgS",
                        "recurring": {
                            "aggregate_usage": None,
                            "interval": "month",
                            "interval_count": 1,
                            "meter": None,
                            "trial_period_days": None,
                            "usage_type": "licensed"
                        },
                        "tax_behavior": "unspecified",
                        "tiers_mode": None,
                        "transform_quantity": None,
                        "type": "recurring",
                        "unit_amount": 12000,
                        "unit_amount_decimal": "12000"
                    },
                    "proration": False,
                    "proration_details": {
                        "credited_items": None
                    },
                    "quantity": 1,
                    "subscription": "sub_123",
                    "subscription_item": "si_RoUBUFWmz6Bcwq",
                    "tax_amounts": [],
                    "tax_rates": [],
                    "type": "subscription",
                    "unit_amount_excluding_tax": "12000"
                }
            ],
            "has_more": False,
            "total_count": 1,
            "url": "/v1/invoices/in_1QurDHCAmBA4OZOP6B5vj6In/lines"
        },
        "livemode": False,
        "metadata": {},
        "next_payment_attempt": None,
        "number": "FCB3EFA3-0023",
        "on_behalf_of": None,
        "paid": True,
        "paid_out_of_band": False,
        "payment_intent": "pi_3QurDICAmBA4OZOP1bTUUeav",
        "payment_settings": {
            "default_mandate": None,
            "payment_method_options": {
                "acss_debit": None,
                "bancontact": None,
                "card": {
                    "request_three_d_secure": "automatic"
                },
                "customer_balance": None,
                "konbini": None,
                "sepa_debit": None,
                "us_bank_account": None
            },
            "payment_method_types": None
        },
        "period_end": 1740125039,
        "period_start": 1740125039,
        "post_payment_credit_notes_amount": 0,
        "pre_payment_credit_notes_amount": 0,
        "quote": None,
        "receipt_number": None,
        "rendering": None,
        "shipping_cost": None,
        "shipping_details": None,
        "starting_balance": 0,
        "statement_descriptor": None,
        "status": "paid",
        "status_transitions": {
            "finalized_at": 1740125039,
            "marked_uncollectible_at": None,
            "paid_at": 1740125042,
            "voided_at": None
        },
        "subscription": "sub_123",
        "subscription_details": {
            "metadata": {}
        },
        "subtotal": 12000,
        "subtotal_excluding_tax": 12000,
        "tax": None,
        "test_clock": None,
        "total": 12000,
        "total_discount_amounts": [],
        "total_excluding_tax": 12000,
        "total_pretax_credit_amounts": [],
        "total_tax_amounts": [],
        "transfer_data": None,
        "webhooks_delivered_at": None
    },
    "previous_attributes": None
}
