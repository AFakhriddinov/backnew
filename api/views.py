from http.client import HTTPResponse
from re import A
from urllib import response
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, filters, generics, permissions
from rest_framework import viewsets
from django.shortcuts import render, redirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import Token
from rest_framework.decorators import action
# from rest_framework.views import APIView
# from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import Group
from django.http import HttpResponse
# # from .models import Post
# from .serializers import PostSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by("price")
    serializer_class = ArticleSerializer


    # def post(self, request, *args, **kwargs):
    #     image = request.data['image']   
    #     tour_title = request.data['tour_title']
    #     Article.object.create(tour_title=tour_title, image=image)
    #     return HttpResponse({'message': 'Image added'}, status=200)
    
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        token = request.headers.get('Authorization').split(" ")[1]

        user = Token.objects.get(key=token).user
        if not user.status == 2:
            return Response({"error": "user must be activated"})
        data["author"] = user
        serializer = ArticleSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"payload": serializer.data})
       
       
        # print(request.headers.get('Authorization'), "request.user")
        # return Response({"success": True})

    @action(detail=False)
    def get_articles_by_user(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        user = Token.objects.get(key=token).user
        articles = self.get_queryset().filter(author=user)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    # authentication_classes = (TokenAuthentication,)

    def create(self, request, *args, **kwargs):
        validated_data = request.data
        if validated_data["groups"]:
            validated_data["groups"] = Group.objects.get(name=validated_data["groups"])
            
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"success": True, "token": token.key})

    @action(detail=False)
    def get_user_group(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        user = Token.objects.get(key=token).user
        user_group = user.groups.name
        return Response({"user_group": user_group})

    @action(detail=False)
    def get_by_token(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(" ")[1]
        user = Token.objects.get(key=token).user
        serializer = UserSerializer(user)
        return Response({"data":serializer.data})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer