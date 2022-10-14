from .utils.exception import PaycomException
from .utils.format import BaseFormat

from billing.models import AgentBalance
from api.models import Article, User


class AgentBalanceController:
    STATE_AVAILABLE = 0
    STATE_WAITING_PAY = 1
    STATE_PAY_ACCEPTED = 2
    STATE_CANCELLED = 3
    STATE_DELIVERED = 4

    response_message = None

    def __init__(self, request_id):
        self.request_id = request_id

    def validate(self, account_params):
        account = account_params["account"]
        id = "tour_id"
        user_id = "user_id"
        amount_str = "amount"

        if id not in account or account[id] == "":
            self.response_message = {
                "code": PaycomException.ERROR_INVALID_ACCOUNT,
                "message": {
                    "ru": "Provide tour id.",
                    "uz": "Tour id kiriting.",
                    "en": "Provide tour id.",
                },
                "data": id,
            }
            return False
        elif (
            amount_str not in account_params
            or account_params[amount_str] == ""
            or BaseFormat.is_not_numeric(value=account_params[amount_str])
        ):
            self.response_message = {
                "code": PaycomException.ERROR_INVALID_AMOUNT,
                "message": {
                    "ru": "Сумма не существует.",
                    "uz": "Narxi mavjud emas.",
                    "en": "Amount does not exist.",
                },
                "data": amount_str,
            }
            return False
        elif user_id not in account or account[user_id] == "":
            self.response_message = {
                "code": PaycomException.ERROR_INVALID_AMOUNT,
                "message": {
                    "ru": "Provide user id.",
                    "uz": "User id kiriting.",
                    "en": "Provide user id.",
                },
                "data": user_id,
            }
            return False
        else:
            try:
                tour = Article.objects.get(id=account[id])
                user = User.objects.get(id=account[user_id])
                data = {
                    "Tour nomi": str(tour.tour_title),
                    "Tour bir kishi uchun narhi": str(tour.price),
                    "Foydalanuvchi": f"{user.first_name} {user.sur_name}",
                    "To'lov turi": "Hisob to'ldirish uchun",
                    "Telefon": str(user.phone),
                }
                if user.status == 3:
                    self.response_message = {
                        "code": PaycomException.ERROR_INVALID_ACCOUNT,
                        "message": {
                            "ru": "Пользователь отключен или неактивен",
                            "uz": "Foydalanuvchi o'chirilgan yoki faol emas",
                            "en": "User is disabled or inactive",
                        },
                        "data": id,
                    }
                    return False
                else:
                    self.response_message = {"allow": True, "additional": data}
                    return True
            except Exception as err:
                if err == Article.DoesNotExist: 
                    self.response_message = {
                        "code": PaycomException.ERROR_INVALID_ACCOUNT,
                        "message": {
                            "ru": "Контракт не найден",
                            "uz": "Shartnoma topilmadi",
                            "en": "Contract not found",
                        },
                        "data": id,
                    }
                    return False
                if err == User.DoesNotExist:
                    self.response_message = {
                        "code": PaycomException.ERROR_INVALID_ACCOUNT,
                        "message": {
                            "ru": "Контракт не найден",
                            "uz": "Shartnoma topilmadi",
                            "en": "Contract not found",
                        },
                        "data": id,
                    }
                    return False
                print('$$$$$$$$$$$$$$$$$$')
                print(err)
                print('$$$$$$$$$$$$$$$$$$')