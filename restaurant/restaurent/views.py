from django.shortcuts import render
from .models import *
from .permissions import CartPermissions
from .serializers import CartSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
# Create your views here.

class CartView(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [CartPermissions]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
