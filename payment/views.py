import json
from decimal import Decimal

import requests
from django.shortcuts import render, redirect

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django_filters.views import FilterView

# from .filters import BalanceTransactionFilter
# from .invoice.paycom.api import InvoiceAPI
# from .models import BalanceTransaction, AccountBalance, WithdrawBalance
from .utils.paycom.api import PaycomAPI
from django.views import View
from django.http import JsonResponse

# from .utils.authorize import MERCHANT
# from ..auction.filters import WithDrawRequestFilter


@method_decorator(csrf_exempt, name="dispatch")
class PaycomView(View):
    """http://127.0.0.1:8000/paycom/api"""

    def post(self, request):
        app = PaycomAPI(request=request)
        response = app.run()
        new_data = json.loads(response)
        return JsonResponse(data=new_data, safe=False)
        # return JsonResponse(data={"success": True}, safe=False)

    def get(self, request):
        return JsonResponse(
            data={"message": " Bu url faqat post request qabul qiladi "}
        )
