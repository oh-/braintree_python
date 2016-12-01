from tests.test_helper import *
from braintree.test.nonces import Nonces

class TestMerchantGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = BraintreeGateway(
            client_id="client_id$development$signup_client_id",
            client_secret="client_secret$development$signup_client_secret"
        )

    def test_create_merchant(self):
        gateway = BraintreeGateway(
            client_id="client_id$development$integration_client_id",
            client_secret="client_secret$development$integration_client_secret"
        )

        result = gateway.merchant.create({
            "email": "name@email.com",
            "country_code_alpha3": "USA",
            "payment_methods": ["credit_card", "paypal"]
        })

        merchant = result.merchant
        self.assertIsNotNone(merchant.id)
        self.assertEqual(merchant.email, "name@email.com")
        self.assertEqual(merchant.country_code_alpha3, "USA")
        self.assertEqual(merchant.country_code_alpha2, "US")
        self.assertEqual(merchant.country_code_numeric, "840")
        self.assertEqual(merchant.country_name, "United States of America")
        self.assertEqual(merchant.company_name, "name@email.com")
        self.assertTrue(result.is_success)

        credentials = result.credentials
        self.assertIsNotNone(credentials.access_token)
        self.assertIsNotNone(credentials.expires_at)
        self.assertEqual("bearer", credentials.token_type)

    def test_returns_error_with_invalid_payment_methods(self):
        gateway = BraintreeGateway(
            client_id="client_id$development$integration_client_id",
            client_secret="client_secret$development$integration_client_secret"
        )

        result = gateway.merchant.create({
            "email": "name@email.com",
            "country_code_alpha3": "USA",
            "payment_methods": ["fake_money"]
        })

        self.assertFalse(result.is_success)
        self.assertIn("One or more payment methods passed are not accepted.", result.message)

        payment_method_errors = result.errors.for_object("merchant").on("payment_methods")
        self.assertEqual(1, len(payment_method_errors))
        self.assertEqual(payment_method_errors[0].code, ErrorCodes.Merchant.PaymentMethodsAreInvalid)

    def test_create_paypal_only_merchant_that_accepts_multiple_currencies(self):
        result = self.gateway.merchant.create({
            "email": "name@email.com",
            "country_code_alpha3": "USA",
            "payment_methods": ["paypal"],
            "currencies": ["GBP", "USD"],
            "paypal_account": {
                "client_id": "paypal_client_id",
                "client_secret": "paypal_client_secret"
            }
        })

        merchant = result.merchant
        self.assertIsNotNone(merchant.id)
        self.assertEqual(merchant.email, "name@email.com")
        self.assertEqual(merchant.country_code_alpha3, "USA")
        self.assertEqual(merchant.country_code_alpha2, "US")
        self.assertEqual(merchant.country_code_numeric, "840")
        self.assertEqual(merchant.country_name, "United States of America")
        self.assertEqual(merchant.company_name, "name@email.com")
        self.assertTrue(result.is_success)

        credentials = result.credentials
        self.assertIsNotNone(credentials.access_token)
        self.assertIsNotNone(credentials.expires_at)
        self.assertEqual("bearer", credentials.token_type)

        merchant_accounts = merchant.merchant_accounts
        self.assertEqual(2, len(merchant_accounts))

        usd_merchant_account = [ma for ma in merchant_accounts if ma.id == "USD"][0]
        self.assertTrue(usd_merchant_account.default)
        self.assertEqual(usd_merchant_account.currency_iso_code, "USD")

        gbp_merchant_account = [ma for ma in merchant_accounts if ma.id == "GBP"][0]
        self.assertFalse(gbp_merchant_account.default)
        self.assertEqual(gbp_merchant_account.currency_iso_code, "GBP")

    def test_allows_creation_of_non_US_merchant_if_onboarding_application_is_internal(self):
        result = self.gateway.merchant.create({
            "email": "name@email.com",
            "country_code_alpha3": "JPN",
            "payment_methods": ["paypal"],
            "paypal_account": {
                "client_id": "paypal_client_id",
                "client_secret": "paypal_client_secret"
            }
        })

        merchant = result.merchant
        self.assertIsNotNone(merchant.id)
        self.assertEqual(merchant.email, "name@email.com")
        self.assertEqual(merchant.country_code_alpha3, "JPN")
        self.assertEqual(merchant.country_code_alpha2, "JP")
        self.assertEqual(merchant.country_code_numeric, "392")
        self.assertEqual(merchant.country_name, "Japan")
        self.assertEqual(merchant.company_name, "name@email.com")
        self.assertTrue(result.is_success)

        credentials = result.credentials
        self.assertIsNotNone(credentials.access_token)
        self.assertIsNotNone(credentials.expires_at)
        self.assertEqual("bearer", credentials.token_type)

        merchant_accounts = merchant.merchant_accounts
        self.assertEqual(1, len(merchant_accounts))

        usd_merchant_account = merchant_accounts[0]
        self.assertTrue(usd_merchant_account.default)
        self.assertEqual(usd_merchant_account.currency_iso_code, "JPY")

    def test_defaults_to_USD_for_non_US_merchant_if_onboarding_application_is_internal_and_country_currency_not_supported(self):
        result = self.gateway.merchant.create({
            "email": "name@email.com",
            "country_code_alpha3": "YEM",
            "payment_methods": ["paypal"],
            "paypal_account": {
                "client_id": "paypal_client_id",
                "client_secret": "paypal_client_secret"
            }
        })

        merchant = result.merchant
        self.assertIsNotNone(merchant.id)
        self.assertEqual(merchant.email, "name@email.com")
        self.assertEqual(merchant.country_code_alpha3, "YEM")
        self.assertEqual(merchant.country_code_alpha2, "YE")
        self.assertEqual(merchant.country_code_numeric, "887")
        self.assertEqual(merchant.country_name, "Yemen")
        self.assertEqual(merchant.company_name, "name@email.com")
        self.assertTrue(result.is_success)

        credentials = result.credentials
        self.assertIsNotNone(credentials.access_token)
        self.assertIsNotNone(credentials.expires_at)
        self.assertEqual("bearer", credentials.token_type)

        merchant_accounts = merchant.merchant_accounts
        self.assertEqual(1, len(merchant_accounts))

        usd_merchant_account = merchant_accounts[0]
        self.assertTrue(usd_merchant_account.default)
        self.assertEqual(usd_merchant_account.currency_iso_code, "USD")
