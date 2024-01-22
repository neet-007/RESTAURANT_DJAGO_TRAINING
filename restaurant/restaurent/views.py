from .models import *
from .permissions import CartPermissions
from .serializers import CartSerializer, OrderSerializer, TableSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
# Create your views here.

class CartView(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [CartPermissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['method'] = self.request.method
        return context

class OrderView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CartPermissions]

    @action(methods=['get'], detail=False, name='orders for delivery crew')
    def delivery(self, request, pk=None):
        if not request.user.userprofile.role == 3:
            return Response(self.serializer_class(self.get_queryset().filter(delivery_crew=request.user), many=True).data, status=status.HTTP_200_OK)
        return Response({'error':'you are not authrized for this'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_queryset(self):
        if not self.request.user.is_superuser or not self.request.user.groups.filter(name__iexact='manager').exists():
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['method'] = self.request.method
        return context

class TableView(ModelViewSet):
    queryset = Tabel.objects.all()
    serializer_class = TableSerializer
    permission_classes = [CartPermissions]

    def get_queryset(self):
        if self.request.method == 'GET':
            if not self.request.user.groups.filter(name__iexact='manager') or self.request.user.is_admin:
                return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['method'] = self.request.method
        return context