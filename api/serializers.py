from unittest.util import _MAX_LENGTH
from rest_framework import serializers
from .models import *


class ArticleSerializer(serializers.ModelSerializer):
       class Meta:
        model = Article
        fields = [
           "id",
            "tour_title",
            "image",
            "country",
            "price",
            "price_under_18",
            "price_over_18",
            "quantity",
            "quantity2",
            "quantity3",
            "duration",
            "description",
            "author",
            "image2",
            "image3",
            "flight",
            "hotel",
            "guide",
            "insurance",
            "company",
            "startDate",
            "endDate",
            "status",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = "UserSerializer"
        model = User
        fields = [
            "id",
            "first_name",
            "sur_name",
            "mid_name",
            "username",
            "email",
            "phone",
            # "passport",
            "per_adr",
            "company",
            "password",
            # "password2"
        ]

        extra_kwargs = {'password': {
            'write_only': True,
            'required': True
        }}

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "tour",
            "date",
        ]

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "user",
            "order",
        ]