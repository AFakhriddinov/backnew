import json
import os
from decimal import Decimal

from django.utils import timezone

from billing.models import AgentBalance 
from ..utils.exception import PaycomException
from ..utils.format import BaseFormat
from ..authorize import MerchantAPI

from ..validator import AgentBalanceController 
from ..http import PaycomRequest, PaycomResponse

from ..transaction import Transactions

# from ...models import AccountBalance


class PaycomAPI:
    """
    https://developer.help.paycom.uz/ru/protokol-merchant-api/skhema-vzaimodeystviya
    https://developer.help.paycom.uz/ru/vzaimodeystvie-protokolov-merchant-api-i-subscribe-api
    https://developer.help.paycom.uz/ru/metody-merchant-api
    """

    method = None
    request = None
    response = None
    merchant = None
    json_content = None
    formatter = BaseFormat()

    def __init__(self, request):
        if request.method == "POST":
            self.request = PaycomRequest(request=request)
            self.method = self.request.method
            self.response = PaycomResponse(request=self.request)
            self.merchant = MerchantAPI(request=request)
        else:
            raise PaycomException(
                request_id=None, message="No post request detected", code=-32300
            )

    def run(self):
        print("self.merchant.authorize()", self.merchant.authorize())
        if self.merchant.authorize():
            try:
                if self.method == "CheckPerformTransaction":
                    self.check_perform_transaction()
                elif self.method == "CreateTransaction":
                    self.create_transaction()
                elif self.method == "PerformTransaction":
                    self.perform_transaction()
                elif self.method == "CancelTransaction":
                    self.cancel_transaction()
                elif self.method == "CheckTransaction":
                    self.check_transaction()
                elif self.method == "GetStatement":
                    self.get_statement()
                elif self.method == "ChangePassword":
                    self.change_password()
                else:
                    self.json_content = self.response.error(
                        code=PaycomException.ERROR_METHOD_NOT_FOUND,
                        message="Method not found",
                        data=self.request.method,
                    )
            except PaycomException:
                self.json_content = self.response.error(
                    code=PaycomException.ERROR_INVALID_JSON_RPC_OBJECT,
                    message="Invalid RPC Object",
                    data="rpc data",
                )
        else:
            self.json_content = self.response.error(
                code=PaycomException.ERROR_INSUFFICIENT_PRIVILEGE,
                message="Invalid login/password",
                data="account",
            )
        return self.json_content

    def check_perform_transaction(self):
        contract = AgentBalanceController(request_id=self.request.id)
        if contract.validate(account_params=self.request.params):
            """
            Comment: Contract successfully validated
            """
            data = {"result": contract.response_message}
            self.json_content = json.dumps(data)
        else:
            self.json_content = self.response.send(
                result=None, error=contract.response_message
            )

    def create_transaction(self):
        transaction = Transactions(params=self.request.params)
        if transaction.exist():
            """
            Comment: If transaction already exists,
            then check transaction state is available and time is not expired
            """
            if transaction.check_transaction_state():
                if transaction.transaction_is_expired():
                    transaction.cancel_transaction(
                        reason=Transactions.REASON_CANCELLED_BY_TIMEOUT
                    )
                    """
                        Comment: If transaction's time is expired,
                        cancel transaction and return error message code: -31008
                    """
                    self.json_content = self.response.error(
                        code=Transactions.TRANSACTION_CAN_NOT_PERFORM,
                        message="Transaction is expired.",
                        data="timeout",
                    )
                else:
                    """
                    Comment: If transaction's time is not expired,
                    return transaction details
                    """
                    self.json_content = transaction.return_transaction_details()
            else:
                """
                Comment: If transaction not exist, return error message code: -31008
                """
                self.json_content = self.response.error(
                    code=Transactions.TRANSACTION_CAN_NOT_PERFORM,
                    message="Transaction found, but is not active.",
                    data="timeout",
                )
        else:
            """
            Comment: If transaction not exist, try to create new one
            """
            user = AgentBalanceController(request_id=self.request.id)
            if user.validate(account_params=self.request.params) is False:
                self.json_content = self.response.send(
                    result=None, error=user.response_message
                )
            else:
                now_in_milliseconds = (
                    self.formatter.millisecond_timestamp_from_utc_to_time_zone(
                        utc_datetime=timezone.now()
                    )
                )
                if (
                    now_in_milliseconds - self.request.params["time"]
                ) > Transactions.TIMEOUT:
                    self.json_content = self.response.error(
                        code=PaycomException.ERROR_INVALID_ACCOUNT,
                        message="Transaction is expired.",
                        data="timeout",
                    )
                else:
                    transaction.save_transaction()
                    self.json_content = transaction.return_transaction_details()

    def perform_transaction(self):
        transaction = Transactions(params=self.request.params)
        if transaction.exist():
            if transaction.check_transaction_state(state=Transactions.STATE_CREATED):
                if transaction.transaction_is_expired():
                    transaction.cancel_transaction(
                        reason=Transactions.REASON_CANCELLED_BY_TIMEOUT
                    )
                    """
                        Comment: If transaction's time is expired,
                        cancel transaction and return error message code: -31008
                    """
                    self.json_content = self.response.error(
                        code=Transactions.TRANSACTION_CAN_NOT_PERFORM,
                        message="Transaction is expired.",
                        data="created_at " + str(transaction.transaction.created_at),
                    )
                else:
                    transaction.complete_transaction()
                    self.json_content = transaction.return_transaction_details(
                        field="perform_time"
                    )
            elif transaction.check_transaction_state(
                state=Transactions.STATE_COMPLETED
            ):
                """
                Comment: Return transaction details if transaction was completed
                """
                self.json_content = transaction.return_transaction_details(
                    field="perform_time"
                )
            else:
                self.json_content = self.response.error(
                    code=Transactions.TRANSACTION_CAN_NOT_PERFORM,
                    message="Transaction state is not valid.",
                    data=transaction.transaction.state,
                )
        else:
            self.json_content = self.response.error(
                code=Transactions.TRANSACTION_NOT_FOUND,
                message="Transaction is not found",
                data=transaction.paycom_transaction_id,
            )

    def cancel_transaction(self):
        transaction = Transactions(params=self.request.params)
        if transaction.exist():
            if transaction.check_transaction_state(state=Transactions.STATE_CREATED):
                transaction.cancel_transaction(reason=self.request.params["reason"])
                self.json_content = transaction.return_transaction_details(
                    field="cancel_time"
                )
            elif transaction.check_transaction_state(
                state=Transactions.STATE_COMPLETED
            ):
                balans = transaction.transaction.credit
                if Decimal(balans.balance) >= Decimal(transaction.transaction.amount):
                    balans.balance = balans.balance - transaction.transaction.amount
                    balans.save()
                    transaction.cancel_transaction(
                        reason="Payme orqali qilingan tolovni qaytarildi",
                        state=Transactions.STATE_CANCELLED_AFTER_COMPLETE,
                    )
                    self.json_content = transaction.return_transaction_details(
                        field="cancel_time"
                    )

                if transaction.transaction.state == 2:
                    self.json_content = self.response.error(
                        code=Transactions.TRANSACTION_CAN_NOT_CANCEL,
                        message="Transaction can not be cancelled.",
                        data=transaction.transaction.state,
                    )
                else:
                    print("STATE_CANCELLED_AFTER_COMPLETE")
                    transaction.cancel_transaction(
                        reason=self.request.params["reason"],
                        state=Transactions.STATE_CANCELLED_AFTER_COMPLETE,
                    )
                    self.json_content = transaction.return_transaction_details(
                        field="cancel_time"
                    )
            else:
                self.json_content = transaction.return_transaction_details(
                    field="cancel_time"
                )
        else:
            self.json_content = self.response.error(
                code=Transactions.TRANSACTION_NOT_FOUND,
                message="Transaction is not found",
                data=transaction.paycom_transaction_id,
            )

    def check_transaction(self):
        transaction = Transactions(params=self.request.params)
        if transaction.exist():
            self.json_content = transaction.get_transaction_details()
        else:
            self.json_content = self.response.error(
                code=Transactions.TRANSACTION_NOT_FOUND,
                message="Transaction is not found",
                data=transaction.paycom_transaction_id,
            )

    # def get_statement(self):
    #     all_transactions = Transactions.get_statement(
    #         _from=self.request.params["from"], _to=self.request.params["to"]
    #     )
    #     self.json_content = all_transactions

    # def change_password(self):
    #     try:
    #         if (
    #             self.request.params["password"]
    #             != os.environ["PAYCOM_PROTOCOL_APP_TESTKEY"]
    #         ):
    #             os.environ["PAYCOM_PROTOCOL_APP_TESTKEY"] = self.request.params[
    #                 "password"
    #             ]
    #             data = {"id": self.request.id, "result": {"success": True}}
    #         else:
    #             data = {
    #                 "code": -32504,
    #                 "message": {
    #                     "ru": "Ошибка при авторизации",
    #                     "uz": "Avtorizatsiyada xatolik",
    #                     "en": "Error during authorization",
    #                 },
    #                 "data": None,
    #                 "id": self.request.id,
    #             }
    #         self.json_content = json.dumps(data)
    #     except:
    #         self.json_content = self.response.error(
    #             code=PaycomException.ERROR_INVALID_JSON_RPC_OBJECT,
    #             message="Invalid RPC Object",
    #             data="rpc data",
    #         )
