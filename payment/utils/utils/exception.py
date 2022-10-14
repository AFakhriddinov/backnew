class PaycomException(Exception):
    ERROR_NOT_POST_REQUEST = -32300
    ERROR_CAN_NOT_PARSING_JSON = -32700
    ERROR_INTERNAL_SYSTEM = -32400
    ERROR_INSUFFICIENT_PRIVILEGE = -32504
    ERROR_INVALID_JSON_RPC_OBJECT = -32600
    ERROR_METHOD_NOT_FOUND = -32601
    ERROR_INVALID_AMOUNT = -31001
    ERROR_TRANSACTION_NOT_FOUND = -31003
    ERROR_INVALID_ACCOUNT = -31050
    ERROR_COULD_NOT_CANCEL = -31007
    ERROR_COULD_NOT_PERFORM = -31008
    ERROR_INVALID_ORDER_AMOUNT = -31099

    request_id = None
    error = {}
    data = None
    messages = None
    exception_msg = None
    code = None

    def __init__(self, request_id, message, code, data=None):
        self.request_id = request_id
        self.messages = message
        self.code = code
        self.data = data
        self.error = {"code": self.code}
        if self.messages:
            self.error["message"] = self.messages
            self.exception_msg = f"Error: {self.error['message']}"
        if self.data:
            self.error["data"] = self.data
            self.exception_msg = (
                f"Error: {self.error['message']}, in {self.error['data']}"
            )

        Exception.__init__(self, self.exception_msg)

    @staticmethod
    def message(ru, en: str = "", uz: str = ""):
        return {"ru": ru, "en": en, "uz": uz}
