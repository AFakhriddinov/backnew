import json
from .utils.exception import PaycomException
from .utils.format import BaseFormat


class PaycomRequest:
    id = None
    method = None
    payload = None
    amount = None
    params = None

    def __init__(self, request):
        try:
            payload = request.body.decode("utf-8")
            self.payload = json.loads(payload)
            # self.payload = request.data
            if self.payload is None:
                PaycomException(
                    None,
                    message="ERROR INVALID JSON RPC OBJECT",
                    code=PaycomException.ERROR_INVALID_JSON_RPC_OBJECT,
                )
        except TypeError or ValueError:
            PaycomException(
                None,
                message="ERROR INVALID JSON RPC OBJECT",
                code=PaycomException.ERROR_INVALID_JSON_RPC_OBJECT,
            )
        self.id = self.payload["id"] if "id" in self.payload else None
        self.method = self.payload["method"] if "method" in self.payload else None
        self.params = self.payload["params"] if "params" in self.payload else []
        self.amount = (
            self.payload["params"]["amount"]
            if "amount" in self.payload["params"]
            and not BaseFormat.is_not_numeric(self.payload["params"]["amount"])
            else None
        )


class PaycomResponse:
    request = None

    def __init__(self, request):
        self.request = request

    def send(self, result=None, error=None):
        data = {"result": result, "error": error, "id": self.request.id}
        return self.get_json(data)

    def error(self, code, message, data=None):
        data = {
            "error": {
                "code": code,
                "message": {"ru": message, "uz": message, "en": message},
                "data": data,
            },
            "result": None,
            "id": self.request.id,
        }

        return self.get_json(data)

    @staticmethod
    def get_json(data):
        return json.dumps(data)
