from django.contrib import admin
from .models import AgentBalance, Transaction

admin.site.register(AgentBalance)
admin.site.register(Transaction)
