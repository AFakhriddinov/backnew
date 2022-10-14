from decimal import Decimal
from pyexpat import model
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from statistics import mode
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        # ordering = ['-created_at', '-updated_at']

    @staticmethod
    def url(field):
        return f"{field.file.url}" if field.file else None


class AgentBalance(TimestampedModel):
    user = models.ForeignKey("api.User", on_delete=models.PROTECT)
    balance = models.BigIntegerField(default=0)


class Transaction(TimestampedModel):
    credit = models.ForeignKey(AgentBalance, on_delete=models.CASCADE)
    debit = models.ForeignKey("api.User", on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    time_datetime = models.DateTimeField(null=True, blank=True)
    time_millisecond = models.CharField(
        max_length=255, blank=True, verbose_name="API kelgan vaqt (format:millisecond)"
    )
    perform_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Tasdiqlangan vaqti:"
    )
    create_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Yaratilgan vaqti:"
    )
    cancel_time = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(
        max_length=300, verbose_name="Tranzaksiya sababi (izoh)", blank=True, null=True
    ) 
    error = models.TextField(default="Aniqlanmadi!", blank=True, null=True)
    TRANSACTION_STATUS = (
        (0, ("Не существует")),
        (1, ("Создан")),
        (2, ("Оплачен")),
        (-1, ("Отменен")),
        (-2, ("Отменена после завершения")),
    )
    state = models.IntegerField(default=1, choices=TRANSACTION_STATUS)

@receiver(post_save, sender=Transaction)
def perform_transaction(sender, instance, **kwargs):
    if instance.state == 2:
        if instance.credit == instance.debit:
            raise Exception("Receiver and sender can't be the same!")
        agent = instance.credit
        agent.balance = agent.balance + instance.amount 
        agent.save()
