from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from user_auth.serializers import UserSerializer 
from .permissions import CanManageStaff
from restaurent.models import Category, MenuItem, Order
from restaurent.serializers import CategorySerializer, MenuItemSerializer, OrderSerializer
import logging
# Create your views here.

logger = logging.getLogger(__name__)

class DeliveryCrewView(ModelViewSet):
    queryset = get_user_model().objects.filter(groups__name__iexact='delivery crew')
    serializer_class = UserSerializer
    permission_classes = [CanManageStaff]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user_model = get_user_model()
        email = self.request.data.get('email')

        if email and user_model.objects.filter(email=email).exists():
            user = user_model.objects.get(email=email)
            Group.objects.get(name__iexact='delivery crew').user_set.add(user)
            #user.userprofile.role = 2
            user.save()
            logger.info('user with pk %d was added as a delivery crew by user with pk %d', user.pk, self.request.user.pk)
            return Response({'success':f'user {user.email} was added as a delivery crew'}, status=status.HTTP_201_CREATED)

        return Response({'error':'user with provided credintials not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name__iexact='delivery crew')

        group.user_set.remove(user)
        logger.info('user with pk %d was removed from delivery crew by user with pk %d', user.pk, self.request.user.pk)
        return Response({'success':f'user {user.email} was removed from delivey crew'}, status=status.HTTP_200_OK)


class CategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CanManageStaff]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MenuItemView(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [CanManageStaff]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serialized_data = self.serializer_class(data=self.request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            logger.info('menu item with name %s was created by user with pk %d', serialized_data.validated_data.get('name'))
            return Response(serialized_data.data, status=status.HTTP_201_CREATED)
        return Response({"error":serialized_data.errors.values()}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DeliveryCrewToOrder(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CanManageStaff]

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_model = get_user_model()
        if user_model.objects.filter(email=self.request.data.get('delivery_crew')).exists():
            user = user_model.objects.get(email=self.request.data.get('delivery_crew'))
            if user.userprofile.role == 2:
                obj = self.get_object()
                obj.delivery_crew = user
                obj.save()
                logger.info('user with pk %d was put in delivery for order with pk %d by user with pk %d',user.pk, self.get_object().pk, request.user.pk)
                return Response(self.serializer_class(obj).data, status=status.HTTP_200_OK)
            return Response({'error':'user is not a delivery_crew'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':'user not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.delivery_crew.email == self.request.data.get('delivery_crew'):
            obj.delivery_crew = None
            obj.save()
            logger.info('user with pk %s was removed from delivery for order with pk %d by user with pk %d', self.request.data.get('delivery_crew'), self.get_object().pk, request.user.pk)
            return Response(self.serializer_class(obj).data, status=status.HTTP_200_OK)
        return Response({'error':'user is not a assigned this order'}, status=status.HTTP_400_BAD_REQUEST)