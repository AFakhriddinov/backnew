import os
from base64 import standard_b64decode
from APIproject.settings import DEBUG

MERCHANT = "6030e0f1a10b214d8d11d487"
PROD_KEY = r"@ZGAbrOf%dQJujsWnj0cFAZXQrFVWPREBFRF"
TEST_KEY = "Be&PWF1@e7@%AsrJ0NcDoFPInGstmZooJ?sZ"

class MerchantAPI:
    header = None
    auth_data = None

    def __init__(self, request):
        self.header = request.META.get("HTTP_AUTHORIZATION", None)
        self.auth_data = self.header.split()[1] if self.header is not None else ""

    def authorize(self):
        if "PAYCOM_AUCTION_BALANCE_APP_KEY" not in os.environ:
            if DEBUG:
                os.environ["PAYCOM_AUCTION_BALANCE_APP_KEY"] = TEST_KEY
            else:
                os.environ["PAYCOM_AUCTION_BALANCE_APP_KEY"] = PROD_KEY

        key = os.environ["PAYCOM_AUCTION_BALANCE_APP_KEY"]
        merchant_auth = f"Paycom:{key}"
        paycom_auth = standard_b64decode(self.auth_data).decode("utf-8")
        if merchant_auth != paycom_auth or self.header is None:
            return False
        return True
