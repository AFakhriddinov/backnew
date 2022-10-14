from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.models import Group
from billing.models import AgentBalance
from django.urls import reverse
from django import forms
from django.contrib.auth.models import User, UserManager
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
  
def upload_path(instance, filename):
    return '/'.join(['images', str(instance.tour_title), filename])

ARTICLE_STATUSES = ((1, "New"), (2, "Active"), (3, "Deleted"))

class Article(models.Model):
    tour_title = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    image = models.ImageField(blank=True, null=True, upload_to=upload_path)
    image2 = models.ImageField(blank=True, null=True, upload_to=upload_path)
    image3 = models.ImageField(blank=True, null=True, upload_to=upload_path)

    price = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Price for under 3")
    price_under_18 = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Price for under 18")
    price_over_18 = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Price for over 18")

    quantity = models.DecimalField(max_digits=20, decimal_places=0, default='1', verbose_name="Quantity for under 3")
    quantity2 = models.DecimalField(max_digits=20, decimal_places=0, default='1', verbose_name="Quantity for under 18")
    quantity3 = models.DecimalField(max_digits=20, decimal_places=0, default='1', verbose_name="Quantity for over 18")

    duration = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)

    
    flight = models.BooleanField("Flight included", default=False)
    hotel = models.BooleanField("Hotel included", default=False)
    guide = models.BooleanField("Guide included", default=False)
    insurance = models.BooleanField("Insurance included", default=False)

    company = models.CharField(max_length=100, default='0000000')
    
    startDate = models.DateField(auto_now_add=False, auto_now=False )
    endDate = models.DateField(auto_now_add=False, auto_now=False )

    status = models.IntegerField(choices=ARTICLE_STATUSES, default=1)

    def __str__(self):
        return self.tour_title
    

USER_STATUSES = ((1, "New"), (2, "Active"), (3, "Deleted"))


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, is_superuser=False):
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(
            username=self.normalize_email(username),
        )
        user.set_password(password)
        user.is_superuser = is_superuser
        user.save()
        return user

    def create_staffuser(self, username, password):
        if not password:
            raise ValueError("staff/admins must have a password.")
        user = self.create_user(username, password=password)
        user.is_staff = True
        user.save()
        return user

    def create_superuser(self, username, password):
        if not password:
            raise ValueError("superusers must have a password.")
        user = self.create_user(username, password=password, is_superuser=True)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Ismi"
    )
    sur_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Familiyasi"
    )
    mid_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Otasining ismi"
    )
    username = models.CharField(
        max_length=255, db_index=True, unique=True, verbose_name="username"
    )
    email = models.EmailField(
        verbose_name="Elektron pochta manzili*", max_length=255, null=True
    )
    phone = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Phone number"
    )
    per_adr = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address"
    )
    company = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Company"
    )

    groups = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        default=1,
        blank=True,
        null=True,
    )
    status = models.IntegerField(choices=USER_STATUSES, default=1)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    activated_date = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []  # email and password required by default

    objects = UserManager()

    def __str__(self):
        return f"{self.username}"

    def __int__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("accounts:accounts_update", kwargs={"pk": self.pk})

@receiver(post_save, sender=User)
def make_balance(sender, instance, **kwargs):
    if not AgentBalance.objects.filter(user=instance.id).exists() and instance.groups.name == 'agent':
        balance = AgentBalance(
            user=instance,
        )
        balance.save()

class Order(models.Model):
    tour = models.ForeignKey(Article, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)